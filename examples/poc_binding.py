# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""POC: Bidirectional data binding.

Run with:
    python examples/poc_binding.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Minimal bidirectional binding test."""

    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.input(value="^mysample.data.name", placeholder="Name")
        page.input(value="^mysample.data.surname", placeholder="Surname")
        page.static("^mysample.data.name")
        page.static("^mysample.data.surname")
        page.button("OK")

    def setup(self):
        self.data["mysample.data.name"] = "John"
        self.data["mysample.data.surname"] = "Doe"
        super().setup()


if __name__ == "__main__":
    Application().run()
