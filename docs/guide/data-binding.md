# Data Binding

Genro Textual uses `^pointer` syntax to bind widgets to paths in the data Bag. When data changes, widgets update. When widgets change, data updates.

## Read Binding (Data → Widget)

Use `^path` in any value or attribute:

```python
source.static("^user.name")              # value bound to data["user.name"]
source.input(value="^form.email")        # attr bound to data["form.email"]
```

When `data["user.name"]` changes, the Static updates automatically.

## Write Binding (Widget → Data)

Input widgets write back to data:

- **Input**: writes on **blur** (when focus leaves the field), not on every keystroke
- **Checkbox/Switch**: writes on **change** (immediate)

```python
source.input(value="^form.name")    # writes data["form.name"] on blur
source.checkbox(value="^settings.dark_mode")  # writes immediately
```

## Anti-Loop

When a widget writes to data, the data Bag notifies all subscribers — including the widget that wrote. The `_reason` mechanism prevents infinite loops:

1. Widget writes to data with `_reason=compiled_node_path`
2. BindingManager receives the notification
3. For each subscriber: if `compiled_path == reason`, skip (it's the originator)
4. All other subscribers update normally

## Subscription Map

The binding uses a flat subscription map:

```python
{
    "form.name": ["horizontal_0.verticalscroll_0.input_0?value",
                   "horizontal_0.verticalscroll_0.static_2"],
    "settings.dark_mode": ["checkbox_5?value"],
}
```

- Key: data path
- Value: list of built node paths (with optional `?attr` suffix)

## CSS Property Binding

CSS properties can be bound to data paths:

```python
source.vertical(id="panel", width="^_system.panel.width")
```

When `data["_system.panel.width"]` changes, `widget.styles.width` updates.

## Setup Order

Data must be initialized in the `store()` method:

```python
def store(self, data):
    data["form.name"] = "John"     # set initial values
    data["form.email"] = ""
```

The lifecycle is: `store(data)` → `main(source)` → `build()` → `subscribe()` → `render`.
