# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Complex application showcasing Textual widgets with Exit button.

Run with CLI:
    textual run examples/complex_app.py

Connect with REPL:
    textual connect complex_app
    >>> app.page.static("Added from REPL!")
"""

from __future__ import annotations

from genro_textual import TextualApp


class Application(TextualApp):
    """Complex application with tabs, forms, and Exit button."""

    def recipe(self, page):
        page.header(show_clock=True, icon="📦")

        tabs = page.tabbedcontent(initial="dashboard")

        # === Dashboard ===
        dashboard = tabs.tabpane(title="Dashboard", id="dashboard")
        dashboard.static("System Overview")
        dashboard.progressbar(total=100, show_percentage=True, id="cpu-progress")
        dashboard.rule()
        dashboard.static("Quick Actions")
        dashboard.button("Refresh", variant="primary", id="btn-refresh")
        dashboard.button("Export", variant="success", id="btn-export")

        # === Files ===
        files = tabs.tabpane(title="Files", id="files")
        files.static("File Browser")
        files.directorytree(path=".", id="file-tree")
        files.rule()
        details = files.collapsible(title="File Details", collapsed=False)
        details.static("Name: -", id="file-name")
        details.static("Size: -", id="file-size")

        # === Settings ===
        settings = tabs.tabpane(title="Settings", id="settings")
        settings.static("Application Settings")
        settings.input(placeholder="Application Name", id="app-name")
        settings.checkbox("Auto-save", value=True, id="chk-autosave")
        settings.checkbox("Dark mode", value=True, id="chk-darkmode")
        settings.rule()
        settings.button("Save", variant="primary", id="btn-save")

        # === Exit button in footer area ===
        page.rule()
        page.button("Exit Application", variant="error", id="btn-exit")
        page.footer(show_command_palette=True)
