# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Data binding example with ^pointer, CSS, and bindings in recipe.

Demonstrates:
    - page.css() for application styling
    - page.binding() for key bindings
    - ^pointer for reactive data binding
    - Bidirectional binding (input → data → label)

Run with:
    python -m genro_textual.cli run examples/reactive/data_binding.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Reactive app with data binding."""

    def recipe(self, page):
        page.css("""
            .greeting { color: green; text-style: bold; margin: 1 0; }
            .info { color: $text-muted; margin: 0 0 1 0; }
        """)
        page.binding(key="q", action="quit", description="Quit")

        page.static("^greeting", classes="greeting")
        page.static("Type your name below:", classes="info")
        page.input(value="^form.name", placeholder="Your name")

    def setup(self):
        self.data["greeting"] = "Hello, World!"
        self.data["form.name"] = ""
        super().setup()
