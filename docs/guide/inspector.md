# Inspector

The built-in inspector lets you examine the three Bag structures of your app at runtime: Data, Source, and Compiled.

## Using app_shell

The easiest way to get the inspector is via the `app_shell` component:

```python
from genro_textual import TextualApp

class Application(TextualApp):
    def recipe(self, page):
        shell = page.app_shell(
            title="My App",
            data_store=self.data,
            source_store=self.source,
            compiled_store=self.compiled,
        )
        shell.content.static("^greeting")
        shell.content.input(value="^form.name", placeholder="Name")

    def setup(self):
        self._init_shell_data()
        self.data["greeting"] = "Hello!"
        self.data["form.name"] = "John"
        super().setup()
```

`app_shell` creates the full layout (header, content, drawer, footer) and exposes a `content` slot for your widgets.

## Opening the Inspector

Press **F12** to toggle the inspector drawer on the right side of the app.

## Inspector Layout

```text
┌─ Header ──────────────────────────────────────────────┐
│                              ┌─ Inspector ── [◀] [▶]  │
│                              │ [Data] [Source] [Comp]  │
│    Your App Content          │ ▼ form                  │
│                              │   name: John            │
│                              │   surname: Doe          │
│                              │ ▼ _system               │
│                              │   ▼ drawer              │
│                              │     width: 40           │
│                              │     display: block      │
└───────────────────────────────────────────────────────┘
```

## Three Tabs

- **Data** — The reactive data Bag. Shows current values, updates when data changes.
- **Source** — The source Bag (recipe output). Shows the UI structure as defined by builder calls.
- **Compiled** — The compiled Bag. Shows the structure after component expansion and pointer resolution.

## Resizing

Use the **◀** and **▶** arrows in the inspector top bar to resize the drawer.

## Store Parameters

The `data_store`, `source_store`, and `compiled_store` parameters are optional. Omit any to hide that tab:

```python
# Only show Data tab
shell = page.app_shell(title="My App", data_store=self.data)
```

Width and visibility are controlled via `_system` paths in the data Bag (initialized by `_init_shell_data()`).
