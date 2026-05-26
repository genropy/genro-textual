# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualRenderer - mount Textual widgets from a source bag.

Renderer for the ``"textual"`` mode on TextualBuilder. Side-effect-only:
walks the source bag and mounts widgets on a LiveApp target, returns
None. Aligned with genro-builders v0.4.0 RendererBase contract.

Dispatch:
    1. ``_render_<tag>`` method for special widgets (static, tree,
       datatable, tabbedcontent, tabpane);
    2. ``_render_default`` for the rest, reading the Textual class to
       instantiate from each element's ``_meta`` (compile_module +
       compile_class).

Each rendered node stores back-reference ``widget._bag_node = node`` so
that Textual event handlers on the LiveApp can identify the source node
that produced a widget.
"""
from __future__ import annotations

import inspect
from importlib import import_module
from typing import Any

from genro_bag import Bag, BagNode
from genro_builders.renderer import RendererBase
from textual.css.styles import RulesMap
from textual.reactive import Reactive
from textual.widget import Widget

_CSS_PROPERTIES = set(RulesMap.__annotations__.keys())


class TextualRenderer(RendererBase):
    """Renderer for the Textual dialect: source bag -> mounted widgets."""

    def __init__(self, handler: Any, builder: Any = None) -> None:
        super().__init__(handler, builder)
        self._widget_counter = 0

    @property
    def widget_counter(self) -> int:
        """Return current counter and auto-increment."""
        current = self._widget_counter
        self._widget_counter += 1
        return current

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def render_textual(
        self,
        source: Bag,
        render_target: Any = None,
        **_kwargs: Any,
    ) -> None:
        """Mount widgets from source onto render_target (a LiveApp).

        Walks the source bag in three phases:
            1. extract ``css`` and ``binding`` nodes recursively;
            2. mount remaining nodes as widgets under ``render_target.root``;
            3. apply collected CSS on the LiveApp stylesheet.

        Returns None: side-effect-only on the live target.
        """
        if render_target is None:
            return None
        css_parts: list[str] = []
        self._extract_config(source, css_parts, render_target)
        for node in source:
            self._mount_widget(node, render_target.root)
        if css_parts:
            render_target.stylesheet.add_source("\n".join(css_parts))
            render_target.stylesheet.reparse()
            render_target.stylesheet.apply(render_target)
        return None

    # ------------------------------------------------------------------
    # Config extraction (css, binding) — recursive
    # ------------------------------------------------------------------

    def _extract_config(
        self, bag: Bag, css_parts: list[str], target: Any,
    ) -> None:
        """Recursively extract css and binding nodes from the source tree."""
        for node in bag:
            tag = node.node_tag or ""
            if tag == "css":
                css_text = node.value
                if css_text:
                    css_parts.append(css_text)
            elif tag == "binding":
                attrs = dict(node.attr)
                key = attrs.get("key", "")
                action = attrs.get("action", "")
                description = attrs.get("description", "")
                if key and action:
                    target.bind(key, action, description=description)
            elif isinstance(node.value, Bag):
                self._extract_config(node.value, css_parts, target)

    # ------------------------------------------------------------------
    # Node rendering dispatch
    # ------------------------------------------------------------------

    def _mount_widget(self, node: BagNode, parent_widget: Widget) -> None:
        """Create the Textual widget for ``node`` and mount it on parent.

        Dispatch by tag (``_mount_widget_<tag>`` for special widgets,
        ``_mount_widget_default`` otherwise), then recurse on children.
        Skips css and binding nodes — extracted by ``_extract_config``
        and applied to the LiveApp.
        """
        tag = node.node_tag or "static"
        if tag in ("css", "binding"):
            return
        mount_method = getattr(self, f"_mount_widget_{tag}", None)
        if mount_method:
            mount_method(node, parent_widget)
            return
        self._mount_widget_default(node, parent_widget)

    def _mount_widget_default(
        self, node: BagNode, parent_widget: Widget,
    ) -> None:
        """Generic case: read class from ``_meta``, instantiate, mount."""
        tag = node.node_tag or "static"
        meta = self._get_meta(tag)
        class_name = meta.get("compile_class")
        if class_name is None:
            return
        module_name = meta.get("compile_module", "textual.widgets")
        module = import_module(module_name)
        textual_class = getattr(module, class_name)

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        init_kwargs, style_attrs, reactive_attrs = self._classify_attrs(
            attrs, textual_class,
        )
        if "id" not in init_kwargs:
            init_kwargs["id"] = f"{tag}_{self.widget_counter}"

        has_children = isinstance(node.value, Bag)
        content = "" if has_children else (node.value or "")
        first_param = self._first_positional_param(textual_class.__init__)
        if content and first_param and first_param not in init_kwargs:
            init_kwargs[first_param] = content

        widget = textual_class(**init_kwargs)
        self._apply_styles(widget, style_attrs)
        self._apply_reactive(widget, reactive_attrs)
        self._attach_widget(node, widget, parent_widget)

        if has_children:
            for child_node in node.value:
                self._mount_widget(child_node, widget)

    # ------------------------------------------------------------------
    # Special renderers
    # ------------------------------------------------------------------

    def _mount_widget_static(
        self, node: BagNode, parent_widget: Widget,
    ) -> None:
        """Static text widget."""
        from textual.widgets import Static

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        content = node.value or ""
        if "id" not in attrs:
            attrs["id"] = f"static_{self.widget_counter}"
        widget = Static(content, **attrs)
        self._attach_widget(node, widget, parent_widget)

    def _mount_widget_tabbedcontent(
        self, node: BagNode, parent_widget: Widget,
    ) -> None:
        """TabbedContent: children go via add_pane(), not mount()."""
        from textual.widgets import TabbedContent

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        initial = attrs.pop("initial", "")
        kwargs = self._filter_kwargs_for_signature(attrs, TabbedContent.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tabbedcontent_{self.widget_counter}"
        widget = TabbedContent(**kwargs)
        self._attach_widget(node, widget, parent_widget)

        first_pane_id: str | None = None
        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._mount_widget_tabpane(child_node, widget)
                if first_pane_id is None:
                    w = getattr(child_node, "_textual_widget", None)
                    first_pane_id = w.id if w else None

        target_id = initial or first_pane_id
        if target_id:
            widget.call_after_refresh(setattr, widget, "active", target_id)

    def _mount_widget_tabpane(
        self, node: BagNode, tabbed_content: Any,
    ) -> None:
        """TabPane added to TabbedContent via add_pane()."""
        from textual.widgets import TabPane

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        title = attrs.pop("title", None) or "Untitled"
        kwargs = self._filter_kwargs_for_signature(attrs, TabPane.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tabpane_{self.widget_counter}"
        widget = TabPane(title, **kwargs)
        # Stash the widget on the node so the parent TabbedContent can
        # read it back to compute the initial active pane.
        node._textual_widget = widget  # type: ignore[attr-defined]
        widget._bag_node = node  # type: ignore[attr-defined]
        tabbed_content.add_pane(widget)

        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._mount_widget(child_node, widget)

    def _mount_widget_tree(
        self, node: BagNode, parent_widget: Widget,
    ) -> None:
        """Tree widget: optionally populated from a Bag passed via ``store``."""
        from textual.widgets import Tree

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        store = attrs.pop("store", None)
        label = attrs.pop("label", None) or "Tree"
        kwargs = self._filter_kwargs_for_signature(attrs, Tree.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tree_{self.widget_counter}"
        widget = Tree(label, **kwargs)
        self._attach_widget(node, widget, parent_widget)
        if isinstance(store, Bag):
            self._populate_tree_from_bag(widget.root, store)
            widget.set_timer(0.1, widget.refresh)

    def _populate_tree_from_bag(self, tree_node: Any, bag: Bag) -> None:
        """Recursively populate a TreeNode from a Bag."""
        for bag_node in bag:
            label = bag_node.label
            value = (
                bag_node.static_value
                if hasattr(bag_node, "static_value")
                else bag_node.value
            )
            if isinstance(value, Bag):
                child = tree_node.add(f"{label}", data=bag_node)
                self._populate_tree_from_bag(child, value)
            else:
                display = f"{label}: {value}" if value is not None else label
                tree_node.add_leaf(display, data=bag_node)

    def _mount_widget_datatable(
        self, node: BagNode, parent_widget: Widget,
    ) -> None:
        """DataTable: columns and rows via add_column/add_row."""
        from textual.widgets import DataTable

        attrs = {k: v for k, v in node.attr.items() if not k.startswith("_")}
        kwargs = self._filter_kwargs_for_signature(attrs, DataTable.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"datatable_{self.widget_counter}"
        widget = DataTable(**kwargs)
        self._attach_widget(node, widget, parent_widget)

        if not isinstance(node.value, Bag):
            return
        for child_node in node.value:
            child_attrs = {
                k: v for k, v in child_node.attr.items()
                if not k.startswith("_")
            }
            if child_node.node_tag == "column":
                label = child_attrs.get("label", child_node.value or "")
                col_kwargs = self._filter_kwargs_for_signature(
                    child_attrs, widget.add_column,
                )
                widget.add_column(label, **col_kwargs)
            elif child_node.node_tag == "row":
                raw_value = child_node.value
                if isinstance(raw_value, (list, tuple)):
                    cells = list(raw_value)
                elif isinstance(raw_value, Bag):
                    cells = [str(c.value) for c in raw_value]
                else:
                    cells = [str(raw_value)] if raw_value else []
                row_kwargs = self._filter_kwargs_for_signature(
                    child_attrs, widget.add_row,
                )
                widget.add_row(*cells, **row_kwargs)

    # ------------------------------------------------------------------
    # Attach to the live tree
    # ------------------------------------------------------------------

    def _attach_widget(
        self, node: BagNode, widget: Widget, parent_widget: Widget,
    ) -> None:
        """Mount widget on parent; keep back-reference widget -> node."""
        widget._bag_node = node  # type: ignore[attr-defined]
        parent_widget.mount(widget)

    # ------------------------------------------------------------------
    # Schema / meta helpers
    # ------------------------------------------------------------------

    def _get_meta(self, tag: str) -> dict[str, Any]:
        """Read the ``_meta`` dict declared on an element via @element."""
        try:
            schema_info = self.builder._get_schema_info(tag)
        except KeyError:
            return {}
        return schema_info.get("_meta") or {}

    # ------------------------------------------------------------------
    # Attribute classification and application
    # ------------------------------------------------------------------

    def _classify_attrs(
        self, attrs: dict[str, Any], textual_class: type,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Classify node attributes into constructor args, CSS styles, reactive attrs."""
        init_kwargs: dict[str, Any] = {}
        style_attrs: dict[str, Any] = {}
        reactive_attrs: dict[str, Any] = {}
        init_params = self._get_init_params(textual_class)
        has_var_keyword = self._has_var_keyword(textual_class)
        for key, value in attrs.items():
            if key in init_params:
                init_kwargs[key] = value
            elif key in _CSS_PROPERTIES:
                style_attrs[key] = value
            elif isinstance(getattr(textual_class, key, None), Reactive):
                reactive_attrs[key] = value
            elif has_var_keyword:
                init_kwargs[key] = value
        return init_kwargs, style_attrs, reactive_attrs

    def _apply_styles(
        self, widget: Widget, style_attrs: dict[str, Any],
    ) -> None:
        """Apply CSS style attributes to widget.styles."""
        for key, value in style_attrs.items():
            setattr(widget.styles, key, value)

    def _apply_reactive(
        self, widget: Widget, reactive_attrs: dict[str, Any],
    ) -> None:
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
        return any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )

    # ------------------------------------------------------------------
    # Signature introspection
    # ------------------------------------------------------------------

    def _filter_kwargs_for_signature(
        self, attrs: dict[str, Any], method: Any,
    ) -> dict[str, Any]:
        """Filter attr dict to only keys accepted by method signature."""
        sig = inspect.signature(method)
        valid_params = set(sig.parameters.keys()) - {"self"}
        has_var_keyword = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        kwargs: dict[str, Any] = {}
        for key, value in attrs.items():
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
