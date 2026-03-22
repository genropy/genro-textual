# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Button that adds widgets dynamically.

Run with:
    textual run examples/interactive/button_app.py

Press the button to add a new Static widget.
"""

from textual.widgets import Button, Static

from genro_textual import TextualApp


class Application(TextualApp):
    """App with button that adds widgets dynamically."""

    def __init__(self):
        super().__init__()
        self._counter = 0

    def recipe(self, page):
        page.static("Press the button to add widgets")
        page.static("Press 'q' to quit")
        page.button("Add Static", id="add_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_btn":
            self._counter += 1
            widget = Static(f"Widget #{self._counter}")
            self._live_app.root.mount(widget)
