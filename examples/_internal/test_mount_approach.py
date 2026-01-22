# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Test del nuovo approccio con mount() invece di yield."""

from textual.app import App
from textual.containers import Vertical
from textual.widgets import Button, Static


class TestMountApp(App):
    """App di test che usa mount() invece di yield per costruire la UI."""

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.root = None

    def compose(self):
        self.root = Vertical(id="root")
        return [self.root]

    def on_mount(self):
        # Simula la compile - costruisce la gerarchia con mount()
        self.root.mount(Static("Hello from mount!"))
        self.root.mount(Button("Click me", id="btn-1"))

        # Container annidato
        inner = Vertical(id="inner")
        self.root.mount(inner)
        inner.mount(Static("Inside inner container"))
        inner.mount(Button("Inner button", id="btn-2"))


if __name__ == "__main__":
    TestMountApp().run()
