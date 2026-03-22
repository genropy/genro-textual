# Architecture

## Puppeteer and Puppet

genro-textual follows a strict separation between configuration and execution:

- **TextualApp** (puppeteer) — extends `BagAppBase`. Owns recipe, data, builder, compiler, binding. Creates and drives the LiveApp.
- **LiveApp** (puppet) — extends `textual.app.App`. No logic of its own. Built and controlled by the puppeteer.
- **CompiledBag** — the script. Produced by the compiler, kept in sync by BindingManager.

## Pipeline

```
recipe(page)         →  Source Bag (widgets, css, bindings, ^pointers)
    ↓ compile()
_materialize()       →  Static Bag (components expanded)
    ↓ bind()
BindingManager       →  Bound Bag (pointers resolved, subscriptions active)
    ↓ render()
TextualCompiler      →  Widget tree mounted on LiveApp
```

## Modules

### textual_builder.py

`TextualWidgetsMixin` + `TextualBuilder(TextualWidgetsMixin, BagBuilderBase)`

All `@element` and `@component` definitions live in the mixin. This enables
subclass inheritance: a user can create `MyBuilder(MyMixin, TextualBuilder)`
and inherit the full schema.

Elements include:
- **Containers**: vertical, horizontal, grid, center, etc.
- **Widgets**: static, button, input, checkbox, datatable, tabs, etc.
- **App config**: css, binding (not rendered as widgets)
- **Components**: fieldset, form (expanded at compile time)

### textual_compiler.py

`TextualCompiler(BagCompilerBase)`

Inherits `compile()` from base (materialize + resolve pointers).
Defines its own `render(compiled_bag, live_app)`:

1. Extract `css` nodes → apply to `live_app.stylesheet`
2. Extract `binding` nodes → call `live_app.bind()`
3. Render remaining nodes as Textual widgets via `_render_node()`

Dispatch: `_render_<tag>` methods for special widgets (tabbedcontent,
datatable, static), `_render_default` for generic widgets via
compile_kwargs (module + class).

Materialized components without compile_class are transparent:
their children render directly into the parent.

### textual_app.py

`TextualApp(BagAppBase)` — the puppeteer.

- `page` property exposes `_store` (domain name for Textual)
- `recipe(page)` — user override
- `render(compiled_bag)` — mounts widgets via `compiler.render()`
- `_on_node_updated(node)` — reactive: updates specific widget, thread-safe via `call_from_thread`
- `_on_widget_changed(widget, value)` — bidirectional: widget → data, with anti-loop guard
- `run()` — creates LiveApp and starts Textual event loop

`LiveApp(App)` — the puppet.

- `compose()` → root Vertical container
- `on_mount()` → `owner.setup()` (recipe + compile + bind + render)
- All events delegated to owner

## Data Binding

### Data → Widget (^pointer)

```python
def recipe(self, page):
    page.static("^greeting")     # value bound to data["greeting"]
    page.input(value="^form.name")  # attr bound to data["form.name"]
```

Flow: `data["greeting"] = "Hello"` → BindingManager → node.value updated → `_on_node_updated` → `widget.update("Hello")`

### Widget → Data (bidirectional)

When user types in Input: `LiveApp.on_input_changed` → `owner._on_widget_changed` → writes to data Bag.

Anti-loop guard: `_updating_from_widget` flag prevents the cycle
widget → data → binding → widget.

## Extending the Builder

Use mixins (not subclasses) to add custom elements:

```python
class MyMixin:
    @component(sub_tags="")
    def login_form(self, comp, **kwargs):
        comp.input(placeholder="Username")
        comp.button("Login")

class MyBuilder(MyMixin, TextualBuilder):
    pass

class MyApp(TextualApp):
    builder_class = MyBuilder
```

The mixin pattern works because `_pop_decorated_methods` collects
decorators from non-BagBuilderBase bases in the MRO.
