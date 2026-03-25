# Getting Started

## Installation

```bash
pip install genro-textual
```

## Your First App

Create a file `hello.py`:

```python
from genro_textual import TextualApp

class Application(TextualApp):
    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.static("Hello, Textual!")
        page.static("Press 'q' to quit")

if __name__ == "__main__":
    Application().run()
```

Run it:

```bash
python hello.py
```

## Adding Data Binding

The `^pointer` syntax binds a widget to a path in the data Bag:

```python
class Application(TextualApp):
    def recipe(self, page):
        page.binding(key="q", action="quit", description="Quit")
        page.input(value="^form.name", placeholder="Your name")
        page.static("^form.name")

    def setup(self):
        self.data["form.name"] = "World"
        super().setup()
```

- The Input shows "World" initially
- When you edit the Input and press Tab, the Static updates
- Everything goes through the data Bag

## Adding CSS

Style your app with inline CSS in the recipe:

```python
def recipe(self, page):
    page.css("""
        .greeting { color: green; text-style: bold; }
        .info { color: $text-muted; }
    """)
    page.binding(key="q", action="quit", description="Quit")
    page.static("^greeting", classes="greeting")
    page.static("Type below:", classes="info")
    page.input(value="^form.name", placeholder="Name")
```

## Using the CLI

The `pygui` command provides tools for running and managing apps:

```bash
# Run an app
pygui run hello.py

# Run with auto-reload on file changes
pygui run -r hello.py

# Run with REPL in tmux split
pygui run -c hello.py

# List running apps
pygui list

# Connect REPL to a running app
pygui connect hello

# Stop a running app
pygui stop hello
```

## Next Steps

- [Recipe Guide](guide/recipe.md) — Builder calls, containers, layout
- [Data Binding](guide/data-binding.md) — Pointers, bidirectional binding, anti-loop
- [Widgets Reference](reference/widgets.md) — All 61+ supported widgets
