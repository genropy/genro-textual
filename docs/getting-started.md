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
    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.static("Hello, Textual!")
        source.static("Press 'q' to quit")

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
    def main(self, source):
        source.binding(key="q", action="quit", description="Quit")
        source.input(value="^form.name", placeholder="Your name")
        source.static("^form.name")

    def store(self, data):
        data["form.name"] = "World"
```

- The Input shows "World" initially
- When you edit the Input and press Tab, the Static updates
- Everything goes through the data Bag

## Adding CSS

Style your app with inline CSS in the main method:

```python
def main(self, source):
    source.css("""
        .greeting { color: green; text-style: bold; }
        .info { color: $text-muted; }
    """)
    source.binding(key="q", action="quit", description="Quit")
    source.static("^greeting", classes="greeting")
    source.static("Type below:", classes="info")
    source.input(value="^form.name", placeholder="Name")
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

- [Building the UI](guide/building-ui.md) — Builder calls, containers, layout
- [Data Binding](guide/data-binding.md) — Pointers, bidirectional binding, anti-loop
- [Widgets Reference](reference/widgets.md) — All 61+ supported widgets
