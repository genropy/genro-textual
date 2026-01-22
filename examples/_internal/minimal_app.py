# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Minimal app to debug widget ID issues."""

from __future__ import annotations

from genro_textual import TextualApp


class Application(TextualApp):
    """Minimal app with just a header and button."""

    def recipe(self, root):
        c = root.container()
        c.static("Hello World")
