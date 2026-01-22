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
import subprocess
import sys
import time

from genro_textual.registry import (
    find_free_port,
    get_app_info,
    list_apps,
    register_app,
    unregister_app,
)


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
    app_name = os.path.basename(file_path).replace(".py", "")

    if reload:
        _run_with_reload(file_path)
        return

    if connect:
        # Lancia l'app in background e poi connetti
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        subprocess.Popen(
            [sys.executable, "-m", "genro_textual.cli", "run", file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        # Attendi che l'app si registri
        for _ in range(20):  # Increased retries
            time.sleep(0.2)
            if get_app_info(app_name) is not None:
                break
        connect_repl(app_name)
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


def list_running() -> None:
    """List all registered apps."""
    apps = list_apps()
    if not apps:
        print("No apps registered")
        return
    for app_name, info in apps.items():
        port = info["port"] if isinstance(info, dict) else info
        print(f"  {app_name}: port {port}")


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

    args = parser.parse_args()

    if args.command == "run":
        run_app(args.file, connect=args.connect, reload=args.reload)
    elif args.command == "list":
        list_running()
    elif args.command == "connect":
        connect_repl(args.name)


if __name__ == "__main__":
    main()
