# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Simple input form example.

Run with:
    textual run examples/basic/input_form.py

Shows Input widgets with placeholders.
"""

from textual.widgets import Input

from genro_textual import TextualApp


class Application(TextualApp):
    """Simple form with input fields."""

    def main(self, source):
        source.static("User Registration")
        source.input(placeholder="First Name", id="first_name")
        source.input(placeholder="Last Name", id="last_name")
        source.input(placeholder="Email", id="email")
        source.static("Press Tab to move between fields, q to quit")

    def on_input_submitted(self, event: Input.Submitted):
        self._live_app.notify(f"Submitted: {event.input.id} = {event.value}")
