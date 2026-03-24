# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualCompiler - Compiler that renders CompiledBag into Textual widgets.

Inherits compile() from BagCompilerBase: materialize components + resolve ^pointers.
Rendering is a separate concern: walk the CompiledBag and mount Widget objects
to a parent widget. This is fundamentally different from string-based rendering
(HTML, Markdown) because Textual widgets are imperative objects with parent-child
mounting, not composable strings.

Rendering dispatch:
    1. _render_<tag> method on this class (for special widgets)
    2. _render_default: generic rendering via compile_kwargs (module + class)

Each rendered node stores its widget in node.compiled["widget"] so the
BindingManager can later update it on data changes.
"""
from __future__ import annotations

import inspect
from importlib import import_module
from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.compiler import BagCompilerBase
from textual.widget import Widget


class TextualCompiler(BagCompilerBase):
    """Compiler for Textual: compile() + render to Widget tree."""

    def __init__(self, builder: Any) -> None:
        super().__init__(builder)
        self._widget_counter = 0

    @property
    def widget_counter(self) -> int:
        """Return current counter and auto-increment."""
        current = self._widget_counter
        self._widget_counter += 1
        return current

    # -------------------------------------------------------------------------
    # Rendering: CompiledBag → Widget tree
    # -------------------------------------------------------------------------

    def render(self, compiled_bag: Bag, live_app: Any) -> None:
        """Walk the CompiledBag, extract app config, mount widgets.

        Nodes tagged 'css' and 'binding' are app configuration —
        applied to live_app, not rendered as widgets.
        All other nodes are rendered as widgets into live_app.root.
        """
        css_parts: list[str] = []

        for node in compiled_bag:
            if node.node_tag == "css":
                css_text = str(node.value) if node.value else ""
                if css_text:
                    css_parts.append(css_text)
            elif node.node_tag == "binding":
                key = node.attr.get("key", "")
                action = node.attr.get("action", "")
                description = node.attr.get("description", "")
                if key and action:
                    live_app.bind(key, action, description=description)
            else:
                self._render_node(node, live_app.root)

        if css_parts:
            live_app.stylesheet.add_source("\n".join(css_parts))
            live_app.stylesheet.reparse()
            live_app.stylesheet.apply(live_app)

    def _render_node(self, node: BagNode, parent_widget: Widget) -> None:
        """Render a single node: dispatch by tag, then recurse children."""
        tag = node.node_tag or "static"

        render_method = getattr(self, f"_render_{tag}", None)
        if render_method:
            render_method(node, parent_widget)
            return

        self._render_default(node, parent_widget)

    def _render_default(self, node: BagNode, parent_widget: Widget) -> None:
        """Generic rendering: import class from compile_kwargs, create, mount.

        If the node has no compile_class (e.g. a materialized component),
        its children are rendered directly into the parent — the component
        node itself is transparent after expansion.
        """
        tag = node.node_tag or "static"
        attr = dict(node.attr)

        try:
            schema_info = self.builder._get_schema_info(tag)
        except KeyError:
            schema_info = {}
        compile_kwargs = schema_info.get("compile_kwargs", {})
        class_name = compile_kwargs.get("class")

        if class_name is None:
            # No widget class: transparent container (e.g. materialized component).
            # Render children directly into parent.
            if isinstance(node.value, Bag):
                for child_node in node.value:
                    self._render_node(child_node, parent_widget)
            return

        module_name = compile_kwargs.get("module", "textual.widgets")
        module = import_module(module_name)
        textual_class = getattr(module, class_name)

        kwargs = self._filter_kwargs_for_signature(attr, textual_class.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"{tag}_{self.widget_counter}"

        if isinstance(node.value, Bag):
            content = ""
        else:
            content = str(node.value) if node.value else ""

        first_param = self._first_positional_param(textual_class.__init__)
        if content and first_param and first_param not in kwargs:
            kwargs[first_param] = content

        widget = textual_class(**kwargs)
        self._mount(node, widget, parent_widget)

        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._render_node(child_node, widget)

    # -------------------------------------------------------------------------
    # Special renderers
    # -------------------------------------------------------------------------

    def _render_static(self, node: BagNode, parent_widget: Widget) -> None:
        """Static text widget."""
        from textual.widgets import Static

        content = str(node.value) if node.value else ""
        attr = {k: v for k, v in node.attr.items() if not k.startswith("_")}

        if "id" not in attr:
            attr["id"] = f"static_{self.widget_counter}"

        widget = Static(content, **attr)
        self._mount(node, widget, parent_widget)

    def _render_tabbedcontent(self, node: BagNode, parent_widget: Widget) -> None:
        """TabbedContent: children go via add_pane(), not mount()."""
        from textual.widgets import TabbedContent

        attr = dict(node.attr)
        kwargs = self._filter_kwargs_for_signature(attr, TabbedContent.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"tabbedcontent_{self.widget_counter}"

        widget = TabbedContent(**kwargs)
        self._mount(node, widget, parent_widget)

        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._render_tabpane(child_node, widget)

    def _render_tabpane(self, node: BagNode, tabbed_content: Widget) -> None:
        """TabPane added to TabbedContent via add_pane()."""
        from textual.widgets import TabPane

        attr = dict(node.attr)
        title = attr.pop("title", None) or "Untitled"
        kwargs = self._filter_kwargs_for_signature(attr, TabPane.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"tabpane_{self.widget_counter}"

        widget = TabPane(title, **kwargs)
        node.compiled["widget"] = widget
        tabbed_content.add_pane(widget)

        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._render_node(child_node, widget)

    def _render_datatable(self, node: BagNode, parent_widget: Widget) -> None:
        """DataTable: columns and rows via add_column/add_row."""
        from textual.widgets import DataTable

        attr = dict(node.attr)
        kwargs = self._filter_kwargs_for_signature(attr, DataTable.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"datatable_{self.widget_counter}"

        widget = DataTable(**kwargs)
        self._mount(node, widget, parent_widget)

        if not isinstance(node.value, Bag):
            return

        columns = []
        rows = []
        for child_node in node.value:
            if child_node.node_tag == "column":
                columns.append(child_node)
            elif child_node.node_tag == "row":
                rows.append(child_node)

        for col_node in columns:
            col_attr = dict(col_node.attr)
            label = col_attr.get("label", str(col_node.value) if col_node.value else "")
            col_kwargs = self._filter_kwargs_for_signature(col_attr, widget.add_column)
            widget.add_column(label, **col_kwargs)

        for row_node in rows:
            row_attr = dict(row_node.attr)
            if isinstance(row_node.value, (list, tuple)):
                cells = row_node.value
            elif isinstance(row_node.value, Bag):
                cells = [str(c.value) for c in row_node.value]
            else:
                cells = [str(row_node.value)] if row_node.value else []
            row_kwargs = self._filter_kwargs_for_signature(row_attr, widget.add_row)
            widget.add_row(*cells, **row_kwargs)

    # -------------------------------------------------------------------------
    # Mount helper
    # -------------------------------------------------------------------------

    def _mount(self, node: BagNode, widget: Widget, parent_widget: Widget) -> None:
        """Mount widget to parent and store bidirectional references."""
        node.compiled["widget"] = widget
        widget._bag_node = node  # type: ignore[attr-defined]
        parent_widget.mount(widget)

    # -------------------------------------------------------------------------
    # Signature introspection
    # -------------------------------------------------------------------------

    def _filter_kwargs_for_signature(
        self, attr: dict[str, Any], method: Any
    ) -> dict[str, Any]:
        """Filter attr dict to only keys accepted by method signature."""
        sig = inspect.signature(method)
        valid_params = set(sig.parameters.keys()) - {"self"}
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        )
        kwargs = {}
        for key, value in attr.items():
            if key.startswith("_"):
                continue
            if has_var_keyword or key in valid_params:
                kwargs[key] = value
        return kwargs

    def _first_positional_param(self, method: Any) -> str | None:
        """Get the name of the first positional parameter (after self)."""
        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        if len(params) > 1:
            first_param = params[1]
            if first_param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            ):
                return first_param.name
        return None
