# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Data binding example with ^pointer, CSS, and bindings in main.

Demonstrates:
    - source.css() for application styling
    - source.binding() for key bindings
    - ^pointer for reactive data binding
    - Bidirectional binding (input → data → label)

Run with:
    python -m genro_textual.cli run examples/reactive/data_binding.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Reactive app with data binding."""

    def main(self, source):
        source.css("""
            .greeting { color: green; text-style: bold; margin: 1 0; }
            .info { color: $text-muted; margin: 0 0 1 0; }
        """)
        source.binding(key="q", action="quit", description="Quit")

        source.static("^greeting", classes="greeting")
        source.static("Type your name below:", classes="info")
        source.input(value="^form.name", placeholder="Your name")

    def store(self, data):
        data["greeting"] = "Hello, World!"
        data["form.name"] = ""
