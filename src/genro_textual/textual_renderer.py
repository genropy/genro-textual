# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualRenderer - build Textual widgets from a source bag.

Renderer for the ``"textual"`` mode on TextualBuilder. Object dialect
(``render_type = "object"``): the universal walk of ``RendererBase``
produces a live Textual ``Widget`` per node and ``finalize`` mounts the
top-level widgets on a LiveApp target.

Strategy: the walk is bottom-up. ``render`` → ``render_children``
renders the children first, so when ``rendered_item(node, item, ...)``
runs, ``item`` already holds the children widgets — they are passed as
``*children`` to the widget constructor. This satisfies textual's
constraint (children go through the constructor, not mounted after) and
avoids races where ``add_pane``/``mount`` hits a container whose compose
has not yet run (TabbedContent is the typical case).

``rendered_item`` dispatches by tag (``_rendered_<tag>`` for special
widgets: static, tree, datatable, tabbedcontent, tabpane) and a generic
branch for the rest, reading the Textual class from the node's ``_meta``
(compile_module + compile_class). ``css``/``binding`` nodes are
transparent (return None); a pre-scan in ``finalize`` applies them.

Each built widget stores back-reference ``widget._bag_node = node`` so
that Textual event handlers on the LiveApp can identify the source
node that produced a widget.
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

    mode = "textual"
    render_type = "object"

    def __init__(self, builder: Any, handler: Any = None) -> None:
        super().__init__(builder, handler)
        # Auto-id counter. Lives on the renderer (ephemeral, one per
        # render). Stable ids across renders belong to a later step
        # (Doc B, node<->widget binding) — not here.
        self._widget_counter = 0

    @property
    def widget_counter(self) -> int:
        """Return current counter and auto-increment."""
        current = self._widget_counter
        self._widget_counter += 1
        return current

    # ------------------------------------------------------------------
    # Walk hook: per-node fragment (a Textual widget)
    # ------------------------------------------------------------------

    def rendered_item(
        self,
        node: Any,
        item: Any,
        runtime_attrs: dict[str, Any],
        *,
        tag: str,
        **_opts: Any,
    ) -> Widget | None:
        """Build the Textual widget for ``node``.

        ``item`` already holds the children widgets (the walk is
        bottom-up) when ``node.value`` is a Bag; otherwise it is the leaf
        value or None. Dispatch by tag: ``_rendered_<tag>`` for special
        widgets, a generic branch otherwise. ``css``/``binding`` nodes
        are transparent (return None) — applied by ``finalize``.
        """
        if tag in ("css", "binding"):
            return None
        children = item if isinstance(item, list) else []
        builder = getattr(self, f"_rendered_{tag}", None)
        if builder is not None:
            return builder(node, children, runtime_attrs)
        return self._rendered_default(node, children, runtime_attrs, tag)

    def _rendered_default(
        self,
        node: Any,
        children: list[Widget],
        runtime_attrs: dict[str, Any],
        tag: str,
    ) -> Widget | None:
        """Generic case: read class from the node ``_meta``, instantiate.

        If the widget class accepts ``*children`` (a container), the
        already-built children widgets are passed as positional args to
        the constructor. Otherwise the node value is used as the first
        positional arg (leaf widgets like Static, Button).
        """
        module_name, class_name = node._get_meta(
            "compile_module,compile_class",
        )
        if class_name is None:
            return None
        module = import_module(module_name or "textual.widgets")
        textual_class = getattr(module, class_name)

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        init_kwargs, style_attrs, reactive_attrs = self._classify_attrs(
            attrs, textual_class,
        )
        if "id" not in init_kwargs:
            init_kwargs["id"] = f"{tag}_{self.widget_counter}"

        accepts_children = self._accepts_var_positional(textual_class)
        if accepts_children:
            widget = textual_class(*children, **init_kwargs)
        else:
            # Leaf widget: use node.value as the first positional arg.
            content = "" if isinstance(node.value, Bag) else (node.value or "")
            first_param = self._first_positional_param(textual_class.__init__)
            if content and first_param and first_param not in init_kwargs:
                init_kwargs[first_param] = content
            widget = textual_class(**init_kwargs)

        self._apply_styles(widget, style_attrs)
        self._apply_reactive(widget, reactive_attrs)
        widget._bag_node = node  # type: ignore[attr-defined]
        return widget

    # ------------------------------------------------------------------
    # Compose final result: mount widgets, apply css/binding
    # ------------------------------------------------------------------

    def finalize(self, result: Any, target: Any, **_opts: Any) -> None:
        """Mount the rendered widgets on the live target.

        ``result`` is the list of top-level widgets (full render) or a
        single widget (partial render). ``target`` is a LiveApp. No
        string join — object dialect. CSS/binding are pre-scanned from
        the source and applied here.
        """
        if target is None:
            return None
        widgets = result if isinstance(result, list) else [result]
        css_parts: list[str] = []
        self._extract_config(self.handler.source, css_parts, target)
        for widget in widgets:
            if widget is not None:
                target.root.mount(widget)
        if css_parts:
            target.stylesheet.add_source("\n".join(css_parts))
            target.stylesheet.reparse()
            target.stylesheet.apply(target)
        return None

    # ------------------------------------------------------------------
    # Config extraction (css, binding) — recursive pre-scan
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
    # Special builders (children already built, passed in)
    # ------------------------------------------------------------------

    def _rendered_static(
        self, node: Any, children: list[Widget], runtime_attrs: dict[str, Any],
    ) -> Widget:
        """Static text widget (leaf)."""
        from textual.widgets import Static

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        content = node.value or ""
        if "id" not in attrs:
            attrs["id"] = f"static_{self.widget_counter}"
        widget = Static(content, **attrs)
        widget._bag_node = node  # type: ignore[attr-defined]
        return widget

    def _rendered_tabbedcontent(
        self, node: Any, children: list[Widget], runtime_attrs: dict[str, Any],
    ) -> Widget:
        """TabbedContent populated via compose_add_child (the same hook
        Textual's own ``with TabbedContent(): yield ...`` syntax uses).

        TabbedContent's constructor expects string titles, not TabPane
        widgets. The idiomatic way to register the already-built TabPane
        children before mount is via ``compose_add_child`` — the same
        hook Textual invokes when the context-manager syntax yields a
        child.
        """
        from textual.widgets import TabbedContent

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        initial = attrs.pop("initial", "")
        kwargs = self._filter_kwargs_for_signature(attrs, TabbedContent.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tabbedcontent_{self.widget_counter}"

        widget = TabbedContent(**kwargs)
        widget._bag_node = node  # type: ignore[attr-defined]

        for pane in children:
            widget.compose_add_child(pane)

        first_pane_id = children[0].id if children else None
        target_id = initial or first_pane_id
        if target_id:
            widget.call_after_refresh(setattr, widget, "active", target_id)
        return widget

    def _rendered_tabpane(
        self, node: Any, children: list[Widget], runtime_attrs: dict[str, Any],
    ) -> Widget:
        """TabPane built with its already-rendered children as compose args."""
        from textual.widgets import TabPane

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        title = attrs.pop("title", None) or "Untitled"
        kwargs = self._filter_kwargs_for_signature(attrs, TabPane.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tabpane_{self.widget_counter}"
        widget = TabPane(title, *children, **kwargs)
        widget._bag_node = node  # type: ignore[attr-defined]
        return widget

    def _rendered_tree(
        self, node: Any, children: list[Widget], runtime_attrs: dict[str, Any],
    ) -> Widget:
        """Tree widget: optionally populated from a Bag passed via ``store``."""
        from textual.widgets import Tree

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        store = attrs.pop("store", None)
        label = attrs.pop("label", None) or "Tree"
        kwargs = self._filter_kwargs_for_signature(attrs, Tree.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"tree_{self.widget_counter}"
        widget = Tree(label, **kwargs)
        widget._bag_node = node  # type: ignore[attr-defined]
        if isinstance(store, Bag):
            # Tree population must happen after the Tree is mounted (its
            # root TreeNode is only valid then). Defer via
            # call_after_refresh — Textual's idiomatic post-mount hook.
            widget.call_after_refresh(
                lambda w=widget, s=store: self._populate_tree(w, s),
            )
        return widget

    def _populate_tree(self, widget: Any, store: Bag) -> None:
        """Populate a Tree widget from a Bag (called post-mount)."""
        self._populate_tree_from_bag(widget.root, store)
        widget.refresh()

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

    def _rendered_datatable(
        self, node: Any, children: list[Widget], runtime_attrs: dict[str, Any],
    ) -> Widget:
        """DataTable: columns and rows populated post-mount.

        DataTable's add_column/add_row require the widget to be mounted
        (it allocates internal storage on mount). We defer the
        population via call_after_refresh, Textual's idiomatic
        post-mount hook. The column/row child *nodes* (not widgets) drive
        the population, read from ``node.value``.
        """
        from textual.widgets import DataTable

        attrs = {k: v for k, v in runtime_attrs.items() if not k.startswith("_")}
        kwargs = self._filter_kwargs_for_signature(attrs, DataTable.__init__)
        if "id" not in kwargs:
            kwargs["id"] = f"datatable_{self.widget_counter}"
        widget = DataTable(**kwargs)
        widget._bag_node = node  # type: ignore[attr-defined]

        if isinstance(node.value, Bag):
            children_snapshot = list(node.value)
            widget.call_after_refresh(
                lambda w=widget, kids=children_snapshot: self._populate_datatable(
                    w, kids,
                ),
            )
        return widget

    def _populate_datatable(
        self, widget: Any, children: list[BagNode],
    ) -> None:
        """Populate a DataTable from its column/row child nodes."""
        for child_node in children:
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

    def _accepts_var_positional(self, textual_class: type) -> bool:
        """Check if __init__ accepts *args (container that takes children)."""
        sig = inspect.signature(textual_class.__init__)
        return any(
            p.kind == inspect.Parameter.VAR_POSITIONAL
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
