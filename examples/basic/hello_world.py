# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Minimal TextualApp example.

Run with:
    python examples/basic/hello_world.py
    textual run --dev examples/basic/hello_world.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Minimal TextualApp showing basic usage."""

    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.static("Hello, Textual!")
        source.static("Press 'q' to quit")


# Expose native Textual App for `textual run --dev`
app = Application().as_textual_app()

if __name__ == "__main__":
    Application().run()
