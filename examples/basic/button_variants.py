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

    def main(self, source):
        source.static("Button Variants")
        source.button("Default", id="btn_default")
        source.button("Primary", id="btn_primary", variant="primary")
        source.button("Success", id="btn_success", variant="success")
        source.button("Warning", id="btn_warning", variant="warning")
        source.button("Error", id="btn_error", variant="error")
        source.static("")
        source.static("Click a button or press 'q' to quit")

    def on_button_pressed(self, event: Button.Pressed):
        self._live_app.notify(f"Pressed: {event.button.label}")
