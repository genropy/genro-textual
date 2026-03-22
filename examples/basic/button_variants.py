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

    def recipe(self, page):
        page.static("Button Variants")
        page.button("Default", id="btn_default")
        page.button("Primary", id="btn_primary", variant="primary")
        page.button("Success", id="btn_success", variant="success")
        page.button("Warning", id="btn_warning", variant="warning")
        page.button("Error", id="btn_error", variant="error")
        page.static("")
        page.static("Click a button or press 'q' to quit")

    def on_button_pressed(self, event: Button.Pressed):
        self._live_app.notify(f"Pressed: {event.button.label}")
