# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Foundation mixin: app_shell component with named slots.

Provides the standard application layout: header, scrollable content area,
resizable inspector drawer with Data/Source/Compiled tree tabs, and footer.

Usage in main::

    def main(self, source):
        shell = source.app_shell(
            title="My App",
            data_store=self.data,
            source_store=self.source,
            compiled_store=self.compiled,
        )
        shell.content.static("Hello!")
        shell.content.input(value="^form.name")
"""
from __future__ import annotations

from genro_builders.builder import component


class FoundationMixin:
    """Builder mixin: app_shell component with inspector drawer."""

    @component(sub_tags="*", slots=["content"])
    def app_shell(
        self,
        comp,
        title: str = "App",
        data_store: object | None = None,
        source_store: object | None = None,
        compiled_store: object | None = None,
        **kwargs,
    ):
        """Application shell: header, content, inspector drawer, footer.

        Returns dict mapping slot 'content' to the #shell-content node,
        so user widgets are mounted inside the scrollable content area.

        Args:
            comp: The component's internal Bag (populated at compile time).
            title: Title shown in the header bar.
            data_store: Bag for the Data inspector tab.
            source_store: Bag for the Source inspector tab.
            compiled_store: Bag for the Compiled inspector tab.
        """
        comp.css("""
            #shell-header {
                height: 1; background: $primary; color: $text;
            }
            #shell-header Static { width: 1fr; padding: 0 1; }
            #shell-main { height: 1fr; }
            #shell-content { width: 1fr; }
            #shell-drawer {
                background: $surface;
                border-left: solid $primary;
            }
            #drawer-topbar {
                height: 1; background: $primary-darken-2;
            }
            #drawer-title {
                width: 1fr; padding: 0 1; color: $text;
            }
            .drawer-btn {
                min-width: 3; height: 1; border: none;
                padding: 0; background: transparent;
                color: $text-muted;
            }
            .drawer-btn:hover {
                color: $text; background: transparent;
            }
        """)
        comp.binding(key="q", action="quit", description="Quit")
        comp.binding(
            key="f12", action="toggle_drawer",
            description="Inspector",
        )

        header = comp.horizontal(id="shell-header")
        header.static(title)

        main = comp.horizontal(id="shell-main")

        content_node = main.verticalscroll(id="shell-content")

        drawer = main.vertical(
            id="shell-drawer",
            width="^_system.drawer.width",
            display="^_system.drawer.display",
        )
        topbar = drawer.horizontal(id="drawer-topbar")
        topbar.static("Inspector", id="drawer-title")
        topbar.button(
            "\u25c0", id="btn-drawer-expand",
            classes="drawer-btn",
        )
        topbar.button(
            "\u25b6", id="btn-drawer-shrink",
            classes="drawer-btn",
        )

        tabs = drawer.tabbedcontent()
        if data_store is not None:
            tabs.tabpane(title="Data", id="tab-data").tree(
                label="data", store=data_store,
            )
        if source_store is not None:
            tabs.tabpane(title="Source", id="tab-source").tree(
                label="source", store=source_store,
            )
        if compiled_store is not None:
            tabs.tabpane(
                title="Compiled", id="tab-compiled",
            ).tree(label="compiled", store=compiled_store)

        comp.footer(show_command_palette=False)

        return {"content": content_node}
