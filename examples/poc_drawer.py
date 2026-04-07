# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""POC: App shell with inspector drawer using component slots.

Uses the app_shell component from FoundationMixin with named slot 'content'.

Run with:
    python examples/poc_drawer.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """App using the built-in shell with inspector."""

    def main(self, source):
        shell = source.app_shell(
            title="My Application",
            data_store=self.data,
            source_store=self.source,
            compiled_store=self.compiled,
        )

        shell.content.static("^greeting")
        shell.content.input(value="^form.name", placeholder="Name")
        shell.content.input(value="^form.surname", placeholder="Surname")
        shell.content.static("")
        for i in range(1, 10):
            shell.content.static(f"  Content line {i}")

    def store(self, data):
        self._init_shell_data()
        data["greeting"] = "Hello!"
        data["form.name"] = "John"
        data["form.surname"] = "Doe"


if __name__ == "__main__":
    Application().run()
