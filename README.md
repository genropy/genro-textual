# genro-textual

**Declarative Terminal UI framework** built on [Textual](https://textual.textualize.io/) and powered by [genro-builders](https://github.com/genropy/genro-builders).

Define your UI in a `main()` method — widgets, CSS, key bindings, data binding — all as Bag nodes. The build step transforms the source into a live Textual app with reactive data binding.

**Status: Pre-Alpha** — Active development.

[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue)](https://genro-textual.readthedocs.io)

## Installation

```bash
pip install genro-textual
```

## Quick Start

```python
from genro_textual import TextualApp

class Application(TextualApp):
    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.static("^greeting")
        source.input(value="^form.name", placeholder="Your name")
        source.button("OK")

    def store(self, data):
        data["greeting"] = "Hello, World!"
        data["form.name"] = ""

if __name__ == "__main__":
    Application().run()
```

Type a name in the input, press Tab — the greeting doesn't change (it's on a different path), but the data Bag updates. Bind the Static and Input to the same path to see reactive updates.

## Architecture

genro-textual follows the **puppeteer/puppet** pattern:

- **TextualApp** (the puppeteer) — configures main, data, builder
- **LiveApp** (the puppet) — a bare `textual.app.App` driven by the puppeteer
- **Built Bag** — the script, kept in sync by the BindingManager

```text
┌──────────────┐      build      ┌──────────────┐     render     ┌──────────────┐
│  Source Bag   │ ──────────────► │  Built Bag   │ ─────────────► │   LiveApp    │
│  (main)       │                 │ (expanded,   │                │  (Textual)   │
│              │                 │  resolved)   │                │              │
└──────────────┘                 └──────────────┘                └──────────────┘
       ▲                                │                               │
       │                         BindingManager                         │
       │                         (data → widget)                        │
       │                                                                │
       │                         blur / change                          │
       └─────────────────────── (widget → data) ───────────────────────┘
```

## Data Binding

### Read: Data to Widget

Bind widget values to data using `^path` syntax:

```python
source.static("^user.name")              # value bound to data path
source.input(value="^form.email")        # attribute bound to data path
```

When `data["user.name"]` changes, the Static updates automatically.

### Write: Widget to Data

- **Input** — writes to data on **blur** (Tab, click away), not on every keystroke
- **Checkbox / Switch** — writes to data on **change** (immediate)

The `_reason` mechanism prevents infinite loops: when a widget writes to data, the BindingManager skips updating that same widget.

### Bidirectional Example

```python
class Application(TextualApp):
    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.input(value="^form.name", placeholder="Name")
        source.input(value="^form.surname", placeholder="Surname")
        source.static("^form.name")       # updates when Input blurs
        source.static("^form.surname")
        source.button("OK")

    def store(self, data):
        data["form.name"] = "John"
        data["form.surname"] = "Doe"
```

## CSS

### Inline Stylesheets

CSS in the main method, with Textual theme variables:

```python
source.css("""
    .title { color: green; text-style: bold; }
    #sidebar { width: 30; background: $surface; border-left: solid $primary; }
""")
```

### Direct Style Attributes

CSS properties can be set directly on widgets and bound to data:

```python
source.vertical(id="panel", width="^_system.panel.width", display="^_system.panel.display")
```

When `data["_system.panel.width"]` changes, the widget resizes. Style attributes are classified automatically at mount time:

1. Constructor parameters → `widget.__init__`
2. CSS properties → `widget.styles`
3. Reactive attributes → `widget.set_reactive`

Note: CSS variables (`$surface`, `$primary`) work only in `source.css()`, not in direct attributes.

## App Shell

The `app_shell` component provides a complete application layout with header, scrollable content area, resizable inspector drawer (Data/Source/Built tree tabs), and footer:

```python
class Application(TextualApp):
    def main(self, source):
        shell = source.app_shell(
            title="My App",
            data_store=self.data,
            source_store=self.source,
            compiled_store=self.compiled,
        )
        shell.content.static("Hello!")
        shell.content.input(value="^form.name", placeholder="Name")

    def store(self, data):
        self._init_shell_data()
        data["form.name"] = "John"
```

