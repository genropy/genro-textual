# Recipe

The recipe is where you define your UI. It's a method on your `TextualApp` subclass that receives a `page` — a BuilderBag with Textual widget definitions.

## Basic Structure

```python
class MyApp(TextualApp):
    def recipe(self, page):
        page.header()
        page.static("Content goes here")
        page.footer()
```

Every builder call adds a node to the source Bag. The compiler expands it, the renderer mounts it as a Textual widget.

## Containers and Layout

Containers return a reference for nesting:

```python
def recipe(self, page):
    main = page.horizontal()

    left = main.vertical()
    left.static("Left panel")

    right = main.vertical()
    right.static("Right panel")
```

Available containers: `vertical`, `horizontal`, `grid`, `center`, `middle`, `verticalscroll`, `horizontalscroll`, `scrollablecontainer`.

## Widgets

Leaf widgets don't have children:

```python
page.static("Display text")
page.input(value="^form.name", placeholder="Name")
page.button("Click me", variant="primary")
page.checkbox("Enable", value=True)
page.switch(value=False)
```

## CSS

Inline stylesheets in the recipe:

```python
page.css("""
    #sidebar { width: 30; background: $surface; }
    .highlight { color: green; text-style: bold; }
""")
```

CSS variables (`$surface`, `$primary`, etc.) work in `page.css()`.

## Key Bindings

```python
page.binding(key="q", action="quit", description="Quit")
page.binding(key="f12", action="toggle_drawer", description="Inspector")
```

Bindings appear in the Footer widget and are clickable.

## Style Attributes

CSS properties can be set directly on widgets:

```python
page.vertical(id="drawer", width="^_system.drawer.width", display="^_system.drawer.display")
```

These are applied to `widget.styles` at mount time and are bindable with `^pointer`.

## Components

Reusable UI patterns defined with `@component`:

```python
page.fieldset(title="User Info")
form = page.form(title="Settings")
form.input(placeholder="Name")
form.checkbox("Active")
```

## Tabs

```python
tabs = page.tabbedcontent(initial="main")
tab1 = tabs.tabpane(title="Main", id="main")
tab1.static("Main content")
tab2 = tabs.tabpane(title="Settings", id="settings")
tab2.input(placeholder="Config")
```

## DataTable

```python
dt = page.datatable()
dt.column(label="Name")
dt.column(label="Age")
dt.row("Alice", "30")
dt.row("Bob", "25")
```

## Tree with Store

A Tree widget can display a Bag structure:

```python
page.tree(label="data", store=self.data)
```

The tree populates recursively from the Bag and updates when the Bag changes.
