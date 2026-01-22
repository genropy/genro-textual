# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualBuilder - Builder for Textual TUI widgets.

Auto-generated element methods for all Textual widgets.
Each method is decorated with @element and has proper sub_tags and typed parameters.
"""

from __future__ import annotations

import inspect
from importlib import import_module
from typing import TYPE_CHECKING, Any

from genro_bag import Bag
from genro_bag.builder import BagBuilderBase, element
from textual.widget import Widget

if TYPE_CHECKING:
    from genro_bag.bagnode import BagNode


class TextualBuilder(BagBuilderBase):
    """Builder for Textual TUI elements.

    All standard Textual widgets are available as methods.
    """

    def __init__(self, bag: Bag) -> None:
        super().__init__(bag)
        self._widget_counter = 0

    @property
    def widget_counter(self) -> int:
        """Return current counter and auto-increment for next widget."""
        current = self._widget_counter
        self._widget_counter += 1
        return current

    # -------------------------------------------------------------------------
    # Container elements (from textual.containers)
    # -------------------------------------------------------------------------

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Container")
    def container(self):
        """A generic container widget."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Vertical")
    def vertical(self):
        """A container that arranges children vertically."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Horizontal")
    def horizontal(self):
        """A container that arranges children horizontally."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Center")
    def center(self):
        """A container that centers its children horizontally."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Middle")
    def middle(self):
        """A container that centers its children vertically."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="CenterMiddle")
    def centermiddle(self):
        """A container that centers its children both horizontally and vertically."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Right")
    def right(self):
        """A container that aligns its children to the right."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="Grid")
    def grid(self):
        """A container with grid layout."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="VerticalScroll")
    def verticalscroll(self):
        """A scrollable vertical container."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="HorizontalScroll")
    def horizontalscroll(self):
        """A scrollable horizontal container."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="ScrollableContainer")
    def scrollablecontainer(self):
        """A scrollable container."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="VerticalGroup")
    def verticalgroup(self):
        """A vertical group of widgets."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="HorizontalGroup")
    def horizontalgroup(self):
        """A horizontal group of widgets."""
        ...

    @element(sub_tags="*", compile_module="textual.containers", compile_class="ItemGrid")
    def itemgrid(self, min_column_width: int = 20):
        """A grid container that arranges items in columns."""
        ...

    # -------------------------------------------------------------------------
    # Widget elements (from textual.widgets)
    # -------------------------------------------------------------------------

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Button")
    def button(
        self,
        content: str = "",
        label: str | None = None,
        variant: str = "default",
        tooltip: str | None = None,
        action: str | None = None,
    ):
        """A simple clickable button."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Checkbox")
    def checkbox(
        self,
        content: str = "",
        label: str = "",
        value: bool = False,
        button_first: bool = True,
        tooltip: str | None = None,
        compact: bool = False,
    ):
        """A check box widget that represents a boolean value."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="Collapsible")
    def collapsible(
        self,
        title: str = "Toggle",
        collapsed: bool = True,
        collapsed_symbol: str = "▶",
        expanded_symbol: str = "▼",
    ):
        """A collapsible container."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="CollapsibleTitle")
    def collapsibletitle(
        self,
        content: str = "",
        label: str | None = None,
        collapsed_symbol: str | None = None,
        expanded_symbol: str | None = None,
        collapsed: str | None = None,
    ):
        """Title and symbol for the Collapsible."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="ContentSwitcher")
    def contentswitcher(self, initial: str | None = None):
        """A widget for switching between different children."""
        ...

    @element(sub_tags="column,row", compile_module="textual.widgets", compile_class="DataTable")
    def datatable(
        self,
        show_header: bool = True,
        show_row_labels: bool = True,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        zebra_stripes: bool = False,
        header_height: int = 1,
        show_cursor: bool = True,
        cursor_foreground_priority: str = "css",
        cursor_background_priority: str = "renderable",
        cursor_type: str = "cell",
        cell_padding: int = 1,
    ):
        """A tabular widget that contains data."""
        ...

    @element(sub_tags="", parent_tags="datatable")
    def column(self, label: str = "", key: str | None = None, width: int | None = None):
        """A column definition for DataTable."""
        ...

    @element(sub_tags="", parent_tags="datatable")
    def row(self, key: str | None = None, label: str | None = None, height: int = 1):
        """A row for DataTable. Value can be a list of cell values."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Digits")
    def digits(self, content: str = "", value: str = ""):
        """A widget to display numerical values using a 3x3 grid of unicode characters."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="DirectoryTree")
    def directorytree(self, content: str = "", path: str | None = None):
        """A Tree widget that presents files and directories."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="Footer")
    def footer(self, show_command_palette: bool = True, compact: bool = False):
        """Textual Footer widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Header")
    def header(
        self,
        content: str = "",
        show_clock: bool = False,
        icon: str | None = None,
        time_format: str | None = None,
    ):
        """A header widget with icon and clock."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="HelpPanel")
    def helppanel(self, markup: bool = True):
        """Textual HelpPanel widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Input")
    def input(
        self,
        content: str = "",
        value: str | None = None,
        placeholder: str = "",
        password: bool = False,
        restrict: str | None = None,
        type: str = "text",
        max_length: int = 0,
        valid_empty: bool = False,
        select_on_focus: bool = True,
        tooltip: str | None = None,
        compact: bool = False,
    ):
        """A text input widget."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="KeyPanel")
    def keypanel(
        self,
        can_focus: str | None = None,
        can_focus_children: str | None = None,
        can_maximize: str | None = None,
    ):
        """Textual KeyPanel widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Label")
    def label(
        self,
        content: str = "",
        variant: str | None = None,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
    ):
        """A simple label widget for displaying text-oriented renderables."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Link")
    def link(
        self,
        content: str = "",
        text: str | None = None,
        url: str | None = None,
        tooltip: str | None = None,
    ):
        """A simple, clickable link that opens a URL."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="ListItem")
    def listitem(self, markup: bool = True):
        """A widget that is an item within a `ListView`."""
        ...

    @element(sub_tags="listitem", compile_module="textual.widgets", compile_class="ListView")
    def listview(self, initial_index: int = 0):
        """A vertical list view widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="LoadingIndicator")
    def loadingindicator(self, content: str = ""):
        """Display an animated loading indicator."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Log")
    def log(
        self,
        content: str = "",
        highlight: bool = False,
        max_lines: str | None = None,
        auto_scroll: bool = True,
    ):
        """A widget to log text."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Markdown")
    def markdown(
        self,
        content: str = "",
        markdown: str | None = None,
        parser_factory: str | None = None,
        open_links: bool = True,
    ):
        """Textual Markdown widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="MarkdownViewer")
    def markdownviewer(
        self,
        content: str = "",
        markdown: str | None = None,
        show_table_of_contents: bool = True,
        parser_factory: str | None = None,
        open_links: bool = True,
    ):
        """A Markdown viewer widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="MaskedInput")
    def maskedinput(
        self,
        content: str = "",
        template: str | None = None,
        value: str | None = None,
        placeholder: str = "",
        valid_empty: bool = False,
        select_on_focus: bool = True,
        tooltip: str | None = None,
        compact: bool = False,
    ):
        """A masked text input widget."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="OptionList")
    def optionlist(self, markup: bool = True, compact: bool = False):
        """A navigable list of options."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Placeholder")
    def placeholder(self, content: str = "", label: str | None = None, variant: str = "default"):
        """A simple placeholder widget to use before you build your custom widgets."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Pretty")
    def pretty(self, content: str = "", object: str | None = None):
        """A pretty-printing widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="ProgressBar")
    def progressbar(
        self,
        content: str = "",
        total: str | None = None,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_eta: bool = True,
        clock: str | None = None,
        gradient: str | None = None,
    ):
        """A progress bar widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="RadioButton")
    def radiobutton(
        self,
        content: str = "",
        label: str = "",
        value: bool = False,
        button_first: bool = True,
        tooltip: str | None = None,
        compact: bool = False,
    ):
        """A radio button widget that represents a boolean value."""
        ...

    @element(sub_tags="radiobutton", compile_module="textual.widgets", compile_class="RadioSet")
    def radioset(self, tooltip: str | None = None, compact: bool = False):
        """Widget for grouping a collection of radio buttons into a set."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="RichLog")
    def richlog(
        self,
        content: str = "",
        max_lines: str | None = None,
        min_width: int = 78,
        wrap: bool = False,
        highlight: bool = False,
        markup: bool = False,
        auto_scroll: bool = True,
    ):
        """A widget for logging Rich renderables and text."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Rule")
    def rule(self, content: str = "", orientation: str = "horizontal", line_style: str = "solid"):
        """A rule widget to separate content, similar to a `<hr>` HTML tag."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Select")
    def select(
        self,
        content: str = "",
        options: str | None = None,
        prompt: str = "Select",
        allow_blank: bool = True,
        value: str = None,
        type_to_search: bool = True,
        tooltip: str | None = None,
        compact: bool = False,
    ):
        """Widget to select from a list of possible options."""
        ...

    @element(sub_tags="*", compile_module="textual.widgets", compile_class="SelectionList")
    def selectionlist(self, compact: bool = False):
        """A vertical selection list that allows making multiple selections."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Sparkline")
    def sparkline(
        self,
        content: str = "",
        data: str | None = None,
        min_color: str | None = None,
        max_color: str | None = None,
        summary_function: str | None = None,
    ):
        """A sparkline widget to display numerical data."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Static")
    def static(
        self, content: str = "", expand: bool = False, shrink: bool = False, markup: bool = True
    ):
        """A widget to display simple static content."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Switch")
    def switch(
        self,
        content: str = "",
        value: bool = False,
        animate: bool = True,
        tooltip: str | None = None,
    ):
        """A switch widget that represents a boolean value."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Tab")
    def tab(self, content: str = "", label: str | None = None):
        """A Widget to manage a single tab within a Tabs widget."""
        ...

    @element(
        sub_tags="*",
        parent_tags="tabbedcontent",
        compile_module="textual.widgets",
        compile_class="TabPane",
    )
    def tabpane(self, title: str | None = None):
        """A container for switchable content, with additional title."""
        ...

    @element(sub_tags="tabpane", compile_module="textual.widgets", compile_class="TabbedContent")
    def tabbedcontent(self, initial: str = ""):
        """A container with associated tabs to toggle content visibility."""
        ...

    @element(sub_tags="tab", compile_module="textual.widgets", compile_class="Tabs")
    def tabs(self, active: str | None = None):
        """A row of tabs."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="TextArea")
    def textarea(
        self,
        content: str = "",
        text: str = "",
        language: str | None = None,
        theme: str = "css",
        soft_wrap: bool = True,
        tab_behavior: str = "focus",
        read_only: bool = False,
        show_cursor: bool = True,
        show_line_numbers: bool = False,
        line_number_start: int = 1,
        max_checkpoints: int = 50,
        tooltip: str | None = None,
        compact: bool = False,
        highlight_cursor_line: bool = True,
        placeholder: str = "",
    ):
        """Textual TextArea widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Tooltip")
    def tooltip(
        self, content: str = "", expand: bool = False, shrink: bool = False, markup: bool = True
    ):
        """Textual Tooltip widget."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Tree")
    def tree(self, content: str = "", label: str | None = None, data: str | None = None):
        """A widget for displaying and navigating data in a tree."""
        ...

    @element(sub_tags="", compile_module="textual.widgets", compile_class="Welcome")
    def welcome(
        self, content: str = "", expand: bool = False, shrink: bool = False, markup: bool = True
    ):
        """A Textual welcome widget."""
        ...

    # -------------------------------------------------------------------------
    # Compile: transform Bag to Textual widgets using mount()
    # -------------------------------------------------------------------------

    def compile(self, bag: Bag, parent_widget: Widget) -> None:
        """Compile a Bag to Textual widgets, mounting them to parent."""
        for node in bag:
            self._compile_node(node, parent_widget)

    def _compile_node(self, node: BagNode, parent_widget: Widget) -> None:
        """Compile a single node and mount it to parent."""
        tag = node.tag or "static"

        # Check for dedicated compile method _compile_<tag>
        compile_method = getattr(self, f"_compile_{tag}", None)
        if compile_method:
            compile_method(node, parent_widget)
            return

        attr = dict(node.attr)

        schema_info = self.get_schema_info(tag)
        compile_kwargs = schema_info.get("compile_kwargs", {})

        module_name = compile_kwargs.get("module", "textual.widgets")
        class_name = compile_kwargs.get("class")

        if class_name is None:
            raise ValueError(f"Element '{tag}' missing compile_class in schema")

        module = import_module(module_name)
        textual_class = getattr(module, class_name)

        kwargs = self._build_widget_kwargs(attr, textual_class)

        # Auto-generate unique widget id
        if "id" not in kwargs:
            kwargs["id"] = f"{tag}_{self.widget_counter}"

        if isinstance(node.value, Bag):
            # CONTAINER: ha figli
            content = ""
        else:
            # LEAF: prendi il contenuto
            content = str(node.value) if node.value else ""

        # Crea il widget - mappa content sul primo parametro posizionale come keyword
        first_param = self._get_first_positional_param(textual_class)
        if content and first_param and first_param not in kwargs:
            kwargs[first_param] = content
        widget = textual_class(**kwargs)

        # Salva il widget nel nodo
        node.compiled["widget"] = widget

        # Monta il widget nel parent
        parent_widget.mount(widget)

        # Se è un container, compila ricorsivamente i figli
        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._compile_node(child_node, widget)

    def _build_widget_kwargs(self, attr: dict[str, Any], widget_class: type) -> dict[str, Any]:
        """Build kwargs for widget constructor, filtering by signature."""
        sig = inspect.signature(widget_class.__init__)
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

    def _build_method_kwargs(self, attr: dict[str, Any], method: callable) -> dict[str, Any]:
        """Build kwargs for a method call, filtering by signature.

        Similar to _build_widget_kwargs but for methods like add_row(), add_column().
        """
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

    def _get_first_positional_param(self, widget_class: type) -> str | None:
        """Get the name of the first positional parameter (after self).

        Returns the parameter name if it exists and is positional, None otherwise.
        This allows mapping node.value to the appropriate parameter (content, label, text, etc.)
        """
        sig = inspect.signature(widget_class.__init__)
        params = list(sig.parameters.values())
        if len(params) > 1:
            first_param = params[1]  # Skip 'self'
            if first_param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.POSITIONAL_ONLY,
            ):
                return first_param.name
        return None

    # -------------------------------------------------------------------------
    # Dedicated compile methods for widgets needing special handling
    # -------------------------------------------------------------------------

    def _compile_static(self, node: BagNode, parent_widget: Widget) -> None:
        """Static: semplice widget di testo."""
        from textual.widgets import Static

        content = str(node.value) if node.value else ""
        # Filtra attributi interni (iniziano con _)
        attr = {k: v for k, v in node.attr.items() if not k.startswith("_")}

        if "id" not in attr:
            attr["id"] = f"static_{self.widget_counter}"

        widget = Static(content, **attr)
        node.compiled["widget"] = widget
        parent_widget.mount(widget)

    def _compile_tabbedcontent(self, node: BagNode, parent_widget: Widget) -> None:
        """TabbedContent: usa add_pane() per aggiungere i TabPane."""
        from textual.widgets import TabbedContent

        attr = dict(node.attr)
        kwargs = self._build_widget_kwargs(attr, TabbedContent)

        if "id" not in kwargs:
            kwargs["id"] = f"tabbedcontent_{self.widget_counter}"

        widget = TabbedContent(**kwargs)
        node.compiled["widget"] = widget
        parent_widget.mount(widget)

        # I TabPane vanno aggiunti con add_pane(), non mount()
        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._compile_tabpane_for_tabbedcontent(child_node, widget)

    def _compile_tabpane_for_tabbedcontent(self, node: BagNode, tabbed_content: Widget) -> None:
        """TabPane: aggiunto a TabbedContent con add_pane()."""
        from textual.widgets import TabPane

        attr = dict(node.attr)
        title = attr.pop("title", None) or "Untitled"
        kwargs = self._build_widget_kwargs(attr, TabPane)

        if "id" not in kwargs:
            kwargs["id"] = f"tabpane_{self.widget_counter}"

        widget = TabPane(title, **kwargs)
        node.compiled["widget"] = widget

        # Usa add_pane() invece di mount()
        tabbed_content.add_pane(widget)

        # Compila ricorsivamente i figli dentro il TabPane
        if isinstance(node.value, Bag):
            for child_node in node.value:
                self._compile_node(child_node, widget)

    def _compile_datatable(self, node: BagNode, parent_widget: Widget) -> None:
        """DataTable: columns and rows via add_column/add_row."""
        from textual.widgets import DataTable

        attr = dict(node.attr)
        kwargs = self._build_widget_kwargs(attr, DataTable)

        if "id" not in kwargs:
            kwargs["id"] = f"datatable_{self.widget_counter}"

        widget = DataTable(**kwargs)
        node.compiled["widget"] = widget
        parent_widget.mount(widget)

        if isinstance(node.value, Bag):
            columns = []
            rows = []
            for child_node in node.value:
                if child_node.tag == "column":
                    columns.append(child_node)
                elif child_node.tag == "row":
                    rows.append(child_node)

            for col_node in columns:
                col_attr = dict(col_node.attr)
                label = col_attr.get("label", str(col_node.value) if col_node.value else "")
                # Filter column kwargs based on add_column signature (version-safe)
                col_kwargs = self._build_method_kwargs(col_attr, widget.add_column)
                widget.add_column(label, **col_kwargs)

            for row_node in rows:
                row_attr = dict(row_node.attr)
                if isinstance(row_node.value, (list, tuple)):
                    cells = row_node.value
                elif isinstance(row_node.value, Bag):
                    cells = [str(c.value) for c in row_node.value]
                else:
                    cells = [str(row_node.value)] if row_node.value else []
                # Filter row kwargs based on add_row signature
                row_kwargs = self._build_method_kwargs(row_attr, widget.add_row)
                widget.add_row(*cells, **row_kwargs)
