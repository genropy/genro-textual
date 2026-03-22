# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""App controllable via remote connection.

Run with:
    textual run examples/interactive/remote_app.py

Use the remote REPL to add widgets dynamically.
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """TextualApp controllable via remote connection."""

    def recipe(self, page):
        page.static("Remote TextualApp")
        page.static("Use remote REPL to add widgets")
        page.static("Press 'q' to quit")
