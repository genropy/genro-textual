# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for the genro-textual pipeline: builder, compiler, app, binding.

All tests run without a Textual terminal — they test the Bag pipeline
up to the built bag level. Widget rendering (mount) requires Textual
and is not tested here.
"""
from __future__ import annotations

from genro_bag import Bag
from genro_builders.builder_bag import BuilderBag

from genro_textual.textual_builder import TextualBuilder
from genro_textual.textual_compiler import TextualCompiler


# ---------------------------------------------------------------------------
# Helper: create a TextualApp without Textual, run pipeline via setup()
# ---------------------------------------------------------------------------


def _make_app(main_fn, render_counter=None):
    """Create a TextualApp, run full pipeline (sync, no event loop)."""
    from genro_textual.textual_app import TextualApp

    class TestApp(TextualApp):
        def main(self, source):
            main_fn(source)

        def _do_render(self):
            if render_counter is not None:
                render_counter["n"] += 1

    app = TestApp()
    # In sync context (no event loop): setup + build + subscribe
    from genro_builders import BuilderManager
    BuilderManager.setup(app)   # store + main
    app.build()                 # sync — returns None (no event loop)
    app.subscribe()             # activate bindings + _do_render
    return app


# ---------------------------------------------------------------------------
# Builder tests
# ---------------------------------------------------------------------------


class TestBuilder:
    """Test TextualBuilder schema and element creation."""

    def test_schema_has_elements(self):
        assert len(TextualBuilder._class_schema) > 50

    def test_schema_has_css_and_binding(self):
        tags = [n.label for n in TextualBuilder._class_schema]
        assert "css" in tags
        assert "binding" in tags

    def test_schema_has_components(self):
        tags = [n.label for n in TextualBuilder._class_schema]
        assert "fieldset" in tags
        assert "form" in tags

    def test_create_static(self):
        page = BuilderBag(builder=TextualBuilder)
        page.static("Hello")
        assert len(page) == 1
        node = list(page)[0]
        assert node.node_tag == "static"
        assert node.value == "Hello"

    def test_create_container_with_children(self):
        page = BuilderBag(builder=TextualBuilder)
        v = page.vertical()
        v.static("Child 1")
        v.button("Child 2")
        assert len(page) == 1
        container = list(page)[0]
        assert isinstance(container.value, Bag)
        assert len(container.value) == 2

    def test_create_tabbedcontent(self):
        page = BuilderBag(builder=TextualBuilder)
        tabs = page.tabbedcontent()
        tab1 = tabs.tabpane(title="Tab 1")
        tab1.static("Content")
        assert len(page) == 1
        assert list(page)[0].node_tag == "tabbedcontent"

    def test_create_datatable(self):
        page = BuilderBag(builder=TextualBuilder)
        table = page.datatable(zebra_stripes=True)
        table.column("Name", key="name")
        table.row(["Alice"], key="r1")
        children = list(list(page)[0].value)
        assert children[0].node_tag == "column"
        assert children[1].node_tag == "row"

    def test_css_element(self):
        page = BuilderBag(builder=TextualBuilder)
        page.css(".title { color: red; }")
        node = list(page)[0]
        assert node.node_tag == "css"
        assert node.value == ".title { color: red; }"

    def test_binding_element(self):
        page = BuilderBag(builder=TextualBuilder)
        page.binding(key="q", action="quit", description="Quit")
        node = list(page)[0]
        assert node.node_tag == "binding"
        assert node.attr["key"] == "q"
        assert node.attr["action"] == "quit"


# ---------------------------------------------------------------------------
# Mixin inheritance tests
# ---------------------------------------------------------------------------


class TestMixinInheritance:
    """Test that subclassing TextualBuilder via mixin inherits schema."""

    def test_subclass_inherits_all_elements(self):
        from genro_builders.builder import component

        class MyMixin:
            @component(sub_tags="")
            def custom_widget(self, comp, **kwargs):
                comp.static("custom")

        class MyBuilder(MyMixin, TextualBuilder):
            pass

        parent_count = len(TextualBuilder._class_schema)
        child_count = len(MyBuilder._class_schema)
        assert child_count == parent_count + 1

    def test_subclass_can_use_parent_elements(self):
        from genro_builders.builder import component

        class MyMixin:
            @component(sub_tags="")
            def my_comp(self, comp, **kwargs):
                comp.static("inside component")

        class MyBuilder(MyMixin, TextualBuilder):
            pass

        page = BuilderBag(builder=MyBuilder)
        page.static("Hello")
        page.my_comp()
        page.button("OK")
        assert len(page) == 3


# ---------------------------------------------------------------------------
# Compiler tests (using builder pipeline)
# ---------------------------------------------------------------------------


class TestCompiler:
    """Test builder pipeline: build phase (no rendering)."""

    def _make_builder(self, data=None):
        """Create a standalone TextualBuilder with full pipeline."""
        builder = TextualBuilder()
        if data is not None:
            builder._data = data
        return builder

    def test_build_basic(self):
        builder = self._make_builder()
        builder.source.static("Hello")
        builder.source.button("OK")
        builder.build()
        built = builder.built
        assert len(built) == 2
        nodes = list(built)
        assert nodes[0].node_tag == "static"
        assert nodes[1].node_tag == "button"

    def test_build_keeps_pointers_formal(self):
        """Pointer formali: ^pointer strings stay in built Bag."""
        data = Bag()
        data.set_backref()
        data["greeting"] = "Hello!"
        builder = self._make_builder(data)
        builder.source.static("^greeting")
        builder.build()
        node = list(builder.built)[0]
        # Value stays as ^pointer in built bag
        assert node.get_value(static=True) == "^greeting"
        # But resolves just-in-time via _resolve_node
        resolved = builder._resolve_node(node, data)
        assert resolved["node_value"] == "Hello!"

    def test_build_keeps_attr_pointers_formal(self):
        """Attr pointers stay formal in built Bag."""
        data = Bag()
        data.set_backref()
        data["form.name"] = "Giovanni"
        builder = self._make_builder(data)
        builder.source.input(value="^form.name", placeholder="Name")
        builder.build()
        node = list(builder.built)[0]
        # Attr stays as ^pointer in built bag
        assert node.attr.get("value") == "^form.name"
        # Resolves just-in-time
        resolved = builder._resolve_node(node, data)
        assert resolved["attrs"]["value"] == "Giovanni"

    def test_build_expands_component(self):
        builder = self._make_builder()
        builder.source.fieldset(title="User Info")
        builder.build()
        node = list(builder.built)[0]
        assert node.node_tag == "fieldset"
        assert isinstance(node.value, Bag)
        child = list(node.value)[0]
        assert child.node_tag == "static"
        assert child.value == "User Info"

    def test_build_preserves_css_and_binding(self):
        builder = self._make_builder()
        builder.source.css(".x { color: red; }")
        builder.source.binding(key="q", action="quit", description="Quit")
        builder.source.static("Hello")
        builder.build()
        tags = [n.node_tag for n in builder.built]
        assert tags == ["css", "binding", "static"]


# ---------------------------------------------------------------------------
# App pipeline tests (without Textual)
# ---------------------------------------------------------------------------


class TestAppPipeline:
    """Test TextualApp pipeline without running Textual."""

    def test_basic_pipeline(self):
        def build_ui(source):
            source.static("Hello")
            source.button("OK")

        app = _make_app(build_ui)
        assert len(app.compiled) == 2

    def test_pointer_binding(self):
        def build_ui(source):
            source.static("^title")

        app = _make_app(build_ui)
        app.data["title"] = "Hello"

        # Pointer is formal in built bag; resolve just-in-time
        node = list(app.compiled)[0]
        resolved = app._page_builder._resolve_node(node, app.data)
        assert resolved["node_value"] == "Hello"

    def test_reactive_data_change(self):
        """Data change triggers _on_node_updated via BindingManager."""
        def build_ui(source):
            source.static("^msg")

        app = _make_app(build_ui)
        app.data["msg"] = "Initial"

        node = list(app.compiled)[0]
        resolved = app._page_builder._resolve_node(node, app.data)
        assert resolved["node_value"] == "Initial"

        app.data["msg"] = "Updated"
        resolved = app._page_builder._resolve_node(node, app.data)
        assert resolved["node_value"] == "Updated"


# ---------------------------------------------------------------------------
# Incremental update tests (simulates REPL)
# ---------------------------------------------------------------------------


class TestIncrementalRepl:
    """Test incremental updates — simulates REPL adding/removing nodes."""

    def test_add_node_after_setup(self):
        """Simulates REPL: app.page.static('New widget')."""
        def build_ui(source):
            source.static("Original")

        app = _make_app(build_ui)
        assert len(app.compiled) == 1

        app.page.static("Added from REPL")

        assert len(app.compiled) == 2
        tags = [n.node_tag for n in app.compiled]
        assert tags == ["static", "static"]

    def test_add_triggers_render(self):
        """Adding a node should trigger _do_render."""
        counter = {"n": 0}

        def build_ui(source):
            source.static("Hello")

        app = _make_app(build_ui, render_counter=counter)
        initial = counter["n"]

        app.page.button("New button")
        assert counter["n"] > initial

    def test_add_node_with_pointer(self):
        """Simulates REPL: app.page.static('^msg') with data binding."""
        def build_ui(source):
            source.static("Fixed")

        app = _make_app(build_ui)
        app.data["msg"] = "Dynamic"

        app.page.static("^msg")

        assert len(app.compiled) == 2
        new_node = list(app.compiled)[1]
        resolved = app._page_builder._resolve_node(new_node, app.data)
        assert resolved["node_value"] == "Dynamic"

    def test_multiple_adds(self):
        """Simulates multiple REPL commands."""
        def build_ui(source):
            source.static("Start")

        app = _make_app(build_ui)

        app.page.button("Button 1")
        app.page.button("Button 2")
        app.page.static("End")

        assert len(app.compiled) == 4
        tags = [n.node_tag for n in app.compiled]
        assert tags == ["static", "button", "button", "static"]
