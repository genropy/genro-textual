# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""App controllable via remote connection.

Run with:
    textual run examples/interactive/remote_app.py

Use the remote REPL to add widgets dynamically.
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """TextualApp controllable via remote connection."""

    def recipe(self, root):
        root.static("Remote TextualApp")
        root.static("Use remote REPL to add widgets")
        root.static("Press 'q' to quit")
