# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""POC: Resizable drawer with Bag inspector (data, source, compiled).

Run with:
    python examples/poc_drawer.py
"""

from genro_textual import TextualApp


DRAWER_WIDTH_DEFAULT = 40
DRAWER_WIDTH_MIN = 20
DRAWER_WIDTH_MAX = 80
DRAWER_WIDTH_STEP = 5


class Application(TextualApp):
    """App with Bag-driven drawer and 3-tab inspector."""

    def recipe(self, page):
        page.css("""
            #main-area { height: 1fr; }
            #main-content { width: 1fr; padding: 1 2; }
            #drawer {
                background: $surface;
                border-left: solid $primary;
            }
            #drawer-topbar {
                height: 1;
                background: $primary-darken-2;
            }
            #drawer-title {
                width: 1fr;
                padding: 0 1;
                color: $text;
            }
            .drawer-btn {
                min-width: 3;
                height: 1;
                border: none;
                padding: 0;
                background: transparent;
                color: $text-muted;
            }
            .drawer-btn:hover {
                color: $text;
                background: transparent;
            }
        """)
        page.binding(key="q", action="quit", description="Quit")
        page.binding(key="f12", action="toggle_drawer", description="Inspector")

        page.header()

        main = page.horizontal(id="main-area")

        # --- Main content ---
        content = main.verticalscroll(id="main-content")
        content.static("Main Application Content")
        content.static("")
        content.static("^greeting")
        content.input(value="^form.name", placeholder="Name")
        content.input(value="^form.surname", placeholder="Surname")
        content.static("")
        for i in range(1, 10):
            content.static(f"  Content line {i}")

        # --- Drawer ---
        drawer = main.vertical(
            id="drawer",
            width="^_system.drawer.width",
            display="^_system.drawer.display",
        )
        topbar = drawer.horizontal(id="drawer-topbar")
        topbar.static("Inspector", id="drawer-title")
        topbar.button("\u25c0", id="btn-expand", classes="drawer-btn")
        topbar.button("\u25b6", id="btn-shrink", classes="drawer-btn")

        # --- 3 tabs: Data, Source, Compiled ---
        tabs = drawer.tabbedcontent(initial="tab-data")

        data_tab = tabs.tabpane(title="Data", id="tab-data")
        data_tab.tree(label="data", store=self.data)

        source_tab = tabs.tabpane(title="Source", id="tab-source")
        source_tab.tree(label="source", store=self.source)

        compiled_tab = tabs.tabpane(title="Compiled", id="tab-compiled")
        compiled_tab.tree(label="compiled", store=self.compiled)

        page.footer(show_command_palette=False)

    def setup(self):
        self.data["_system.drawer.width"] = DRAWER_WIDTH_DEFAULT
        self.data["_system.drawer.display"] = "block"
        self.data["greeting"] = "Hello!"
        self.data["form.name"] = "John"
        self.data["form.surname"] = "Doe"
        super().setup()

    def on_key(self, event):
        """Handle F12 for drawer toggle — writes to data Bag."""
        if event.key == "f12":
            current = self.data["_system.drawer.display"]
            self.data["_system.drawer.display"] = "none" if current == "block" else "block"

    def on_button_pressed(self, event):
        """Handle drawer resize buttons — write to data Bag."""
        current = self.data["_system.drawer.width"] or DRAWER_WIDTH_DEFAULT
        if event.button.id == "btn-shrink":
            new_width = max(DRAWER_WIDTH_MIN, current - DRAWER_WIDTH_STEP)
        elif event.button.id == "btn-expand":
            new_width = min(DRAWER_WIDTH_MAX, current + DRAWER_WIDTH_STEP)
        else:
            return
        if new_width != current:
            self.data["drawer.width"] = new_width


if __name__ == "__main__":
    Application().run()
