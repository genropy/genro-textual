# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TabbedContent example with TabPane containers.

Run with:
    textual run examples/widgets/tabs.py

Shows how to create tabbed interfaces with TabbedContent and TabPane.
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """TabbedContent with multiple TabPane containers."""

    CSS = """
    .tab-title {
        text-style: bold;
        color: $primary;
        margin: 1 0;
    }
    """

    def recipe(self, root):
        tabs = root.tabbedcontent(id="main-tabs", initial="overview")

        # Tab 1: Overview
        overview = tabs.tabpane(title="Overview", id="overview")
        overview.static("Welcome to the TabbedContent Example", classes="tab-title")
        overview.static("This demonstrates how to use tabs in genro-textual.")
        overview.static("Use Tab/Shift-Tab or click to switch tabs.")

        # Tab 2: Features
        features = tabs.tabpane(title="Features", id="features")
        features.static("Available Features", classes="tab-title")
        features.static("- Declarative UI with Bag")
        features.static("- All Textual widgets supported")
        features.static("- Containers and layouts")
        features.static("- Event handling")

        # Tab 3: Settings
        settings = tabs.tabpane(title="Settings", id="settings")
        settings.static("Application Settings", classes="tab-title")
        settings.checkbox("Enable notifications", value=True, id="chk-notifications")
        settings.checkbox("Dark mode", value=True, id="chk-dark")
        settings.switch(value=False, id="sw-debug")
        settings.static("Debug mode")

        root.footer()
