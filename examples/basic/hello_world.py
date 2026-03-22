# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Minimal TextualApp example.

Run with:
    python -m genro_textual.cli run examples/basic/hello_world.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Minimal TextualApp showing basic usage."""

    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.static("Hello, Textual!")
        page.static("Press 'q' to quit")
