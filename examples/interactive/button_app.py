# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Button that adds widgets dynamically.

Run with:
    textual run examples/interactive/button_app.py

Press the button to add a new Static widget.
"""

from textual.widgets import Button

from genro_textual import TextualApp


class Application(TextualApp):
    """App with button that adds widgets dynamically."""

    def recipe(self, root):
        root.static("Press the button to add widgets")
        root.static("Press 'q' to quit")
        root.button("Add Static", id="add_btn", variant="primary")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_btn":
            count = len(list(self.root.children))
            self.root.mount_from_bag(lambda b: b.static(f"Widget #{count}"))
