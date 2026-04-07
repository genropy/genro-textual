# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Example with nested containers.

Run with CLI:
    textual run examples/basic/nested_containers.py
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """App with nested containers."""

    def main(self, source):
        source.static("Main Title")

        box = source.container()
        box.static("Inside container")
        box.button("Click me", variant="primary")