The `content` slot is a named insertion point — widgets added to `shell.content` are mounted inside the scrollable content area. Press **F12** to toggle the inspector drawer.

`app_shell` is defined in `FoundationMixin`, included in `TextualBuilder` by default. To exclude it, compose your own builder without the mixin.

## Key Bindings

```python
source.binding(key="q", action="quit", description="Quit")
source.binding(key="f12", action="toggle_drawer", description="Inspector")
```

Bindings appear in the Footer and are clickable.

## Components

Reusable UI blocks defined with `@component` in mixin classes. Component mixins live in `genro_textual.components`.

### Simple component (no slots)

```python
from genro_builders.builder import component
from genro_textual import TextualApp, TextualBuilder

class MyMixin:
    @component(sub_tags="")
    def login_form(self, comp, title="Login", **kwargs):
        comp.static(title)
        comp.input(placeholder="Username", value="^.username")
        comp.input(placeholder="Password", value="^.password")
        comp.button("Submit", variant="primary")

class MyBuilder(MyMixin, TextualBuilder):
    pass

class Application(TextualApp):
    builder_class = MyBuilder

    def main(self, source):
        source.login_form(title="Sign In")
```

### Component with named slots

Components can declare named slots — insertion points where the caller adds content:

```python
class DashboardMixin:
    @component(sub_tags="*", slots=["left", "right"])
    def dashboard(self, comp, title="", **kwargs):
        comp.static(title)
        main = comp.horizontal()
        left_node = main.vertical(id="left-panel")
        right_node = main.vertical(id="right-panel")
        return {"left": left_node, "right": right_node}

class MyBuilder(DashboardMixin, TextualBuilder):
    pass
```

Usage in main:

```python
def main(self, source):
    dash = source.dashboard(title="Overview")
    dash.left.tree(label="nav", store=self.data)
    dash.right.static("Main content")
```

The handler body returns a dict mapping slot names to destination nodes. Content added to slots at main time is mounted into those nodes at build time.

## Live REPL

Connect to a running app and modify it in real-time:

```bash
# Terminal 1: Start the app
pygui run examples/complex_app.py

# Terminal 2: Connect to it
pygui connect complex_app
```

```python
>>> app.data["form.name"] = "New value"
>>> app.page.static("Added from REPL!")
```

## CLI Reference

| Command | Description |
| ------- | ----------- |
| `pygui run FILE.py` | Run a TextualApp |
| `pygui run -r FILE.py` | Run with **auto-reload** (watches for file changes) |
| `pygui run -c FILE.py` | Run and **connect REPL** in tmux split |
| `pygui list` | List registered running apps |
| `pygui connect NAME` | Connect REPL to a running app |
| `pygui stop NAME` | Stop a running app |
| `pygui completions zsh` | Generate shell completions |

## Supported Widgets

genro-textual supports **60+ Textual elements**:

### Containers

`container`, `vertical`, `horizontal`, `center`, `middle`, `grid`, `verticalscroll`, `horizontalscroll`, `scrollablecontainer`, `verticalgroup`, `horizontalgroup`, `itemgrid`

### Input Widgets

`button`, `checkbox`, `input`, `maskedinput`, `switch`, `select`, `selectionlist`, `optionlist`, `radiobutton`, `radioset`, `textarea`

### Display Widgets

`static`, `label`, `link`, `header`, `footer`, `rule`, `markdown`, `markdownviewer`, `richlog`, `log`, `pretty`, `digits`, `sparkline`, `progressbar`, `placeholder`, `loadingindicator`, `welcome`

### Complex Widgets

`tabbedcontent`, `tabpane`, `tabs`, `tab`, `datatable` (with `column`, `row`), `tree` (with `store`), `directorytree`, `listview`, `listitem`, `collapsible`, `contentswitcher`, `helppanel`, `keypanel`

### App Configuration

`css`, `binding`

### Components

`fieldset`, `form`, `app_shell` (with `content` slot)

## License

Apache License 2.0 — See [LICENSE](LICENSE) for details.

Copyright 2025 Softwell S.r.l.
