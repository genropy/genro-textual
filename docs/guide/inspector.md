# Inspector

The built-in inspector lets you examine the three Bag structures of your app at runtime: Data, Source, and Compiled.

## Opening the Inspector

Press **F12** to toggle the inspector drawer on the right side of the app.

## Inspector Layout

```
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

## Implementation

The inspector is built entirely with the recipe pattern:

```python
drawer = main.vertical(id="drawer", width="^_system.drawer.width", display="^_system.drawer.display")

tabs = drawer.tabbedcontent()
data_tab = tabs.tabpane(title="Data")
data_tab.tree(label="data", store=self.data)
```

Width and visibility are controlled via `_system` paths in the data Bag.
