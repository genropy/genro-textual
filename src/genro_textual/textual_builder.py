# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""TextualBuilder - Builder for Textual TUI widgets.

Elements and components are defined in TextualWidgetsMixin so that
subclasses of TextualBuilder inherit the full schema. This follows
the genro-builders mixin pattern: _pop_decorated_methods collects
decorators from mixin bases (non-BagBuilderBase) in the MRO.

No rendering logic here — that belongs in TextualCompiler.
"""
from __future__ import annotations

from genro_builders.builder import BagBuilderBase, component, element


class TextualWidgetsMixin:
    """All Textual widget @element and @component definitions.

    Defined as a mixin so that subclasses of TextualBuilder
    automatically inherit the full schema via MRO.
    """

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
        total: float | int | None = None,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_eta: bool = True,
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
    # App configuration elements (not rendered as widgets)
    # -------------------------------------------------------------------------

    @element(sub_tags="")
    def css(self, content: str = ""):
        """CSS stylesheet applied to the live app."""
        ...

    @element(sub_tags="")
    def binding(self, key: str = "", action: str = "", description: str = ""):
        """Key binding: maps a key press to an action method."""
        ...

    # -------------------------------------------------------------------------
    # Components (composite elements expanded at compile time)
    # -------------------------------------------------------------------------

    @component(sub_tags="")
    def fieldset(self, comp, title="", **kwargs):
        """A group of input fields with a title. Closed: returns parent for chaining."""
        if title:
            comp.static(title)

    @component(sub_tags="*")
    def form(self, comp, title="", **kwargs):
        """A form container. Open: returns internal bag for adding fields."""
        if title:
            comp.static(title)


class TextualBuilder(TextualWidgetsMixin, BagBuilderBase):
    """Builder for Textual TUI elements.

    All @element and @component definitions live in TextualWidgetsMixin.
    Subclass TextualBuilder freely — the mixin schema is inherited via MRO.

    To add custom components, define them in a mixin:

        class MyMixin:
            @component(sub_tags="")
            def login_form(self, comp, **kwargs):
                comp.input(placeholder="Username")
                comp.button("Login")

        class MyBuilder(MyMixin, TextualBuilder):
            pass
    """
