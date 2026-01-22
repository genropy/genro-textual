# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Colored stripes example (inspired by Textual Pride app).

Run with:
    textual run examples/basic/color_stripes.py

Shows how to create multiple Static widgets with different colors.
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """Display colored stripes using Static widgets."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    CSS = """
    Static {
        text-align: center;
        text-style: bold;
        height: 1fr;
    }
    .stripe-0 { background: red; }
    .stripe-1 { background: orange; }
    .stripe-2 { background: yellow; color: black; }
    .stripe-3 { background: green; }
    .stripe-4 { background: blue; }
    .stripe-5 { background: purple; }
    """

    def recipe(self, root):
        for i, color in enumerate(self.COLORS):
            root.static(f"  {color.upper()}  ", classes=f"stripe-{i}")
