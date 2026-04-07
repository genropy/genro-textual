# Building the UI

The `main()` method is where you define your UI. It's a method on your `TextualApp` subclass that receives a `source` — a BuilderBag with Textual widget definitions.

## Basic Structure

```python
class MyApp(TextualApp):
    def main(self, source):
        source.header()
        source.static("Content goes here")
        source.footer()
```

Every builder call adds a node to the source Bag. The build step expands it, the renderer mounts it as a Textual widget.

## Containers and Layout

Containers return a reference for nesting:

```python
def main(self, source):
    main = source.horizontal()

    left = main.vertical()
    left.static("Left panel")

    right = main.vertical()
    right.static("Right panel")
```

Available containers: `vertical`, `horizontal`, `grid`, `center`, `middle`, `verticalscroll`, `horizontalscroll`, `scrollablecontainer`.

## Widgets

Leaf widgets don't have children:

```python
source.static("Display text")
source.input(value="^form.name", placeholder="Name")
source.button("Click me", variant="primary")
source.checkbox("Enable", value=True)
source.switch(value=False)
```

## CSS

Inline stylesheets in the main method:

```python
source.css("""
    #sidebar { width: 30; background: $surface; }
    .highlight { color: green; text-style: bold; }
""")
```

CSS variables (`$surface`, `$primary`, etc.) work in `source.css()`.

## Key Bindings

```python
source.binding(key="q", action="quit", description="Quit")
source.binding(key="f12", action="toggle_drawer", description="Inspector")
```

Bindings appear in the Footer widget and are clickable.

## Style Attributes

CSS properties can be set directly on widgets:

```python
source.vertical(id="drawer", width="^_system.drawer.width", display="^_system.drawer.display")
```

These are applied to `widget.styles` at mount time and are bindable with `^pointer`.

## Components

Reusable UI patterns defined with `@component`:

```python
source.fieldset(title="User Info")
form = source.form(title="Settings")
form.input(placeholder="Name")
form.checkbox("Active")
```

## Tabs

```python
tabs = source.tabbedcontent(initial="main")
tab1 = tabs.tabpane(title="Main", id="main")
tab1.static("Main content")
tab2 = tabs.tabpane(title="Settings", id="settings")
tab2.input(placeholder="Config")
```

## DataTable

```python
dt = source.datatable()
dt.column(label="Name")
dt.column(label="Age")
dt.row("Alice", "30")
dt.row("Bob", "25")
```

## Tree with Store

A Tree widget can display a Bag structure:

```python
source.tree(label="data", store=self.data)
```

The tree populates recursively from the Bag and updates when the Bag changes.
