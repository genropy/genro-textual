# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""CLI for running TextualApp applications.

Usage:
    pygui run examples/basic/hello_world.py
    pygui run examples/basic/hello_world.py -c   # run and connect
    pygui run examples/basic/hello_world.py -r   # run with autoreload
    pygui list
    pygui connect hello_world
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys

from genro_textual.registry import (
    find_free_port,
    get_app_info,
    list_apps,
    register_app,
    unregister_app,
)


def _run_with_tmux(file_path: str, app_name: str) -> None:
    """Run app in tmux: TUI on top pane, REPL on bottom pane."""
    if shutil.which("tmux") is None:
        print("Error: tmux not found. Install it or use two terminals:")
        print(f"  Terminal 1: pygui run {file_path}")
        print(f"  Terminal 2: pygui connect {app_name}")
        sys.exit(1)

    session = f"pygui-{app_name}"
    python = sys.executable
    file_abs = os.path.abspath(file_path)

    # Command for top pane: run the TUI app
    run_cmd = f"{python} -m genro_textual.cli run {file_abs}"
    # Command for bottom pane: wait for app to register, then connect
    connect_cmd = (
        f"sleep 1 && {python} -m genro_textual.cli connect {app_name}"
    )

    # Create tmux session with the TUI in the first pane
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session, "-x", "200", "-y", "50", run_cmd],
        check=True,
    )
    # Split horizontally: REPL on bottom (30% height)
    subprocess.run(
        ["tmux", "split-window", "-v", "-t", session, "-p", "30", connect_cmd],
        check=True,
    )
    # Focus on the REPL pane (bottom)
    subprocess.run(
        ["tmux", "select-pane", "-t", session + ":.1"],
        check=True,
    )
    # Attach to the session
    os.execvp("tmux", ["tmux", "attach-session", "-t", session])


def _run_with_reload(file_path: str) -> None:
    """Run app with autoreload using watchfiles."""
    try:
        from watchfiles import run_process
    except ImportError:
        print("Error: watchfiles not installed. Run: pip install watchfiles")
        sys.exit(1)

    def target():
        run_app(file_path, connect=False, reload=False)

    watch_dir = os.path.dirname(os.path.abspath(file_path)) or "."
    run_process(watch_dir, target=target)


def run_app(file_path: str, connect: bool = False, reload: bool = False) -> None:
    """Run a TextualApp from file path. Expects class Application."""
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        sys.exit(1)

    app_name = os.path.splitext(os.path.basename(file_path))[0]

    if reload:
        _run_with_reload(file_path)
        return

    if connect:
        _run_with_tmux(file_path, app_name)
        return

    # Carica il modulo dal file
    spec = importlib.util.spec_from_file_location(app_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Cerca classe Main
    app_class = getattr(module, "Application", None)
    if app_class is None:
        print(f"Error: {file_path} must have a class named 'Application'")
        sys.exit(1)

    port = find_free_port()

    # Create app first to get token from remote server
    app = app_class(remote_port=port)

    # Get token from remote server (created during app init)
    token = ""
    if app._remote_server is not None:
        token = app._remote_server.token

    register_app(app_name, port, token)
    print(f"Starting {app_name} on port {port}")

    try:
        app.run()
    finally:
        unregister_app(app_name)


def _is_alive(port: int) -> bool:
    """Check if something is listening on the given port."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.3)
    try:
        sock.connect(("localhost", port))
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def list_running() -> None:
    """List all registered apps, checking if they are alive."""
    apps = list_apps()
    if not apps:
        print("No apps registered")
        return
    dead = []
    for app_name, info in apps.items():
        port = info["port"] if isinstance(info, dict) else info
        alive = _is_alive(port)
        status = "alive" if alive else "dead"
        print(f"  {app_name}: port {port} [{status}]")
        if not alive:
            dead.append(app_name)
    if dead:
        for name in dead:
            unregister_app(name)
        print(f"  Cleaned up {len(dead)} dead app(s)")


def connect_repl(name: str) -> None:
    """Start a REPL connected to an app."""
    info = get_app_info(name)
    if info is None:
        print(f"App '{name}' not found")
        sys.exit(1)

    from genro_textual.remote import connect

    app = connect(name=name)
    port = info["port"]
    print(f"Connected to {name} on port {port}")
    print("Use 'app.page.static(\"text\")' to add widgets")
    print("Type 'exit()' to quit")

    import code

    code.interact(local={"app": app})


def stop_app(name: str) -> None:
    """Stop a running app and kill its tmux session if any."""
    info = get_app_info(name)
    if info is None:
        print(f"App '{name}' not found")
        sys.exit(1)

    # Try graceful shutdown via remote protocol
    from genro_textual.remote import connect

    try:
        app = connect(name=name)
        app._send(("__quit__",))
        print(f"Stopped {name}")
    except Exception:
        print(f"App {name} not responding, cleaning up")

    # Kill tmux session if it exists
    session = f"pygui-{name}"
    subprocess.run(
        ["tmux", "kill-session", "-t", session],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    unregister_app(name)
    print(f"Unregistered {name}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(prog="pygui", description="TextualApp CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a TextualApp")
    run_parser.add_argument("file", help="path/to/file.py (must have class Application)")
    run_parser.add_argument(
        "-c", "--connect", action="store_true", help="Run in background and connect REPL"
    )
    run_parser.add_argument(
        "-r", "--reload", action="store_true", help="Run with autoreload on file changes"
    )

    # list command
    subparsers.add_parser("list", help="List running apps")

    # connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to an app")
    connect_parser.add_argument("name", help="App name")

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a running app")
    stop_parser.add_argument("name", help="App name")

    args = parser.parse_args()

    if args.command == "run":
        run_app(args.file, connect=args.connect, reload=args.reload)
    elif args.command == "list":
        list_running()
    elif args.command == "connect":
        connect_repl(args.name)
    elif args.command == "stop":
        stop_app(args.name)


if __name__ == "__main__":
    main()
