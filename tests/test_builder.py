# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for the builder + handler configuration of genro-textual.

These tests exercise the grammar schema, the TextualBuilder renderer
wiring (the ``renderer_textual`` property the core resolves through
``get_render``) and the ``create()`` lifecycle that populates the
source bag — all without spinning up a Textual event loop. The live
widget shape is covered by ``test_pilot.py``.
"""
from __future__ import annotations

from genro_textual import TextualApp, TextualBuilder, TextualRenderer

# ----------------------------------------------------------------------
# Builder configuration
# ----------------------------------------------------------------------


class TestBuilderConfig:
    """TextualBuilder declares grammar + exposes the textual renderer."""

    def test_name(self):
        assert TextualBuilder._name == "textual"

    def test_default_render_mode(self):
        assert TextualBuilder._default_render_mode == "textual"

    def test_exposes_textual_renderer(self):
        """The ``renderer_textual`` property yields a TextualRenderer
        (object dialect) bound to the builder — the core resolves it
        through ``get_render``."""
        b = TextualBuilder()
        renderer = b.renderer_textual
        assert isinstance(renderer, TextualRenderer)
        assert renderer.mode == "textual"
        assert renderer.render_type == "object"
        assert renderer.builder is b

    def test_schema_has_expected_widget_tags(self):
        """A handful of representative tags must be in the grammar."""
        b = TextualBuilder()
        tags = {n.label for n in b._schema}
        for expected in [
            "static", "button", "input", "container", "vertical",
            "tabbedcontent", "tabpane", "datatable", "column", "row",
            "tree", "css", "binding",
        ]:
            assert expected in tags, f"tag '{expected}' missing from schema"


# ----------------------------------------------------------------------
# Handler lifecycle
# ----------------------------------------------------------------------


class TestHandlerLifecycle:
    """TextualApp(BuilderHandler) populates the source via create()."""

    def test_handler_binds_builder_class(self):
        assert TextualApp.builder_class is TextualBuilder

    def test_create_populates_source(self):
        class App(TextualApp):
            def main(self, source):
                source.static("Hello")
                source.button("OK")

        app = App()
        app.create()
        assert len(app.source) == 2

    def test_page_property_is_alias_for_source(self):
        class App(TextualApp):
            def main(self, source):
                source.static("X")

        app = App()
        app.create()
        assert app.page is app.source
