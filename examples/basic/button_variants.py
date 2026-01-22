# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Button variants example.

Run with:
    textual run examples/basic/button_variants.py

Shows all Button variants: default, primary, success, warning, error.
"""

from textual.widgets import Button

from genro_textual import TextualApp


class Application(TextualApp):
    """Display all button variants."""

    def recipe(self, root):
        root.static("Button Variants")
        root.button("Default", id="btn_default")
        root.button("Primary", id="btn_primary", variant="primary")
        root.button("Success", id="btn_success", variant="success")
        root.button("Warning", id="btn_warning", variant="warning")
        root.button("Error", id="btn_error", variant="error")
        root.static("")
        root.static("Click a button or press 'q' to quit")

    def on_button_pressed(self, event: Button.Pressed):
        self.notify(f"Pressed: {event.button.label}")
