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
    5. Widget blur/change → _on_widget_changed → data update (bidirectional)

Bidirectional binding:
    - Input widgets write to data on blur (not on every keystroke)
    - Checkbox/Switch write to data on change (immediate)
    - Anti-loop: _reason parameter prevents updating the originating widget
    - Thread safety: call_from_thread only when called from a different thread

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

import threading
from typing import TYPE_CHECKING, Any

from genro_bag import Bag, BagNode
from genro_builders.app import BagAppBase
from genro_builders.builder_bag import BuilderBag
from textual import events
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
    Delegates events to the owner (TextualApp).
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
        if self.owner._shell_active:
            if self.owner._handle_shell_button(event):
                return
        handler = getattr(self.owner, "on_button_pressed", None)
        if handler:
            handler(event)

    def on_key(self, event: Any) -> None:
        if self.owner._shell_active:
            if self.owner._handle_shell_key(event):
                return
        handler = getattr(self.owner, "on_key", None)
        if handler:
            handler(event)

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """Write Input value to data on blur (not on every keystroke)."""
        from genro_textual.debug import log
        widget = event.widget
        log(f"on_descendant_blur: {widget.__class__.__name__} id={widget.id}")
        if isinstance(widget, Input):
            log(f"  blur Input value={widget.value!r}")
            self.owner._on_widget_changed(widget, widget.value)
        handler = getattr(self.owner, "on_descendant_blur", None)
        if handler:
            handler(event)

    def on_input_changed(self, event: Input.Changed) -> None:
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
        self._shell_active = False
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

    def app_shell(self, page: BuilderBag, title: str = "App") -> Any:
        """Build an application shell with header, content area, and inspector drawer.

        Returns the content area (verticalscroll) where the user adds widgets.

        Args:
            page: The page BuilderBag.
            title: Title shown in the header bar.

        Usage::

            def recipe(self, page):
                content = self.app_shell(page, title="My App")
                content.static("My content")
                content.input(value="^form.name")
        """
        page.css("""
            #shell-header {
                height: 1; background: $primary; color: $text;
            }
            #shell-header Static { width: 1fr; padding: 0 1; }
            #shell-main { height: 1fr; }
            #shell-content { width: 1fr; }
            #shell-drawer {
                background: $surface;
                border-left: solid $primary;
            }
            #drawer-topbar {
                height: 1; background: $primary-darken-2;
            }
            #drawer-title {
                width: 1fr; padding: 0 1; color: $text;
            }
            .drawer-btn {
                min-width: 3; height: 1; border: none;
                padding: 0; background: transparent;
                color: $text-muted;
            }
            .drawer-btn:hover {
                color: $text; background: transparent;
            }
        """)
        page.binding(key="q", action="quit", description="Quit")
        page.binding(
            key="f12", action="toggle_drawer",
            description="Inspector",
        )

        header = page.horizontal(id="shell-header")
        header.static(title)

        main = page.horizontal(id="shell-main")

        content = main.verticalscroll(id="shell-content")

        drawer = main.vertical(
            id="shell-drawer",
            width="^_system.drawer.width",
            display="^_system.drawer.display",
        )
        topbar = drawer.horizontal(id="drawer-topbar")
        topbar.static("Inspector", id="drawer-title")
        topbar.button(
            "\u25c0", id="btn-drawer-expand",
            classes="drawer-btn",
        )
        topbar.button(
            "\u25b6", id="btn-drawer-shrink",
            classes="drawer-btn",
        )

        tabs = drawer.tabbedcontent()
        tabs.tabpane(title="Data", id="tab-data").tree(
            label="data", store=self.data,
        )
        tabs.tabpane(title="Source", id="tab-source").tree(
            label="source", store=self.source,
        )
        tabs.tabpane(
            title="Compiled", id="tab-compiled",
        ).tree(label="compiled", store=self.compiled)

        page.footer(show_command_palette=False)

        self._shell_active = True
        return content

    _DRAWER_WIDTH_DEFAULT = 40
    _DRAWER_WIDTH_MIN = 20
    _DRAWER_WIDTH_MAX = 80
    _DRAWER_WIDTH_STEP = 5

    def _init_shell_data(self) -> None:
        """Initialize _system data for the shell drawer."""
        self.data["_system.drawer.width"] = self._DRAWER_WIDTH_DEFAULT
        self.data["_system.drawer.display"] = "block"

    def _handle_shell_key(self, event: Any) -> bool:
        """Handle shell key events. Returns True if handled."""
        if event.key == "f12":
            current = self.data["_system.drawer.display"]
            new = "none" if current == "block" else "block"
            self.data["_system.drawer.display"] = new
            return True
        return False

    def _handle_shell_button(self, event: Any) -> bool:
        """Handle shell button events. Returns True if handled."""
        bid = event.button.id
        if bid not in ("btn-drawer-expand", "btn-drawer-shrink"):
            return False
        current = self.data["_system.drawer.width"]
        current = current or self._DRAWER_WIDTH_DEFAULT
        if bid == "btn-drawer-shrink":
            new = max(self._DRAWER_WIDTH_MIN,
                      current - self._DRAWER_WIDTH_STEP)
        else:
            new = min(self._DRAWER_WIDTH_MAX,
                      current + self._DRAWER_WIDTH_STEP)
        if new != current:
            self.data["_system.drawer.width"] = new
        return True

    def render(self, compiled_bag: Bag) -> None:
        """Mount widgets from CompiledBag into the LiveApp.

        Overrides BagAppBase.render() — Textual rendering is imperative
        (mount widgets), not string-based.
        """
        if self._live_app is None or self._live_app.root is None:
            return None
        self._live_app.root.remove_children()
        self._compiler.render(compiled_bag, self._live_app)
        return None

    def _on_node_updated(self, node: BagNode) -> None:
        """Called by BindingManager when a bound node changes.

        Uses call_from_thread only when called from a different thread
        (e.g. remote REPL, timer). Same-thread calls update directly.
        """
        if not self._auto_compile:
            return
        widget = node.compiled.get("widget")
        if widget is None:
            return
        if self._live_app is not None and self._live_app._thread_id != threading.get_ident():
            self._live_app.call_from_thread(self._update_widget, node, widget)
        else:
            self._update_widget(node, widget)

    def _update_widget(self, node: BagNode, widget: Any) -> None:
        """Apply node value/attr changes to the Textual widget.

        Handles both value updates and CSS/reactive attribute updates.
        """
        from textual.css.styles import RulesMap
        from textual.reactive import Reactive

        css_properties = RulesMap.__annotations__

        # Update value
        value = node.value
        if isinstance(widget, Static):
            widget.update(str(value) if value is not None else "")
        elif isinstance(widget, Input):
            widget.value = str(value) if value is not None else ""
        elif isinstance(widget, (Checkbox, Switch)):
            widget.value = bool(value)
        elif hasattr(widget, "label"):
            widget.label = str(value) if value is not None else ""

        # Update CSS style attributes
        for key, attr_value in node.attr.items():
            if key.startswith("_"):
                continue
            if key in css_properties:
                setattr(widget.styles, key, attr_value)
            elif isinstance(getattr(type(widget), key, None), Reactive):
                widget.set_reactive(getattr(type(widget), key), attr_value)

    def _on_widget_changed(self, widget: Any, value: Any) -> None:
        """Called by LiveApp on blur (Input) or change (Checkbox/Switch).

        Writes the widget value back to the data Bag using _reason
        for anti-loop: the BindingManager skips the originating node.

        Finds the data path by reverse-lookup in the subscription map:
        searches for the compiled node path in the map values.
        """
        from genro_textual.debug import log
        node = getattr(widget, "_bag_node", None)
        log(f"_on_widget_changed: {type(widget).__name__} v={value!r} node={node is not None}")
        if node is None:
            return
        # Find compiled path of this node
        compiled_path = self._find_compiled_path(node)
        log(f"  compiled_path={compiled_path!r}")
        if not compiled_path:
            return
        # Reverse-lookup: find data_key for this compiled entry
        data_path = self._find_data_path(compiled_path)
        log(f"  data_path={data_path!r}")
        if data_path:
            log(f"  writing data[{data_path!r}] = {value!r} with reason={compiled_path!r}")
            self.data.set_item(data_path, value, _reason=compiled_path)

    def _find_compiled_path(self, node: BagNode) -> str | None:
        """Find the path of a node relative to the compiled Bag."""
        return self.compiled.relative_path(node)

    def _find_data_path(self, compiled_path: str) -> str | None:
        """Reverse-lookup: find the data path bound to a compiled entry.

        Searches for compiled_path or compiled_path?value in the map.
        """
        smap = self._binding.subscription_map
        # Check for attr:value binding (e.g. input with value="^path")
        entry_with_attr = f"{compiled_path}?value"
        for data_key, entries in smap.items():
            if entry_with_attr in entries or compiled_path in entries:
                return data_key.partition("?")[0]
        return None

    def run(self) -> None:
        """Run the Textual app."""
        self._live_app = LiveApp(self)
        if self._remote_server is not None:
            self._remote_server.start()
        self._live_app.run()
