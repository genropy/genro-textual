# Schema: Textual Widgets

Auto-generated from TextualBuilder schema. 61 elements total.

| Name | Sub Tags | Parameters | Compile | Documentation |
| --- | --- | --- | --- | --- |
| `container` | * | - | module: textual.containers, class: Container | A generic container widget. |
| `vertical` | * | - | module: textual.containers, class: Vertical | A container that arranges children vertically. |
| `horizontal` | * | - | module: textual.containers, class: Horizontal | A container that arranges children horizontally. |
| `center` | * | - | module: textual.containers, class: Center | A container that centers its children horizontally. |
| `middle` | * | - | module: textual.containers, class: Middle | A container that centers its children vertically. |
| `centermiddle` | * | - | module: textual.containers, class: CenterMiddle | A container that centers its children both horizontally and vertically. |
| `right` | * | - | module: textual.containers, class: Right | A container that aligns its children to the right. |
| `grid` | * | - | module: textual.containers, class: Grid | A container with grid layout. |
| `verticalscroll` | * | - | module: textual.containers, class: VerticalScroll | A scrollable vertical container. |
| `horizontalscroll` | * | - | module: textual.containers, class: HorizontalScroll | A scrollable horizontal container. |
| `scrollablecontainer` | * | - | module: textual.containers, class: ScrollableContainer | A scrollable container. |
| `verticalgroup` | * | - | module: textual.containers, class: VerticalGroup | A vertical group of widgets. |
| `horizontalgroup` | * | - | module: textual.containers, class: HorizontalGroup | A horizontal group of widgets. |
| `itemgrid` | * | min_column_width | module: textual.containers, class: ItemGrid | A grid container that arranges items in columns. |
| `button` | - | content, label, variant, tooltip, action | module: textual.widgets, class: Button | A simple clickable button. |
| `checkbox` | - | content, label, value, button_first, tooltip, compact | module: textual.widgets, class: Checkbox | A check box widget that represents a boolean value. |
| `collapsible` | * | title, collapsed, collapsed_symbol, expanded_symbol | module: textual.widgets, class: Collapsible | A collapsible container. |
| `collapsibletitle` | - | content, label, collapsed_symbol, expanded_symbol, collapsed | module: textual.widgets, class: CollapsibleTitle | Title and symbol for the Collapsible. |
| `contentswitcher` | * | initial | module: textual.widgets, class: ContentSwitcher | A widget for switching between different children. |
| `datatable` | column,row | show_header, show_row_labels, fixed_rows, fixed_columns, zebra_stripes, header_height, show_cursor, cursor_foreground_priority, cursor_background_priority, cursor_type, cell_padding | module: textual.widgets, class: DataTable | A tabular widget that contains data. |
| `column` | - | label, key, width | - | A column definition for DataTable. |
| `row` | - | key, label, height | - | A row for DataTable. Value can be a list of cell values. |
| `digits` | - | content, value | module: textual.widgets, class: Digits | A widget to display numerical values using a 3x3 grid of unicode characters. |
| `directorytree` | - | content, path | module: textual.widgets, class: DirectoryTree | A Tree widget that presents files and directories. |
| `footer` | * | show_command_palette, compact | module: textual.widgets, class: Footer | Textual Footer widget. |
| `header` | - | content, show_clock, icon, time_format | module: textual.widgets, class: Header | A header widget with icon and clock. |
| `helppanel` | * | markup | module: textual.widgets, class: HelpPanel | Textual HelpPanel widget. |
| `input` | - | content, value, placeholder, password, restrict, type, max_length, valid_empty, select_on_focus, tooltip, compact | module: textual.widgets, class: Input | A text input widget. |
| `keypanel` | * | can_focus, can_focus_children, can_maximize | module: textual.widgets, class: KeyPanel | Textual KeyPanel widget. |
| `label` | - | content, variant, expand, shrink, markup | module: textual.widgets, class: Label | A simple label widget for displaying text-oriented renderables. |
| `link` | - | content, text, url, tooltip | module: textual.widgets, class: Link | A simple, clickable link that opens a URL. |
| `listitem` | * | markup | module: textual.widgets, class: ListItem | A widget that is an item within a `ListView`. |
| `listview` | listitem | initial_index | module: textual.widgets, class: ListView | A vertical list view widget. |
| `loadingindicator` | - | content | module: textual.widgets, class: LoadingIndicator | Display an animated loading indicator. |
| `log` | - | content, highlight, max_lines, auto_scroll | module: textual.widgets, class: Log | A widget to log text. |
| `markdown` | - | content, markdown, parser_factory, open_links | module: textual.widgets, class: Markdown | Textual Markdown widget. |
| `markdownviewer` | - | content, markdown, show_table_of_contents, parser_factory, open_links | module: textual.widgets, class: MarkdownViewer | A Markdown viewer widget. |
| `maskedinput` | - | content, template, value, placeholder, valid_empty, select_on_focus, tooltip, compact | module: textual.widgets, class: MaskedInput | A masked text input widget. |
| `optionlist` | * | markup, compact | module: textual.widgets, class: OptionList | A navigable list of options. |
| `placeholder` | - | content, label, variant | module: textual.widgets, class: Placeholder | A simple placeholder widget to use before you build your custom widgets. |
| `pretty` | - | content, object | module: textual.widgets, class: Pretty | A pretty-printing widget. |
| `progressbar` | - | content, total, show_bar, show_percentage, show_eta, clock, gradient | module: textual.widgets, class: ProgressBar | A progress bar widget. |
| `radiobutton` | - | content, label, value, button_first, tooltip, compact | module: textual.widgets, class: RadioButton | A radio button widget that represents a boolean value. |
| `radioset` | radiobutton | tooltip, compact | module: textual.widgets, class: RadioSet | Widget for grouping a collection of radio buttons into a set. |
| `richlog` | - | content, max_lines, min_width, wrap, highlight, markup, auto_scroll | module: textual.widgets, class: RichLog | A widget for logging Rich renderables and text. |
| `rule` | - | content, orientation, line_style | module: textual.widgets, class: Rule | A rule widget to separate content, similar to a `<hr>` HTML tag. |
| `select` | - | content, options, prompt, allow_blank, value, type_to_search, tooltip, compact | module: textual.widgets, class: Select | Widget to select from a list of possible options. |
| `selectionlist` | * | compact | module: textual.widgets, class: SelectionList | A vertical selection list that allows making multiple selections. |
| `sparkline` | - | content, data, min_color, max_color, summary_function | module: textual.widgets, class: Sparkline | A sparkline widget to display numerical data. |
| `static` | - | content, expand, shrink, markup | module: textual.widgets, class: Static | A widget to display simple static content. |
| `switch` | - | content, value, animate, tooltip | module: textual.widgets, class: Switch | A switch widget that represents a boolean value. |
| `tab` | - | content, label | module: textual.widgets, class: Tab | A Widget to manage a single tab within a Tabs widget. |
| `tabpane` | * | title | module: textual.widgets, class: TabPane | A container for switchable content, with additional title. |
| `tabbedcontent` | tabpane | initial | module: textual.widgets, class: TabbedContent | A container with associated tabs to toggle content visibility. |
| `tabs` | tab | active | module: textual.widgets, class: Tabs | A row of tabs. |
| `textarea` | - | content, text, language, theme, soft_wrap, tab_behavior, read_only, show_cursor, show_line_numbers, line_number_start, max_checkpoints, tooltip, compact, highlight_cursor_line, placeholder | module: textual.widgets, class: TextArea | Textual TextArea widget. |
| `tooltip` | - | content, expand, shrink, markup | module: textual.widgets, class: Tooltip | Textual Tooltip widget. |
| `tree` | - | content, label, data | module: textual.widgets, class: Tree | A widget for displaying and navigating data in a tree. |
| `welcome` | - | content, expand, shrink, markup | module: textual.widgets, class: Welcome | A Textual welcome widget. |
| `css` | - | content | - | CSS stylesheet applied to the live app. |
| `binding` | - | key, action, description | - | Key binding: maps a key press to an action method. |
| `fieldset` | - | - | component | A group of input fields with a title. Closed: returns parent for chaining. |
| `form` | * | - | component | A form container. Open: returns internal bag for adding fields. |
