# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Tests for the genro-textual pipeline: builder, compiler, app, binding.

All tests run without a Textual terminal — they test the Bag pipeline
up to the compiled bag level. Widget rendering (mount) requires Textual
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


def _make_app(recipe_fn, render_counter=None):
    """Create a TextualApp, override render to avoid Textual, call setup()."""
    from genro_textual.textual_app import TextualApp

    class TestApp(TextualApp):
        def recipe(self, page):
            recipe_fn(page)

        def render(self, compiled_bag):
            if render_counter is not None:
                render_counter["n"] += 1

    app = TestApp()
    app.setup()
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
# Compiler tests
# ---------------------------------------------------------------------------


class TestCompiler:
    """Test TextualCompiler compile phase (no rendering)."""

    def test_compile_basic(self):
        page = BuilderBag(builder=TextualBuilder)
        page.static("Hello")
        page.button("OK")
        compiler = TextualCompiler(page.builder)
        compiled = compiler.compile(page)
        assert len(compiled) == 2
        nodes = list(compiled)
        assert nodes[0].node_tag == "static"
        assert nodes[1].node_tag == "button"

    def test_compile_resolves_pointers(self):
        page = BuilderBag(builder=TextualBuilder)
        page.static("^greeting")
        data = Bag()
        data["greeting"] = "Hello!"
        compiler = TextualCompiler(page.builder)
        compiled = compiler.compile(page, data)
        node = list(compiled)[0]
        assert node.value == "Hello!"

    def test_compile_resolves_attr_pointers(self):
        page = BuilderBag(builder=TextualBuilder)
        page.input(value="^form.name", placeholder="Name")
        data = Bag()
        data["form.name"] = "Giovanni"
        compiler = TextualCompiler(page.builder)
        compiled = compiler.compile(page, data)
        node = list(compiled)[0]
        assert node.attr["value"] == "Giovanni"

    def test_compile_expands_component(self):
        page = BuilderBag(builder=TextualBuilder)
        page.fieldset(title="User Info")
        compiler = TextualCompiler(page.builder)
        compiled = compiler.compile(page)
        node = list(compiled)[0]
        assert node.node_tag == "fieldset"
        assert isinstance(node.value, Bag)
        child = list(node.value)[0]
        assert child.node_tag == "static"
        assert child.value == "User Info"

    def test_compile_preserves_css_and_binding(self):
        page = BuilderBag(builder=TextualBuilder)
        page.css(".x { color: red; }")
        page.binding(key="q", action="quit", description="Quit")
        page.static("Hello")
        compiler = TextualCompiler(page.builder)
        compiled = compiler.compile(page)
        tags = [n.node_tag for n in compiled]
        assert tags == ["css", "binding", "static"]


# ---------------------------------------------------------------------------
# App pipeline tests (without Textual)
# ---------------------------------------------------------------------------


class TestAppPipeline:
    """Test TextualApp pipeline without running Textual."""

    def test_basic_pipeline(self):
        def recipe(page):
            page.static("Hello")
            page.button("OK")

        app = _make_app(recipe)
        assert len(app.compiled) == 2

    def test_pointer_binding(self):
        def recipe(page):
            page.static("^title")

        app = _make_app(recipe)
        app.data["title"] = "Hello"
        app._binding.rebind(app.data)

        node = list(app.compiled)[0]
        assert node.value == "Hello"

    def test_reactive_data_change(self):
        def recipe(page):
            page.static("^msg")

        app = _make_app(recipe)
        app.data["msg"] = "Initial"
        app._binding.rebind(app.data)

        node = list(app.compiled)[0]
        assert node.value == "Initial"

        app.data["msg"] = "Updated"
        assert node.value == "Updated"


# ---------------------------------------------------------------------------
# Incremental update tests (simulates REPL)
# ---------------------------------------------------------------------------


class TestIncrementalRepl:
    """Test incremental updates — simulates REPL adding/removing nodes."""

    def test_add_node_after_setup(self):
        """Simulates REPL: app.page.static('New widget')."""
        def recipe(page):
            page.static("Original")

        app = _make_app(recipe)
        assert len(app.compiled) == 1

        app.page.static("Added from REPL")

        assert len(app.compiled) == 2
        tags = [n.node_tag for n in app.compiled]
        assert tags == ["static", "static"]
        values = [n.value for n in app.compiled]
        assert values == ["Original", "Added from REPL"]

    def test_add_triggers_render(self):
        """Adding a node should trigger _rerender."""
        counter = {"n": 0}

        def recipe(page):
            page.static("Hello")

        app = _make_app(recipe, render_counter=counter)
        initial = counter["n"]

        app.page.button("New button")
        assert counter["n"] > initial

    def test_add_node_with_pointer(self):
        """Simulates REPL: app.page.static('^msg') with data binding."""
        def recipe(page):
            page.static("Fixed")

        app = _make_app(recipe)
        app.data["msg"] = "Dynamic"

        app.page.static("^msg")

        assert len(app.compiled) == 2
        new_node = list(app.compiled)[1]
        assert new_node.value == "Dynamic"

    def test_multiple_adds(self):
        """Simulates multiple REPL commands."""
        def recipe(page):
            page.static("Start")

        app = _make_app(recipe)

        app.page.button("Button 1")
        app.page.button("Button 2")
        app.page.static("End")

        assert len(app.compiled) == 4
        tags = [n.node_tag for n in app.compiled]
        assert tags == ["static", "button", "button", "static"]
