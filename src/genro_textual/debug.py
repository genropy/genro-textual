# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Debug logger for genro-textual. Writes to /tmp/genro_textual.log."""

import threading
import time

_LOG_FILE = "/tmp/genro_textual.log"
_start = time.monotonic()


def log(msg: str) -> None:
    """Log a message with timestamp and thread info."""
    elapsed = time.monotonic() - _start
    thread = threading.current_thread().name
    tid = threading.get_ident()
    with open(_LOG_FILE, "a") as f:
        f.write(f"[{elapsed:8.3f}s] [{thread}:{tid}] {msg}\n")


def clear() -> None:
    """Clear the log file."""
    with open(_LOG_FILE, "w") as f:
        f.write("")
