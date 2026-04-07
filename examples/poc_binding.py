# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""POC: Bidirectional data binding.

Run with:
    python examples/poc_binding.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Minimal bidirectional binding test."""

    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.input(value="^mysample.data.name", placeholder="Name")
        source.input(value="^mysample.data.surname", placeholder="Surname")
        source.static("^mysample.data.name")
        source.static("^mysample.data.surname")
        source.button("OK")

    def store(self, data):
        data["mysample.data.name"] = "John"
        data["mysample.data.surname"] = "Doe"


if __name__ == "__main__":
    Application().run()
