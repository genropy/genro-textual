# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""App registry for name-based connection.

Stores mapping of app names to ports and tokens in a JSON file.
Uses atomic writes and file locking for safety.
"""

from __future__ import annotations

import fcntl
import json
import os
import socket
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

# Registry file in user's temp directory with restricted permissions
REGISTRY_DIR = Path(tempfile.gettempdir()) / f"genro_textual_{os.getuid()}"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"


def _ensure_registry_dir() -> None:
    """Ensure registry directory exists with proper permissions."""
    if not REGISTRY_DIR.exists():
        REGISTRY_DIR.mkdir(mode=0o700, exist_ok=True)


@contextmanager
def _locked_registry(write: bool = False):
    """Context manager for locked access to registry file."""
    _ensure_registry_dir()
    lock_file = REGISTRY_DIR / ".lock"
    lock_file.touch(mode=0o600, exist_ok=True)

    with open(lock_file) as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX if write else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def find_free_port() -> int:
    """Find a free port on localhost."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def register_app(name: str, port: int, token: str = "") -> None:
    """Register an app name with its port and token."""
    with _locked_registry(write=True):
        registry = _load_registry_unlocked()
        registry[name] = {"port": port, "token": token}
        _save_registry_unlocked(registry)


def unregister_app(name: str) -> None:
    """Remove an app from the registry."""
    with _locked_registry(write=True):
        registry = _load_registry_unlocked()
        registry.pop(name, None)
        _save_registry_unlocked(registry)


def get_port(name: str) -> int | None:
    """Get port for an app name."""
    info = get_app_info(name)
    return info["port"] if info else None


def get_app_info(name: str) -> dict[str, Any] | None:
    """Get full info (port, token) for an app name."""
    with _locked_registry():
        registry = _load_registry_unlocked()
        return registry.get(name)


def _load_registry_unlocked() -> dict[str, dict[str, Any]]:
    """Load registry from file (must hold lock)."""
    if not REGISTRY_FILE.exists():
        return {}
    try:
        data = json.loads(REGISTRY_FILE.read_text())
        # Handle old format (name -> port) vs new format (name -> {port, token})
        result = {}
        for name, info in data.items():
            if isinstance(info, int):
                result[name] = {"port": info, "token": ""}
            else:
                result[name] = info
        return result
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry_unlocked(registry: dict[str, dict[str, Any]]) -> None:
    """Save registry atomically (must hold lock)."""
    _ensure_registry_dir()
    # Write to temp file then rename (atomic on POSIX)
    temp_file = REGISTRY_DIR / ".registry.tmp"
    temp_file.write_text(json.dumps(registry, indent=2))
    os.chmod(temp_file, 0o600)
    temp_file.rename(REGISTRY_FILE)


def list_apps() -> dict[str, dict[str, Any]]:
    """List all registered apps."""
    with _locked_registry():
        return _load_registry_unlocked()
