# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Remote control for TextualApp.

Server side (in TextualApp):
    app.enable_remote(port=9999)

Client side:
    from genro_textual.remote import connect
    app = connect()
    app.page.static("Hello!")

Protocol:
    - Each message is prefixed with 4 bytes (big-endian) indicating length
    - Messages are pickle-serialized Python objects
    - Client sends: (command, *args)
    - Server responds: (status, result) where status is "ok" or "error"
    - Token authentication required for all commands
"""

from __future__ import annotations

import pickle
import secrets
import socket
import struct
import threading
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from genro_textual.textual_app import TextualApp

# Frame format: 4-byte length prefix (big-endian)
FRAME_HEADER_SIZE = 4
FRAME_HEADER_FORMAT = ">I"  # unsigned int, big-endian
MAX_MESSAGE_SIZE = 16 * 1024 * 1024  # 16MB max


def _send_framed(sock: socket.socket, data: bytes) -> None:
    """Send data with length prefix."""
    if len(data) > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message too large: {len(data)} bytes")
    header = struct.pack(FRAME_HEADER_FORMAT, len(data))
    sock.sendall(header + data)


def _recv_framed(sock: socket.socket) -> bytes | None:
    """Receive length-prefixed data."""
    header = _recv_exact(sock, FRAME_HEADER_SIZE)
    if header is None:
        return None
    length = struct.unpack(FRAME_HEADER_FORMAT, header)[0]
    if length > MAX_MESSAGE_SIZE:
        raise ValueError(f"Message too large: {length} bytes")
    return _recv_exact(sock, length)


def _recv_exact(sock: socket.socket, n: int) -> bytes | None:
    """Receive exactly n bytes."""
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data.extend(chunk)
    return bytes(data)


class RemoteProxy:
    """Proxy that sends method calls to remote TextualApp."""

    def __init__(self, host: str = "localhost", port: int = 9999, token: str = "") -> None:
        self._host = host
        self._port = port
        self._token = token

    def _send(self, cmd: tuple) -> Any:
        """Send command and receive result."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self._host, self._port))
            # Send auth token + command
            message = (self._token, cmd)
            _send_framed(sock, pickle.dumps(message))
            # Receive response
            response_data = _recv_framed(sock)
            if response_data is None:
                raise ConnectionError("Connection closed by server")
            status, result = pickle.loads(response_data)  # noqa: S301
            if status == "error":
                raise RuntimeError(f"Remote error: {result}")
            return result
        finally:
            sock.close()

    @property
    def page(self) -> PageProxy:
        """Return proxy for page Bag."""
        return PageProxy(self)


class PageProxy:
    """Proxy for page Bag - forwards all method calls."""

    def __init__(self, remote: RemoteProxy) -> None:
        self._remote = remote

    def __getattr__(self, name: str) -> Any:
        """Forward method calls to remote page."""

        def method(*args: Any, **kwargs: Any) -> Any:
            return self._remote._send(("__call__", name, args, kwargs))

        return method

    def keys(self) -> list[str]:
        """Get keys from remote Bag."""
        return self._remote._send(("__keys__",))

    def __getitem__(self, key: str) -> Any:
        """Get item from remote Bag."""
        return self._remote._send(("__getitem__", key))

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item on remote Bag."""
        self._remote._send(("__setitem__", key, value))


def connect(
    name: str | None = None, host: str = "localhost", port: int | None = None, token: str = ""
) -> RemoteProxy:
    """Connect to a remote TextualApp by name or port."""
    if name is not None:
        from genro_textual.registry import get_app_info

        info = get_app_info(name)
        if info is None:
            raise ValueError(f"App '{name}' not found in registry")
        port = info["port"]
        token = info.get("token", "")
    elif port is None:
        port = 9999
    return RemoteProxy(host, port, token)


class RemoteServer:
    """Server that receives commands for TextualApp."""

    def __init__(self, app: TextualApp, port: int = 9999) -> None:
        self._app = app
        self._port = port
        self._thread: threading.Thread | None = None
        self._running = False
        self._token = secrets.token_hex(16)

    @property
    def token(self) -> str:
        """Authentication token for this server."""
        return self._token

    def start(self) -> None:
        """Start the server in a background thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server."""
        self._running = False

    def _run(self) -> None:
        """Run the socket server."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", self._port))
        server.listen(50)  # Increased backlog
        server.settimeout(1.0)

        while self._running:
            try:
                conn, _ = server.accept()
                self._handle_connection(conn)
            except socket.timeout:
                continue
            except Exception:
                break

        server.close()

    def _handle_connection(self, conn: socket.socket) -> None:
        """Handle a single connection."""
        try:
            data = _recv_framed(conn)
            if data is None:
                return
            token, cmd = pickle.loads(data)  # noqa: S301
            # Verify token
            if token != self._token:
                response = ("error", "Invalid authentication token")
            else:
                result = self._handle_command(cmd)
                response = ("ok", result)
            _send_framed(conn, pickle.dumps(response))
        except Exception as e:
            try:
                _send_framed(conn, pickle.dumps(("error", str(e))))
            except Exception:
                pass
        finally:
            conn.close()

    def _handle_command(self, cmd: tuple) -> Any:
        """Handle incoming command."""
        cmd_type = cmd[0]

        if cmd_type == "__keys__":
            return list(self._app.page.keys())

        if cmd_type == "__getitem__":
            key = cmd[1]
            return self._app.page[key]

        if cmd_type == "__setitem__":
            key, value = cmd[1], cmd[2]
            return self._safe_call(lambda: setattr_item(self._app.page, key, value))

        if cmd_type == "__call__":
            method_name, args, kwargs = cmd[1], cmd[2], cmd[3]
            return self._safe_call(
                lambda: getattr(self._app.page, method_name)(*args, **kwargs)
            )

        raise ValueError(f"Unknown command: {cmd_type}")

    def _safe_call(self, func: Callable[[], Any]) -> Any:
        """Execute function in Textual's main thread and return result."""
        textual_app = self._app._live_app
        if textual_app is None:
            return func()
        return textual_app.call_from_thread(func)


def setattr_item(obj: Any, key: str, value: Any) -> None:
    """Helper to set item on object (for lambda)."""
    obj[key] = value
