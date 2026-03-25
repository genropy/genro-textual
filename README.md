# genro-textual

**Declarative Terminal UI framework** built on [Textual](https://textual.textualize.io/) and powered by [genro-builders](https://github.com/genropy/genro-builders).

Define your UI as a "recipe" — widgets, CSS, key bindings, data binding — all as Bag nodes. The compiler transforms the recipe into a live Textual app with reactive data binding.

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
    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.static("^greeting")
        page.input(value="^form.name", placeholder="Your name")
        page.button("OK")

    def setup(self):
        self.data["greeting"] = "Hello, World!"
        self.data["form.name"] = ""
        super().setup()

if __name__ == "__main__":
    Application().run()
```

Type a name in the input, press Tab — the greeting doesn't change (it's on a different path), but the data Bag updates. Bind the Static and Input to the same path to see reactive updates.

## Architecture

genro-textual follows the **puppeteer/puppet** pattern:

- **TextualApp** (the puppeteer) — configures recipe, data, compiler
- **LiveApp** (the puppet) — a bare `textual.app.App` driven by the puppeteer
- **CompiledBag** — the script, kept in sync by the BindingManager

```text
┌──────────────┐     compile     ┌──────────────┐     render     ┌──────────────┐
│  Source Bag   │ ──────────────► │ Compiled Bag │ ─────────────► │   LiveApp    │
│  (recipe)     │                 │ (expanded,   │                │  (Textual)   │
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
page.static("^user.name")              # value bound to data path
page.input(value="^form.email")        # attribute bound to data path
```

When `data["user.name"]` changes, the Static updates automatically.

### Write: Widget to Data

- **Input** — writes to data on **blur** (Tab, click away), not on every keystroke
- **Checkbox / Switch** — writes to data on **change** (immediate)

The `_reason` mechanism prevents infinite loops: when a widget writes to data, the BindingManager skips updating that same widget.

### Bidirectional Example

```python
class Application(TextualApp):
    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.input(value="^form.name", placeholder="Name")
        page.input(value="^form.surname", placeholder="Surname")
        page.static("^form.name")       # updates when Input blurs
        page.static("^form.surname")
        page.button("OK")

    def setup(self):
        self.data["form.name"] = "John"
        self.data["form.surname"] = "Doe"
        super().setup()
```

## CSS

### Inline Stylesheets

CSS in the recipe, with Textual theme variables:

```python
page.css("""
    .title { color: green; text-style: bold; }
    #sidebar { width: 30; background: $surface; border-left: solid $primary; }
""")
```

### Direct Style Attributes

CSS properties can be set directly on widgets and bound to data:

```python
page.vertical(id="panel", width="^_system.panel.width", display="^_system.panel.display")
```

When `data["_system.panel.width"]` changes, the widget resizes. Style attributes are classified automatically at mount time:

1. Constructor parameters → `widget.__init__`
2. CSS properties → `widget.styles`
3. Reactive attributes → `widget.set_reactive`

Note: CSS variables (`$surface`, `$primary`) work only in `page.css()`, not in direct attributes.

## Inspector Drawer

Built-in inspector for debugging Bag structures at runtime:

```python
class Application(TextualApp):
    def recipe(self, page):
        page.header()
        main = page.horizontal(id="main-area")

        content = main.verticalscroll(id="main-content")
        content.static("My app content")

        # Drawer with inspector
        drawer = main.vertical(
            id="drawer",
            width="^_system.drawer.width",
            display="^_system.drawer.display",
        )
        tabs = drawer.tabbedcontent()
        tabs.tabpane(title="Data").tree(label="data", store=self.data)
        tabs.tabpane(title="Source").tree(label="source", store=self.source)
        tabs.tabpane(title="Compiled").tree(label="compiled", store=self.compiled)

        page.footer()
```

The Tree widget with `store` attribute populates recursively from a Bag and updates reactively when the Bag changes, preserving expanded state.

Use `_system` paths for infrastructure data (drawer width, display) to separate them from application data.

## Key Bindings

```python
page.binding(key="q", action="quit", description="Quit")
page.binding(key="f12", action="toggle_drawer", description="Inspector")
```

Bindings appear in the Footer and are clickable.

## Components

Reusable UI blocks defined with `@component`:

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

    def recipe(self, page):
        page.login_form(title="Sign In")
```

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

`fieldset`, `form`

## License

Apache License 2.0 — See [LICENSE](LICENSE) for details.

Copyright 2025 Softwell S.r.l.
