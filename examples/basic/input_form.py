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

    def recipe(self, root):
        root.static("User Registration")
        root.input(placeholder="First Name", id="first_name")
        root.input(placeholder="Last Name", id="last_name")
        root.input(placeholder="Email", id="email")
        root.static("Press Tab to move between fields, q to quit")

    def on_input_submitted(self, event: Input.Submitted):
        self.notify(f"Submitted: {event.input.id} = {event.value}")
