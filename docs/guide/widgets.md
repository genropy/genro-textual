# Widgets

Genro Textual wraps 60+ Textual widgets as builder elements. All are available as methods on the page/container.

## Containers

| Method | Widget | Description |
|--------|--------|-------------|
| `vertical()` | Vertical | Arrange children vertically |
| `horizontal()` | Horizontal | Arrange children horizontally |
| `grid()` | Grid | Grid layout |
| `center()` | Center | Center children horizontally |
| `middle()` | Middle | Center children vertically |
| `verticalscroll()` | VerticalScroll | Scrollable vertical |
| `horizontalscroll()` | HorizontalScroll | Scrollable horizontal |
| `container()` | Container | Generic container |

## Input Widgets

| Method | Widget | Binding |
|--------|--------|---------|
| `input(value="^path")` | Input | Writes on blur |
| `checkbox(value="^path")` | Checkbox | Writes on change |
| `switch(value="^path")` | Switch | Writes on change |
| `radiobutton()` | RadioButton | Toggle |
| `radioset()` | RadioSet | Group of radio buttons |
| `select()` | Select | Dropdown |
| `textarea()` | TextArea | Multi-line input |
| `button(label, variant)` | Button | Click handler |

## Display Widgets

| Method | Widget | Description |
|--------|--------|-------------|
| `static("text")` | Static | Display text (bindable) |
| `label("text")` | Label | Simple label |
| `markdown("# Title")` | Markdown | Render markdown |
| `rule()` | Rule | Horizontal/vertical rule |
| `progressbar(total=100)` | ProgressBar | Progress indicator |
| `sparkline()` | Sparkline | Data visualization |
| `digits("123")` | Digits | Large digit display |
| `log()` | Log | Append-only text |
| `richlog()` | RichLog | Rich-formatted log |

## Complex Widgets

| Method | Widget | Description |
|--------|--------|-------------|
| `tabbedcontent()` | TabbedContent | Tab container |
| `tabpane(title)` | TabPane | Tab content |
| `datatable()` | DataTable | Table with columns/rows |
| `tree(label, store)` | Tree | Hierarchical tree |
| `collapsible(title)` | Collapsible | Expandable section |
| `directorytree(path)` | DirectoryTree | File browser |

## App Widgets

| Method | Widget | Description |
|--------|--------|-------------|
| `header()` | Header | App header bar |
| `footer()` | Footer | Footer with bindings |

## Components

Components are reusable composite elements defined with `@component` in mixin classes. They live in `genro_textual.components`.

| Method | Mixin | Slots | Description |
| ------ | ----- | ----- | ----------- |
| `app_shell(title, ...)` | FoundationMixin | `content` | Full app layout with inspector drawer |
| `fieldset(title)` | TextualWidgetsMixin | — | Group of fields with title |
| `form(title)` | TextualWidgetsMixin | — | Form container |

Components can declare **named slots** — insertion points where the caller adds content:

```python
shell = page.app_shell(title="My App", data_store=self.data)
shell.content.static("Hello!")     # adds to the 'content' slot
shell.content.input(value="^name") # also in the 'content' slot
```

## Config (Non-Widget)

| Method | Description |
|--------|-------------|
| `css("...")` | Inline CSS stylesheet |
| `binding(key, action, description)` | Key binding |

## Tree with Store

The Tree widget can display a Bag structure:

```python
page.tree(label="data", store=self.data)
```

The tree populates recursively. When the Bag changes, the tree updates preserving expanded state.
