# CSS and Styles

Genro Textual supports Textual's CSS for styling, both as inline stylesheets and as direct widget attributes.

## Inline CSS

Use `page.css()` in the recipe for stylesheets:

```python
page.css("""
    #sidebar { width: 30; background: $surface; border-left: solid $primary; }
    .title { color: green; text-style: bold; margin: 1 0; }
    .muted { color: $text-muted; }
""")
```

CSS variables (`$surface`, `$primary`, `$text`, `$error`, etc.) are Textual theme variables — they work only in `page.css()`, not in direct attribute assignment.

## Direct Style Attributes

Set CSS properties directly on widgets:

```python
page.vertical(id="panel", width=40, display="block")
page.static("Bold text", color="green", background="red")
```

At mount time, the compiler classifies each attribute:
1. **Constructor parameter** → passed to widget `__init__`
2. **CSS property** → applied to `widget.styles`
3. **Reactive attribute** → applied to widget via `set_reactive`

## Bindable Styles

Direct style attributes support `^pointer` binding:

```python
page.vertical(width="^_system.panel.width")
```

When `data["_system.panel.width"]` changes, the width updates.

Note: CSS variables (`$surface`) cannot be used in direct attributes — only in `page.css()`.

## Supported CSS Properties

All Textual CSS properties are supported as direct attributes:

| Property | Example |
|----------|---------|
| `width`, `height` | `width=40`, `height="1fr"` |
| `min_width`, `max_width` | `min_width=20` |
| `color`, `background` | `color="green"` |
| `display` | `display="block"`, `display="none"` |
| `dock` | `dock="right"` |
| `padding`, `margin` | `padding=(1, 2)` |
| `opacity` | `opacity=0.5` |
| `position` | `position="absolute"` |

## Classes and IDs

```python
page.static("Text", id="my-label", classes="title highlight")
```

IDs and classes are used for CSS selector targeting.
