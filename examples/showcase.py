# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Showcase: all examples in a TabbedContent.

Run with:
    textual run examples/showcase.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """All examples in tabs."""

    CSS = """
    .stripe-red { background: red; }
    .stripe-orange { background: orange; }
    .stripe-yellow { background: yellow; color: black; }
    .stripe-green { background: green; }
    .stripe-blue { background: blue; }
    .stripe-purple { background: purple; }
    """

    def recipe(self, root):
        tabs = root.tabbedcontent(id="examples")

        # Tab 1: Hello World
        tab1 = tabs.tabpane(title="Hello World", id="tab-hello")
        tab1.static("Hello, Textual!")
        tab1.static("Press 'q' to quit")

        # Tab 2: Colors
        tab2 = tabs.tabpane(title="Colors", id="tab-colors")
        for color in ["red", "orange", "yellow", "green", "blue", "purple"]:
            tab2.static(f"  {color.upper()}  ", classes=f"stripe-{color}")

        # Tab 3: Buttons
        tab3 = tabs.tabpane(title="Buttons", id="tab-buttons")
        tab3.static("Button Variants")
        tab3.button("Default", id="btn_default")
        tab3.button("Primary", id="btn_primary", variant="primary")
        tab3.button("Success", id="btn_success", variant="success")
        tab3.button("Warning", id="btn_warning", variant="warning")
        tab3.button("Error", id="btn_error", variant="error")

        # Tab 4: Form
        tab4 = tabs.tabpane(title="Form", id="tab-form")
        tab4.static("User Registration")
        tab4.input(placeholder="First Name", id="first_name")
        tab4.input(placeholder="Last Name", id="last_name")
        tab4.input(placeholder="Email", id="email")


