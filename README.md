# genro-textual

Textual UI framework for Genro Bag-driven applications, built with [Textual](https://textual.textualize.io/).

## Status

**Development Status: Pre-Alpha** - Early exploration and POC phase.

## Purpose

Provide a declarative, Bag-driven framework for building terminal UIs:
- Define UI as a "recipe" using Bag methods
- Automatic compilation to Textual widgets
- Remote control via REPL
- Live updates and hot reload

## Installation

```bash
pip install genro-textual
```

## Quick Start

```python
from genro_textual import TextualApp

class Application(TextualApp):
    def recipe(self, root):
        root.static("Hello, Textual!")
        root.button("Click me", variant="primary")

if __name__ == "__main__":
    Application().run()
```

## CLI

```bash
# Run an app
pygui run examples/basic/hello_world.py

# Run with auto-reload
pygui run examples/basic/hello_world.py -r

# Run and connect REPL
pygui run examples/basic/hello_world.py -c

# List running apps
pygui list

# Connect to running app
pygui connect hello_world
```

## Features

- [x] Declarative UI with Bag
- [x] All Textual widgets supported
- [x] TabbedContent/TabPane
- [x] DataTable with columns/rows
- [x] Remote REPL control
- [x] Hot reload
- [ ] Data binding
- [ ] FormulaResolver integration

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.
