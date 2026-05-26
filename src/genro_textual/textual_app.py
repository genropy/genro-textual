# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualApp - BuilderHandler that drives a live Textual application.

Architecture: puppeteer and puppet.

    TextualApp (BuilderHandler) is the puppeteer. Owns the source bag
    via BuilderHandler.create(), creates and drives the LiveApp.

    LiveApp (textual.app.App) is the puppet — no logic of its own.
    Mounted by the puppeteer.

Everything goes through the source bag: CSS, key bindings, widgets —
all declared in ``main(self, source)`` as nodes. TextualRenderer extracts
app config (css, binding) and applies it to the LiveApp, then mounts
widgets on ``LiveApp.root``.

Lifecycle (2 phases, decision 5 v0.4.0):
    1. TextualApp() → BuilderHandler.__init__ instantiates the builder
       and the source bag.
    2. run() / as_textual_app() → creates LiveApp.
    3. LiveApp.on_mount() → _activate() = create() + render() against
       the live target.

Example:
    from genro_textual import TextualApp

    class MyApp(TextualApp):
        def main(self, source):
            source.css(".title { color: green; }")
            source.binding(key="q", action="quit", description="Quit")
            source.static("Hello!", classes="title")

    if __name__ == "__main__":
        MyApp().run()
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from genro_builders.builder_handler import BuilderHandler
from textual.app import App
from textual.containers import Vertical
from textual.widgets import Button

from genro_textual.textual_builder import TextualBuilder

if TYPE_CHECKING:
    from genro_textual.remote import RemoteServer


class LiveApp(App):
    """The puppet: a bare textual.app.App driven by TextualApp.

    Has no CSS or BINDINGS of its own — those come from main() and are
    applied by TextualRenderer at render time. Delegates events to the
    owner (TextualApp).
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
        handler = getattr(self.owner, "on_button_pressed", None)
        if handler:
            handler(event)

    def on_key(self, event: Any) -> None:
        handler = getattr(self.owner, "on_key", None)
        if handler:
            handler(event)


class TextualApp(BuilderHandler):
    """The puppeteer: a BuilderHandler that drives a LiveApp.

    Subclass and override ``main(self, source)`` to populate the source
    bag with widgets, css and key bindings.
    """

    builder_class = TextualBuilder

    def __init__(self, remote_port: int | None = None) -> None:
        super().__init__()
        self._live_app: LiveApp | None = None
        self._remote_server: RemoteServer | None = None
        if remote_port is not None:
            from genro_textual.remote import RemoteServer
            self._remote_server = RemoteServer(self, remote_port)

    # ------------------------------------------------------------------
    # Backward-compatible alias
    # ------------------------------------------------------------------

    @property
    def page(self):
        """Domain name for ``source`` — used by example/tutorial code."""
        return self.source

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _activate(self) -> None:
        """Create the source and mount widgets onto the live target.

        Called from LiveApp.on_mount() (async context). Uses smartawait
        so any async grammar callbacks expand correctly inside the
        Textual event loop.
        """
        from genro_toolbox import smartawait
        await smartawait(self.create())
        if self._live_app is not None:
            self.set_render_target("textual", self._live_app, default=True)
            self.render()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def as_textual_app(self) -> LiveApp:
        """Return the native Textual App for use with textual devtools.

        Creates the LiveApp without starting it. The full lifecycle
        (create + render) happens inside LiveApp.on_mount().

        Enables ``textual run --dev`` and ``textual serve``::

            # In your example file:
            app = Application().as_textual_app()
        """
        self._live_app = LiveApp(self)
        return self._live_app

    def run(self) -> None:
        """Run the Textual app.

        Lifecycle:
            1. LiveApp.run() — starts the Textual event loop.
            2. on_mount() → _activate() — create() + render().
        """
        self._live_app = LiveApp(self)
        if self._remote_server is not None:
            self._remote_server.start()
        self._live_app.run()
