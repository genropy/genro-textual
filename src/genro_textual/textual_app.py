# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualApp - Reactive Textual app driven by CompiledBag.

Architecture: puppeteer and puppet.

    TextualApp (BagAppBase) is the puppeteer — configures recipe, data,
    compiler. Creates and drives the LiveApp.

    LiveApp (textual.app.App) is the puppet — no logic of its own.
    Built and controlled by the puppeteer.

Everything goes through the Bag: CSS, bindings, widgets — all declared
in the recipe as nodes. The compiler extracts app config (css, binding)
and applies it to the LiveApp, then mounts widgets.

Lifecycle:
    1. TextualApp() → BagAppBase.__init__()
    2. run() → creates LiveApp, starts Textual event loop
    3. LiveApp.on_mount() → setup() = recipe + compile + bind + render
    4. Data changes → BindingManager updates node → widget update
    5. Widget changes → _on_widget_changed → data update (bidirectional)

Example:
    from genro_textual import TextualApp

    class MyApp(TextualApp):
        def recipe(self, page):
            page.css(".title { color: green; }")
            page.binding(key="q", action="quit", description="Quit")
            page.static("Hello!", classes="title")

    if __name__ == "__main__":
        MyApp().run()
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from genro_bag import Bag, BagNode
from genro_builders.app import BagAppBase
from genro_builders.builder_bag import BuilderBag
from textual.app import App
from textual.containers import Vertical
from textual.widgets import Button, Checkbox, Input, Static, Switch

from genro_textual.textual_builder import TextualBuilder
from genro_textual.textual_compiler import TextualCompiler

if TYPE_CHECKING:
    from genro_textual.remote import RemoteServer


class LiveApp(App):
    """The puppet: a bare textual.app.App driven by TextualApp.

    Has no CSS or BINDINGS of its own — those come from the recipe
    and are applied by the compiler at render time.
    Delegates all events to the owner (TextualApp).
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, owner: TextualApp) -> None:
        super().__init__()
        self.owner = owner
        self.root: Vertical | None = None

    def compose(self):
        self.root = Vertical(id="root")
        return [self.root]

    def on_mount(self) -> None:
        self.owner.setup()

    # --- Event delegation to owner ---

    def on_button_pressed(self, event: Button.Pressed) -> None:
        handler = getattr(self.owner, "on_button_pressed", None)
        if handler:
            handler(event)

    def on_key(self, event: Any) -> None:
        handler = getattr(self.owner, "on_key", None)
        if handler:
            handler(event)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.owner._on_widget_changed(event.input, event.value)
        handler = getattr(self.owner, "on_input_changed", None)
        if handler:
            handler(event)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.owner._on_widget_changed(event.checkbox, event.value)
        handler = getattr(self.owner, "on_checkbox_changed", None)
        if handler:
            handler(event)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        self.owner._on_widget_changed(event.switch, event.value)
        handler = getattr(self.owner, "on_switch_changed", None)
        if handler:
            handler(event)


class TextualApp(BagAppBase):
    """The puppeteer: configures and drives a LiveApp.

    Subclass and override recipe(page) to define your UI.
    Everything goes in the recipe: widgets, CSS, bindings.
    """

    builder_class = TextualBuilder
    compiler_class = TextualCompiler

    def __init__(self, remote_port: int | None = None) -> None:
        super().__init__()
        self._live_app: LiveApp | None = None
        self._updating_from_widget = False
        if remote_port is not None:
            from genro_textual.remote import RemoteServer
            self._remote_server: RemoteServer | None = RemoteServer(self, remote_port)
        else:
            self._remote_server = None

    @property
    def page(self) -> BuilderBag:
        """The page Bag (UI structure). Domain name for source."""
        return self.source

    @property
    def data(self) -> Bag:
        """The data Bag. Setting values triggers reactive updates."""
        return self._data

    @data.setter
    def data(self, value: Bag | dict[str, Any]) -> None:
        """Replace data entirely. Delegates to BagAppBase."""
        BagAppBase.data.fset(self, value)

    def recipe(self, page: BuilderBag) -> None:
        """Override to build your UI. page is a BuilderBag with TextualBuilder."""

    def render(self, compiled_bag: Bag) -> None:
        """Mount widgets from CompiledBag into the LiveApp."""
        if self._live_app is None or self._live_app.root is None:
            return None
        self._live_app.root.remove_children()
        self._compiler.render(compiled_bag, self._live_app)
        return None

    def _on_node_updated(self, node: BagNode) -> None:
        """Called by BindingManager when a bound node changes.

        Uses call_from_thread for thread safety — the binding callback
        may arrive from a different thread (remote, timer).
        Updates the specific widget, not the entire tree.
        """
        if self._updating_from_widget or not self._auto_compile:
            return
        widget = node.compiled.get("widget")
        if widget is None:
            return
        if self._live_app is not None:
            self._live_app.call_from_thread(self._update_widget, node, widget)
        else:
            self._update_widget(node, widget)

    def _update_widget(self, node: BagNode, widget: Any) -> None:
        """Apply node value/attr changes to the Textual widget."""
        value = node.value
        if isinstance(widget, Static):
            widget.update(str(value) if value is not None else "")
        elif isinstance(widget, Input):
            widget.value = str(value) if value is not None else ""
        elif isinstance(widget, (Checkbox, Switch)):
            widget.value = bool(value)
        elif hasattr(widget, "label"):
            widget.label = str(value) if value is not None else ""

    def _on_widget_changed(self, widget: Any, value: Any) -> None:
        """Called by LiveApp when a widget value changes (bidirectional binding).

        Writes the new value back to the data Bag. The _updating_from_widget
        flag prevents the loop: widget→data→binding→widget.
        """
        node = getattr(widget, "_bag_node", None)
        if node is None:
            return
        bindings = node.compiled.get("bindings", [])
        for b in bindings:
            if b["location"] == "value":
                self._updating_from_widget = True
                node.set_relative_data(self.data, b["pointer_info"].raw[1:], value)
                self._updating_from_widget = False
                break

    def run(self) -> None:
        """Run the Textual app."""
        self._live_app = LiveApp(self)
        if self._remote_server is not None:
            self._remote_server.start()
        self._live_app.run()
