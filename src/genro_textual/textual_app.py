# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualApp - Reactive Textual app driven by genro-builders.

Architecture: puppeteer and puppet.

    TextualApp (BuilderManager) is the puppeteer — configures store, main,
    builder. Creates and drives the LiveApp.

    LiveApp (textual.app.App) is the puppet — no logic of its own.
    Built and controlled by the puppeteer.

Everything goes through the Bag: CSS, bindings, widgets — all declared
in main() as nodes. The compiler extracts app config (css, binding)
and applies it to the LiveApp, then mounts widgets.

Lifecycle:
    1. TextualApp() → BuilderManager.__init_subclass__ wraps __init__
    2. run() → creates LiveApp, starts Textual event loop
    3. LiveApp.on_mount() → setup() = store + main + build + subscribe + render
    4. Data changes → BindingManager fires _on_node_updated → widget update
    5. Widget blur/change → _on_widget_changed → data update (bidirectional)

Bidirectional binding:
    - Input widgets write to data on blur (not on every keystroke)
    - Checkbox/Switch write to data on change (immediate)
    - Anti-loop: _reason parameter prevents updating the originating widget
    - Thread safety: call_from_thread only when called from a different thread

Example:
    from genro_textual import TextualApp

    class MyApp(TextualApp):
        def main(self, page):
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
from genro_builders import BuilderManager
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

    Has no CSS or BINDINGS of its own — those come from main()
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

    async def on_mount(self) -> None:
        await self.owner._activate()

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


