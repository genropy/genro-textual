# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""POC: App shell with inspector drawer.

Uses self.app_shell() for the full structure: header, content, drawer, footer.

Run with:
    python examples/poc_drawer.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """App using the built-in shell with inspector."""

    def recipe(self, page):
        content = self.app_shell(page, title="My Application")

        content.static("^greeting")
        content.input(value="^form.name", placeholder="Name")
        content.input(value="^form.surname", placeholder="Surname")
        content.static("")
        for i in range(1, 10):
            content.static(f"  Content line {i}")

    def setup(self):
        self._init_shell_data()
        self.data["greeting"] = "Hello!"
        self.data["form.name"] = "John"
        self.data["form.surname"] = "Doe"
        super().setup()


if __name__ == "__main__":
    Application().run()
