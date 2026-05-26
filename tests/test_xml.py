# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for the XML rendering pipeline of genro-textual.

These tests exercise the builder + handler + xml renderer chain
without spinning up a Textual event loop. They verify the grammar
schema, the TextualBuilder configuration and the round-trip from
``handler.create()`` (populate source) to ``handler.render_xml()``
(serialize source as XML).

The XML mode is inherited for free from BagBuilderBase (every dialect
registers XmlRenderer in __init__) and gives us a stable reference
output to assert against — no Textual needed.
"""
from __future__ import annotations

from genro_textual import TextualApp, TextualBuilder, TextualRenderer


# ----------------------------------------------------------------------
# Builder configuration
# ----------------------------------------------------------------------


class TestBuilderConfig:
    """TextualBuilder declares grammar + registers the textual renderer."""

    def test_name(self):
        assert TextualBuilder._name == "textual"

    def test_default_render_mode(self):
        assert TextualBuilder._default_render_mode == "textual"

    def test_registers_textual_renderer(self):
        b = TextualBuilder()
        assert "textual" in b._renderers
        assert b._renderers["textual"] is TextualRenderer

    def test_inherits_xml_mode_from_base(self):
        """XmlRenderer is registered by BagBuilderBase.__init__."""
        b = TextualBuilder()
        assert "xml" in b._renderers

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
    """TextualApp(BuilderHandler) supports create() + render(xml)."""

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

    def test_render_xml_returns_string(self):
        class App(TextualApp):
            def main(self, source):
                source.static("Hello")

        app = App()
        app.create()
        xml = app.render_xml()
        assert isinstance(xml, str)
        assert "<static>Hello</static>" in xml

    def test_page_property_is_alias_for_source(self):
        class App(TextualApp):
            def main(self, source):
                source.static("X")

        app = App()
        app.create()
        assert app.page is app.source


# ----------------------------------------------------------------------
# XML output shape per widget family
# ----------------------------------------------------------------------


class TestXmlOutputShape:
    """Each widget family produces the expected XML shape."""

    def _render(self, main_fn):
        class App(TextualApp):
            def main(self, source):
                main_fn(source)

        app = App()
        app.create()
        return app.render_xml(pretty=True)

    def test_leaf_static(self):
        xml = self._render(lambda s: s.static("Hello"))
        assert "<static>Hello</static>" in xml

    def test_leaf_button_with_attrs(self):
        xml = self._render(lambda s: s.button("OK", variant="primary"))
        assert "<button" in xml
        assert 'variant="primary"' in xml
        assert ">OK</button>" in xml

    def test_container_with_children(self):
        def build(s):
            v = s.vertical()
            v.static("a")
            v.static("b")
        xml = self._render(build)
        assert "<vertical>" in xml
        assert xml.count("<static>") == 2

    def test_nested_containers(self):
        def build(s):
            outer = s.container()
            inner = outer.vertical()
            inner.button("deep")
        xml = self._render(build)
        assert "<container>" in xml
        assert "<vertical>" in xml
        assert ">deep</button>" in xml

    def test_tabbedcontent_with_panes(self):
        def build(s):
            tabs = s.tabbedcontent(initial="t1")
            t1 = tabs.tabpane(title="One", id="t1")
            t1.static("first")
            t2 = tabs.tabpane(title="Two", id="t2")
            t2.static("second")
        xml = self._render(build)
        assert 'initial="t1"' in xml
        assert xml.count("<tabpane") == 2
        assert 'title="One"' in xml
        assert 'title="Two"' in xml

    def test_datatable_with_columns_and_rows(self):
        def build(s):
            t = s.datatable(zebra_stripes=True)
            t.column("Name", key="n")
            t.column("Age", key="a")
            t.row(["Alice", 30], key="r1")
        xml = self._render(build)
        assert "<datatable" in xml
        assert 'zebra_stripes="True"' in xml
        assert xml.count("<column") == 2
        assert xml.count("<row") == 1

    def test_css_and_binding_are_first_class_nodes(self):
        def build(s):
            s.css(".x { color: red; }")
            s.binding(key="q", action="quit", description="Quit")
            s.static("body")
        xml = self._render(build)
        assert "<css>" in xml
        assert ".x { color: red; }" in xml
        assert "<binding" in xml
        assert 'key="q"' in xml
        assert 'action="quit"' in xml
