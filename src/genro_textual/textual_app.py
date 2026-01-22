# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualApp - Base class for Textual apps built with Bag.

Workflow:
    1. App instantiated → creates _page (recipe Bag) and _data (data Bag)
    2. recipe(root) → populates the recipe Bag (the "human-readable recipe")
    3. run() → compiles the recipe and starts Textual
    4. Textual calls App.compose() → yields the pre-compiled widgets

IMPORTANT: recipe() is called ONCE at instantiation to create the recipe.
compile() transforms the recipe into Textual widgets ONCE.
Textual's compose() just yields the cached widgets.

Example:
    from genro_textual import TextualApp

    class MyApp(TextualApp):
        def recipe(self, root):
            root.static("Hello, Textual!")
            tabs = root.tabbedcontent()
            tab1 = tabs.tabpane("Tab 1")
            tab1.button("Click me")

    if __name__ == "__main__":
        MyApp().run()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from genro_bag import Bag
from textual.app import App
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Button

from genro_textual.textual_builder import TextualBuilder

if TYPE_CHECKING:
    from genro_textual.remote import RemoteServer


class TextualWrapperApp(App):
    """Internal Textual App that wraps TextualApp."""

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, owner: "TextualApp") -> None:
        super().__init__()
        self.owner = owner
        self.root = None

    def compose(self):
        self.root = Vertical(id="root")
        return [self.root]

    def on_mount(self) -> None:
        self.owner._page.builder.compile(self.owner._page, self.root)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def on_key(self, event: any) -> None:
        pass


class TextualApp:
    """Base class for Textual apps built with Bag.

    Subclass and override recipe(root) to define your UI.
    The root is a Bag with TextualBuilder - use it to add widgets.
    """

    def __init__(self, remote_port: int | None = None) -> None:
        self._page = Bag(builder=TextualBuilder)
        self._data = Bag()
        self._remote_server: RemoteServer | None = None
        self._remote_port = remote_port
        self._compiled_widgets: list[Widget] = []
        self._textual_app: App | None = None
        self.recipe(self._page)

    @property
    def page(self) -> Bag:
        """The page Bag (UI structure)."""
        return self._page

    @property
    def data(self) -> Bag:
        """The data Bag (application data)."""
        return self._data

    def recipe(self, root: Bag) -> None:
        """Override this method to build your UI.

        Args:
            root: The page Bag. Add widgets by calling methods on it.
        """


    def run(self) -> None:
        """Run the Textual app."""
        self._textual_app = TextualWrapperApp(self)
        self._textual_app.run()

    def _enable_remote(self, port: int) -> None:
        """Enable remote control via socket."""
        from genro_textual.remote import RemoteServer

        self._remote_server = RemoteServer(self, port)
        self._remote_server.start()
