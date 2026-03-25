# CLI — pygui

The `pygui` command-line tool manages genro-textual applications.

## Commands

### Run

```bash
pygui run app.py
```

Options:
- `-c, --connect` — Run in background + connect REPL in tmux split
- `-r, --reload` — Watch file changes and auto-reload

### List

```bash
pygui list
```

Shows running apps with port and status (alive/dead). Cleans up dead entries.

### Connect

```bash
pygui connect app_name
```

Opens a REPL connected to a running app. Special commands:
- `/help` — Show available commands
- `/keys` — List page keys
- `/quit` — Disconnect

### Stop

```bash
pygui stop app_name
```

Graceful shutdown via remote protocol. Kills tmux session if exists.

### Completions

```bash
pygui completions zsh
```

Generate shell completions (zsh supported).

## Tmux Integration

With `-c` flag, `pygui run` creates a tmux session with:
- Top pane: TUI application
- Bottom pane: REPL (30% height)
- Mouse enabled, focus on TUI pane

## Remote REPL

When connected, you have access to the app:

```python
>>> app.data["form.name"] = "New value"
>>> app.page.static("Added from REPL!")
```
