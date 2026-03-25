# Genro Textual

[![GitHub](https://img.shields.io/badge/GitHub-genro--textual-blue?logo=github)](https://github.com/genropy/genro-textual)

A **declarative TUI framework** that builds terminal interfaces from [Bag](https://genro-bag.readthedocs.io) structures using [Textual](https://textual.textualize.io) as the rendering engine.

## The Idea

Instead of writing imperative widget code, you describe your UI in a **recipe** — a series of builder calls that create a Bag structure. The framework compiles this structure and renders it as a Textual application.

```python
from genro_textual import TextualApp

class MyApp(TextualApp):
    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.static("^greeting")
        page.input(value="^form.name", placeholder="Your name")

    def setup(self):
        self.data["greeting"] = "Hello, World!"
        self.data["form.name"] = ""
        super().setup()

if __name__ == "__main__":
    MyApp().run()
```

## Key Concepts

- **Recipe** — Declare your UI structure with builder calls
- **Bag-driven** — All state lives in Bag structures (data, source, compiled)
- **Reactive binding** — `^pointer` syntax binds widgets to data paths
- **Bidirectional** — Input widgets write back to data on blur
- **CSS in recipe** — Inline stylesheets via `page.css()`
- **Puppeteer/Puppet** — TextualApp (logic) drives LiveApp (rendering)

## Architecture

```mermaid
graph LR
    R[Recipe] --> S[Source Bag]
    S --> C[Compiler]
    C --> CB[Compiled Bag]
    CB --> RE[Renderer]
    RE --> W[Widget Tree]
    D[Data Bag] -.->|binding| CB
    W -.->|blur/change| D
```

---

**Next:** [Getting Started](getting-started.md) — Build your first app in 5 minutes

```{toctree}
:maxdepth: 1
:caption: Start Here
:hidden:

getting-started
```

```{toctree}
:maxdepth: 2
:caption: Guide
:hidden:

guide/recipe
guide/data-binding
guide/css-and-styles
guide/widgets
guide/inspector
guide/cli
```

```{toctree}
:maxdepth: 2
:caption: Architecture
:hidden:

architecture
```

```{toctree}
:maxdepth: 1
:caption: Reference
:hidden:

reference/api
reference/widgets
```
