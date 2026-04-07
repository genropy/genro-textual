# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualCompiler - Compiler that turns built Bag into Textual widgets.

Inherits from BagCompilerBase: provides _build_context() for just-in-time
^pointer resolution. The built Bag retains ^pointer strings; resolution
happens here at widget creation time.

Rendering dispatch:
    1. _render_<tag> method on this class (for special widgets)
    2. _render_default: generic rendering via _meta (module + class)

Each rendered node stores its widget in node.compiled["widget"] so the
BindingManager can later update it on data changes. Each widget stores
widget._bag_node back to the built node (bidirectional link).
"""

from __future__ import annotations

import inspect
from importlib import import_module
from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.compiler import BagCompilerBase
from textual.css.styles import RulesMap
from textual.reactive import Reactive
from textual.widget import Widget

_CSS_PROPERTIES = set(RulesMap.__annotations__.keys())


class TextualCompiler(BagCompilerBase):
    """Compiler for Textual: built Bag -> Widget tree."""

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
    # Main entry point: compile built Bag into widgets
    # -------------------------------------------------------------------------

    def compile(self, built_bag: Bag, target: Any = None) -> None:
        """Walk the built Bag, extract app config, mount widgets.

        Nodes tagged 'css' and 'binding' are app configuration —
        applied to the live_app (target), not rendered as widgets.
        All other nodes are rendered recursively into target.root.

        Args:
            built_bag: The built Bag with pointer formali.
            target: The LiveApp instance to mount widgets into.
        """
        if target is None:
            return

        # Phase 1: Extract CSS and bindings from entire built tree (recursive)
        css_parts: list[str] = []
        self._extract_config(built_bag, css_parts, target)

        # Phase 2: Render widgets (css/binding skipped by _render_node)
        for node in built_bag:
            self._render_node(node, target.root)

        # Phase 3: Apply collected CSS
        if css_parts:
            target.stylesheet.add_source("\n".join(css_parts))
            target.stylesheet.reparse()
            target.stylesheet.apply(target)

    # -------------------------------------------------------------------------
    # Config extraction (css, binding) — recursive through transparent nodes
    # -------------------------------------------------------------------------

    def _extract_config(self, bag: Bag, css_parts: list[str], target: Any) -> None:
        """Recursively extract css and binding nodes from the built tree."""
        for node in bag:
            tag = node.node_tag or ""
            if tag == "css":
                ctx = self._build_context(node)
                css_text = ctx["node_value"]
                if css_text:
                    css_parts.append(css_text)
            elif tag == "binding":
                ctx = self._build_context(node)
                key = ctx.get("key", "")
                action = ctx.get("action", "")
                description = ctx.get("description", "")
                if key and action:
                    target.bind(key, action, description=description)
            elif isinstance(node.value, Bag):
                self._extract_config(node.value, css_parts, target)

    # -------------------------------------------------------------------------
    # Node rendering dispatch
    # -------------------------------------------------------------------------

    def _render_node(self, node: BagNode, parent_widget: Widget) -> None:
        """Render a single node: dispatch by tag, then recurse children.

        Skips css and binding nodes — those are extracted separately
        by compile() and applied to the LiveApp, not rendered as widgets.
        """
        tag = node.node_tag or "static"

        if tag in ("css", "binding"):
            return

        render_method = getattr(self, f"_render_{tag}", None)
        if render_method:
            render_method(node, parent_widget)
            return

        self._render_default(node, parent_widget)

    def _render_default(self, node: BagNode, parent_widget: Widget) -> None:
        """Generic rendering: import class from _meta, create, mount.

        If the node has no compile_class (e.g. a materialized component),
        its children are rendered directly into the parent — the component
        node itself is transparent after expansion.
        """
        tag = node.node_tag or "static"

        try:
            schema_info = self.builder._get_schema_info(tag)
        except KeyError:
            schema_info = {}
        meta = schema_info.get("_meta") or {}
        class_name = meta.get("compile_class")

        if class_name is None:
            # No widget class: transparent container (e.g. materialized component).
            # Render children directly into parent.
            if isinstance(node.value, Bag):
                for child_node in node.value:
                    self._render_node(child_node, parent_widget)
            return

        module_name = meta.get("compile_module", "textual.widgets")
        module = import_module(module_name)
        textual_class = getattr(module, class_name)

        # Resolve pointer formali just-in-time
        ctx = self._build_context(node)
        resolved_value = ctx["node_value"]
        resolved_attrs = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children")
        }

        # Separate attributes into constructor args, CSS styles, reactive attrs
        init_kwargs, style_attrs, reactive_attrs = self._classify_attrs(
            resolved_attrs, textual_class
        )

        if "id" not in init_kwargs:
            init_kwargs["id"] = f"{tag}_{self.widget_counter}"

        has_children = isinstance(node.value, Bag)
        content = "" if has_children else (resolved_value or "")

        first_param = self._first_positional_param(textual_class.__init__)
        if content and first_param and first_param not in init_kwargs:
            init_kwargs[first_param] = content

        widget = textual_class(**init_kwargs)
        self._apply_styles(widget, style_attrs)
        self._apply_reactive(widget, reactive_attrs)
        self._mount(node, widget, parent_widget)

        if has_children:
            for child_node in node.value:
                self._render_node(child_node, widget)

    # -------------------------------------------------------------------------
    # Special renderers
    # -------------------------------------------------------------------------

    def _render_static(self, node: BagNode, parent_widget: Widget) -> None:
        """Static text widget."""
        from textual.widgets import Static

        ctx = self._build_context(node)
        content = ctx["node_value"] or ""
        attr = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children") and not k.startswith("_")
        }

        if "id" not in attr:
            attr["id"] = f"static_{self.widget_counter}"

        widget = Static(content, **attr)
        self._mount(node, widget, parent_widget)

    def _render_tabbedcontent(self, node: BagNode, parent_widget: Widget) -> None:
        """TabbedContent: children go via add_pane(), not mount()."""
        from textual.widgets import TabbedContent

        ctx = self._build_context(node)
        attr = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children")
        }
        initial = attr.pop("initial", "")
        kwargs = self._filter_kwargs_for_signature(attr, TabbedContent.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"tabbedcontent_{self.widget_counter}"

        widget = TabbedContent(**kwargs)
        self._mount(node, widget, parent_widget)

        first_pane_id = None
        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._render_tabpane(child_node, widget)
                if first_pane_id is None:
                    w = child_node.compiled.get("widget")
                    first_pane_id = w.id if w else None

        target_id = initial or first_pane_id
        if target_id:
            widget.call_after_refresh(setattr, widget, "active", target_id)

    def _render_tabpane(self, node: BagNode, tabbed_content: Widget) -> None:
        """TabPane added to TabbedContent via add_pane()."""
        from textual.widgets import TabPane

        ctx = self._build_context(node)
        attr = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children")
        }
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

    def _render_tree(self, node: BagNode, parent_widget: Widget) -> None:
        """Tree widget: populate from store attribute if it's a Bag."""
        from textual.widgets import Tree

        ctx = self._build_context(node)
        attr = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children")
        }
        store = attr.pop("store", None)
        label = attr.pop("label", None) or "Tree"
        kwargs = self._filter_kwargs_for_signature(attr, Tree.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"tree_{self.widget_counter}"

        widget = Tree(label, **kwargs)
        self._mount(node, widget, parent_widget)

        if isinstance(store, Bag):
            self._populate_tree_from_bag(widget.root, store)
            widget.set_timer(0.1, widget.refresh)

    def _populate_tree_from_bag(self, tree_node: Any, bag: Bag) -> None:
        """Recursively populate a TreeNode from a Bag."""
        for bag_node in bag:
            label = bag_node.label
            value = bag_node.static_value if hasattr(bag_node, "static_value") else bag_node.value
            if isinstance(value, Bag):
                child = tree_node.add(f"{label}", data=bag_node)
                self._populate_tree_from_bag(child, value)
            else:
                display = f"{label}: {value}" if value is not None else label
                tree_node.add_leaf(display, data=bag_node)

    def _render_datatable(self, node: BagNode, parent_widget: Widget) -> None:
        """DataTable: columns and rows via add_column/add_row."""
        from textual.widgets import DataTable

        ctx = self._build_context(node)
        attr = {
            k: v
            for k, v in ctx.items()
            if k not in ("node_value", "node_label", "_node", "children")
        }
        kwargs = self._filter_kwargs_for_signature(attr, DataTable.__init__)

        if "id" not in kwargs:
            kwargs["id"] = f"datatable_{self.widget_counter}"

        widget = DataTable(**kwargs)
        self._mount(node, widget, parent_widget)

        if not isinstance(node.value, Bag):
            return

        for child_node in node.value:
            if child_node.node_tag == "column":
                col_ctx = self._build_context(child_node)
                col_attr = {
                    k: v
                    for k, v in col_ctx.items()
                    if k not in ("node_value", "node_label", "_node", "children")
                }
                label = col_attr.get("label", col_ctx["node_value"] or "")
                col_kwargs = self._filter_kwargs_for_signature(col_attr, widget.add_column)
                widget.add_column(label, **col_kwargs)
            elif child_node.node_tag == "row":
                row_ctx = self._build_context(child_node)
                row_attr = {
                    k: v
                    for k, v in row_ctx.items()
                    if k not in ("node_value", "node_label", "_node", "children")
                }
                raw_value = child_node.value
                if isinstance(raw_value, (list, tuple)):
                    cells = raw_value
                elif isinstance(raw_value, Bag):
                    cells = [str(c.value) for c in raw_value]
                else:
                    cells = [str(raw_value)] if raw_value else []
                row_kwargs = self._filter_kwargs_for_signature(row_attr, widget.add_row)
                widget.add_row(*cells, **row_kwargs)

    # -------------------------------------------------------------------------
    # Mount and link
    # -------------------------------------------------------------------------

    def _mount(self, node: BagNode, widget: Widget, parent_widget: Widget) -> None:
        """Mount widget to parent, store bidirectional node <-> widget link."""
        node.compiled["widget"] = widget
        widget._bag_node = node  # type: ignore[attr-defined]

        # If the node has a store attribute (a Bag), subscribe for reactive updates
        store = node.attr.get("store")
        if isinstance(store, Bag):
            from genro_textual.debug import log

            widget._store = store  # type: ignore[attr-defined]
            subscriber_id = f"store_{widget.id or id(widget)}"
            store.subscribe(subscriber_id, any=lambda **kw: self._on_store_changed(widget, store))
            log(f"_mount: subscribed {subscriber_id} on {widget.id}")

        parent_widget.mount(widget)

    def _on_store_changed(self, widget: Widget, store: Bag) -> None:
        """Called when a store Bag changes. Repopulate preserving expanded state."""
        from textual.widgets import Tree

        if isinstance(widget, Tree):
            expanded_paths = self._collect_expanded_paths(widget.root, "")
            widget.clear()
            self._populate_tree_from_bag(widget.root, store)
            self._restore_expanded_paths(widget.root, "", expanded_paths)
            widget.set_timer(0.1, widget.refresh)

    def _collect_expanded_paths(self, tree_node: Any, prefix: str) -> set[str]:
        """Collect paths of expanded tree nodes."""
        expanded = set()
        for child in tree_node.children:
            path = f"{prefix}.{child.label}" if prefix else str(child.label)
            if child.is_expanded:
                expanded.add(path)
                expanded.update(self._collect_expanded_paths(child, path))
        return expanded

    def _restore_expanded_paths(self, tree_node: Any, prefix: str, expanded: set[str]) -> None:
        """Restore expanded state on tree nodes matching saved paths."""
        for child in tree_node.children:
            path = f"{prefix}.{child.label}" if prefix else str(child.label)
            if path in expanded:
                child.expand()
                self._restore_expanded_paths(child, path, expanded)

    # -------------------------------------------------------------------------
    # Attribute classification and application
    # -------------------------------------------------------------------------

    def _classify_attrs(
        self, attr: dict[str, Any], textual_class: type
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Classify node attributes into constructor args, CSS styles, reactive attrs."""
        init_kwargs: dict[str, Any] = {}
        style_attrs: dict[str, Any] = {}
        reactive_attrs: dict[str, Any] = {}

        init_params = self._get_init_params(textual_class)

        for key, value in attr.items():
            if key.startswith("_"):
                continue
            if key in init_params:
                init_kwargs[key] = value
            elif key in _CSS_PROPERTIES:
                style_attrs[key] = value
            elif isinstance(getattr(textual_class, key, None), Reactive):
                reactive_attrs[key] = value
            else:
                if self._has_var_keyword(textual_class):
                    init_kwargs[key] = value

        return init_kwargs, style_attrs, reactive_attrs

    def _apply_styles(self, widget: Widget, style_attrs: dict[str, Any]) -> None:
        """Apply CSS style attributes to widget.styles."""
        for key, value in style_attrs.items():
            setattr(widget.styles, key, value)

    def _apply_reactive(self, widget: Widget, reactive_attrs: dict[str, Any]) -> None:
        """Apply reactive attributes to the widget without triggering watchers."""
        for key, value in reactive_attrs.items():
            descriptor = getattr(type(widget), key, None)
            if isinstance(descriptor, Reactive):
                widget.set_reactive(descriptor, value)

    def _get_init_params(self, textual_class: type) -> set[str]:
        """Get the set of parameter names accepted by __init__."""
        sig = inspect.signature(textual_class.__init__)
        return set(sig.parameters.keys()) - {"self"}

    def _has_var_keyword(self, textual_class: type) -> bool:
        """Check if __init__ accepts **kwargs."""
        sig = inspect.signature(textual_class.__init__)
        return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

    # -------------------------------------------------------------------------
    # Signature introspection
    # -------------------------------------------------------------------------

    def _filter_kwargs_for_signature(self, attr: dict[str, Any], method: Any) -> dict[str, Any]:
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