class TextualApp(BuilderManager):
    """The puppeteer: configures and drives a LiveApp.

    Subclass and override main(page) to define your UI,
    and store(data) to populate initial data.
    """

    def __init__(self, remote_port: int | None = None) -> None:
        self._page_builder = self.set_builder('page', TextualBuilder)
        self._compiler = TextualCompiler(self._page_builder)
        self._live_app: LiveApp | None = None
        self._shell_active = False
        # Wire surgical widget updates instead of full re-render
        self._page_builder._binding._on_node_updated = self._on_node_updated
        # Override _rerender on builder: Textual does imperative widget
        # mounting, not string rendering. Delegate to _do_render.
        self._page_builder._rerender = self._do_render
        if remote_port is not None:
            from genro_textual.remote import RemoteServer
            self._remote_server: RemoteServer | None = RemoteServer(self, remote_port)
        else:
            self._remote_server = None

    # -------------------------------------------------------------------------
    # Properties (backward-compatible proxies)
    # -------------------------------------------------------------------------

    @property
    def page(self) -> BuilderBag:
        """The page Bag (UI structure). Domain name for source."""
        return self._page_builder.source

    @property
    def source(self) -> BuilderBag:
        """Alias for page — the source Bag."""
        return self._page_builder.source

    @property
    def data(self) -> Bag:
        """The data Bag. Setting values triggers reactive updates."""
        return self.reactive_store

    @data.setter
    def data(self, value: Bag | dict[str, Any]) -> None:
        """Replace data entirely."""
        self.reactive_store = value

    @property
    def compiled(self) -> BuilderBag:
        """The built Bag (components expanded, pointers formal)."""
        return self._page_builder.built

    @property
    def _binding(self):
        """Access the builder's BindingManager."""
        return self._page_builder._binding

    @property
    def _auto_compile(self):
        """Whether auto-compile is active on the builder."""
        return self._page_builder._auto_compile

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def _activate(self) -> None:
        """Full lifecycle: store -> main -> build -> subscribe -> render.

        Called from LiveApp.on_mount() (async context). Uses smartawait
        so that component resolvers expand correctly inside the event loop.
        """
        from genro_toolbox import smartawait
        super().setup()                          # store + main (sync)
        await smartawait(self.build())           # source -> built (async-safe)
        self.subscribe()                         # activate bindings + _do_render

    # -------------------------------------------------------------------------
    # Shell (inspector drawer)
    # -------------------------------------------------------------------------

    _DRAWER_WIDTH_DEFAULT = 40
    _DRAWER_WIDTH_MIN = 20
    _DRAWER_WIDTH_MAX = 80
    _DRAWER_WIDTH_STEP = 5

    def _init_shell_data(self) -> None:
        """Initialize _system data for the shell drawer."""
        self.data["_system.drawer.width"] = self._DRAWER_WIDTH_DEFAULT
        self.data["_system.drawer.display"] = "block"
        self._shell_active = True

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

    # -------------------------------------------------------------------------
    # Rendering
    # -------------------------------------------------------------------------

    def _do_render(self) -> None:
        """Mount widgets from built Bag into the LiveApp.

        Called after setup and on full re-render.
        """
        if self._live_app is None or self._live_app.root is None:
            return
        self._compiler.compile(self._page_builder.built, target=self._live_app)

    # -------------------------------------------------------------------------
    # Reactive: data -> widget
    # -------------------------------------------------------------------------

    def _on_node_updated(self, node: BagNode) -> None:
        """Called by BindingManager when a bound node changes.

        Uses call_from_thread only when called from a different thread
        (e.g. remote REPL, timer). Same-thread calls update directly.
        """
        if not self._page_builder._auto_compile:
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

        Resolves pointer formali just-in-time before updating.
        """
        from textual.css.styles import RulesMap
        from textual.reactive import Reactive

        css_properties = RulesMap.__annotations__

        # Resolve pointer formali
        resolved = self._page_builder._resolve_node(node, self._page_builder.data)
        value = resolved["node_value"]
        attrs = resolved["attrs"]

        # Update value
        if isinstance(widget, Static):
            widget.update(str(value) if value is not None else "")
        elif isinstance(widget, Input):
            widget.value = str(value) if value is not None else ""
        elif isinstance(widget, (Checkbox, Switch)):
            widget.value = bool(value)
        elif hasattr(widget, "label"):
            widget.label = str(value) if value is not None else ""

        # Update CSS style attributes and reactive attributes
        for key, attr_value in attrs.items():
            if key.startswith("_"):
                continue
            if key in css_properties:
                setattr(widget.styles, key, attr_value)
            elif isinstance(getattr(type(widget), key, None), Reactive):
                widget.set_reactive(getattr(type(widget), key), attr_value)

    # -------------------------------------------------------------------------
    # Reactive: widget -> data (bidirectional)
    # -------------------------------------------------------------------------

    def _on_widget_changed(self, widget: Any, value: Any) -> None:
        """Called by LiveApp on blur (Input) or change (Checkbox/Switch).

        Writes the widget value back to the data Bag using _reason
        for anti-loop: the BindingManager skips the originating node.
        """
        from genro_textual.debug import log
        node = getattr(widget, "_bag_node", None)
        log(f"_on_widget_changed: {type(widget).__name__} v={value!r} node={node is not None}")
        if node is None:
            return
        compiled_path = self._find_compiled_path(node)
        log(f"  compiled_path={compiled_path!r}")
        if not compiled_path:
            return
        data_path = self._find_data_path(compiled_path)
        log(f"  data_path={data_path!r}")
        if data_path:
            log(f"  writing data[{data_path!r}] = {value!r} with reason={compiled_path!r}")
            self.data.set_item(data_path, value, _reason=compiled_path)

    def _find_compiled_path(self, node: BagNode) -> str | None:
        """Find the path of a node relative to the built Bag."""
        return self._page_builder.built.relative_path(node)

    def _find_data_path(self, compiled_path: str) -> str | None:
        """Reverse-lookup: find the data path bound to a compiled entry."""
        smap = self._page_builder._binding.subscription_map
        entry_with_attr = f"{compiled_path}?value"
        for data_key, entries in smap.items():
            if entry_with_attr in entries or compiled_path in entries:
                return data_key.partition("?")[0]
        return None

    # -------------------------------------------------------------------------
    # Run
    # -------------------------------------------------------------------------

    def as_textual_app(self) -> LiveApp:
        """Return the native Textual App for use with textual devtools.

        Creates the LiveApp without starting it. The full lifecycle
        (store, main, build, subscribe, render) happens in on_mount().

        This enables compatibility with ``textual run --dev`` and
        ``textual serve``::

            # In your example file:
            app = Application().as_textual_app()

            # Then run with: textual run --dev examples/my_app.py
        """
        self._live_app = LiveApp(self)
        return self._live_app

    def run(self, *, subscribe: bool = False) -> None:
        """Run the Textual app.

        Lifecycle:
            1. LiveApp.run() — starts Textual event loop
            2. on_mount() → _activate() — store + main + build + subscribe + render
        """
        self._live_app = LiveApp(self)
        if self._remote_server is not None:
            self._remote_server.start()
        self._live_app.run()
