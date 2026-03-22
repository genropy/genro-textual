# genro-textual

**Declarative Terminal UI framework** built on [Textual](https://textual.textualize.io/) and powered by [genro-builders](https://github.com/softwell-srl/genro-builders).

Define your UI as a "recipe" — widgets, CSS, key bindings, data binding — all as Bag nodes. The compiler transforms the recipe into a live Textual app.

**Status: Pre-Alpha** - Active development.

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
        page.static("Hello, Textual!")
        page.button("Click me", variant="primary")

if __name__ == "__main__":
    Application().run()
```

## Architecture

genro-textual follows the **puppeteer/puppet** pattern:

- **TextualApp** (the puppeteer) — configures recipe, data, compiler. Creates and drives the LiveApp.
- **LiveApp** (the puppet) — a bare `textual.app.App` with no logic of its own. Built and controlled by the puppeteer.
- **CompiledBag** — the script. Produced by the compiler, kept in sync by the BindingManager.

**Everything goes through the Bag.** CSS, bindings, widgets, data binding — all declared in the recipe.

```text
┌──────────────┐     compile     ┌──────────────┐     render     ┌──────────────┐
│  Bag Recipe  │ ──────────────► │ CompiledBag  │ ─────────────► │   LiveApp    │
│  (widgets,   │                 │ (expanded,   │                │  (Textual    │
│   css,       │                 │  pointers    │                │   terminal)  │
│   bindings,  │                 │  resolved)   │                │              │
│   ^pointers) │                 │              │                │              │
└──────────────┘                 └──────────────┘                └──────────────┘
       ▲                                │                               │
       │                          BindingManager                        │
       │                          (data changes                         │
       │                           → node update                        │
       │                           → widget update)                     │
       │                                                                │
       └────────────────── Live REPL ───────────────────────────────────┘
```

## CSS and Bindings in Recipe

CSS and key bindings are **recipe elements**, not class attributes:

```python
class Application(TextualApp):
    def recipe(self, page):
        page.css("""
            .title { color: green; text-style: bold; }
            .info { color: $text-muted; }
        """)
        page.binding(key="q", action="quit", description="Quit")
        page.binding(key="d", action="toggle_dark", description="Dark mode")

        page.static("Hello!", classes="title")
        page.static("Press 'd' for dark mode", classes="info")
```

## Data Binding with ^pointer

Bind widget values to data using `^path` syntax:

```python
class Application(TextualApp):
    def recipe(self, page):
        page.css(".greeting { color: green; }")
        page.binding(key="q", action="quit", description="Quit")

        page.static("^greeting", classes="greeting")
        page.input(value="^form.name", placeholder="Your name")

    def setup(self):
        self.data["greeting"] = "Hello, World!"
        self.data["form.name"] = ""
        super().setup()
```

When `self.data["greeting"]` changes, the Static widget updates automatically. When the user types in the Input, the value flows back to `self.data["form.name"]`.

## Complete Example: Dashboard App

```python
from genro_textual import TextualApp

class Application(TextualApp):
    def recipe(self, page):
        page.header(show_clock=True, icon="📦")

        tabs = page.tabbedcontent(initial="dashboard")

        # === Dashboard ===
        dashboard = tabs.tabpane(title="Dashboard", id="dashboard")
        dashboard.static("System Overview")
        dashboard.progressbar(total=100, show_percentage=True)
        dashboard.rule()
        dashboard.button("Refresh", variant="primary")

        # === Settings ===
        settings = tabs.tabpane(title="Settings", id="settings")
        settings.static("Application Settings")
        settings.input(placeholder="Application Name")
        settings.checkbox("Auto-save", value=True)
        settings.checkbox("Dark mode", value=True)

        page.footer(show_command_palette=True)
```

## Components

Reusable UI blocks defined with `@component`. Use a mixin to extend the builder:

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
>>> app.page.static("Hello from REPL!")
>>> app.page.button("New Button", variant="warning")
```

## CLI Reference

| Command | Description |
| ------- | ----------- |
| `pygui run FILE.py` | Run a TextualApp |
| `pygui run -r FILE.py` | Run with **auto-reload** (watches for file changes) |
| `pygui run -c FILE.py` | Run and **connect REPL** |
| `pygui list` | List registered running apps |
| `pygui connect NAME` | Connect REPL to a running app |

## Supported Widgets

genro-textual supports **60+ Textual elements**:

### Containers

`container`, `vertical`, `horizontal`, `center`, `middle`, `grid`, `verticalscroll`, `horizontalscroll`, `scrollablecontainer`, `verticalgroup`, `horizontalgroup`, `itemgrid`

### Input Widgets

`button`, `checkbox`, `input`, `maskedinput`, `switch`, `select`, `selectionlist`, `optionlist`, `radiobutton`, `radioset`, `textarea`

### Display Widgets

`static`, `label`, `link`, `header`, `footer`, `rule`, `markdown`, `markdownviewer`, `richlog`, `log`, `pretty`, `digits`, `sparkline`, `progressbar`, `placeholder`, `loadingindicator`, `welcome`

### Complex Widgets

`tabbedcontent`, `tabpane`, `tabs`, `tab`, `datatable` (with `column`, `row`), `tree`, `directorytree`, `listview`, `listitem`, `collapsible`, `contentswitcher`, `helppanel`, `keypanel`

### App Configuration

`css`, `binding`

### Components

`fieldset`, `form`

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

Copyright 2025 Softwell S.r.l.
