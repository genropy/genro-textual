# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Pilot smoke tests for the live Textual rendering pipeline.

Drive each example through Textual's ``App.run_test()`` (headless
pilot mode): a real event loop, real mount, real compose — but no
terminal. After mount we assert the shape of the resulting widget
tree.

These tests catch regressions in the live render path that pure-XML
tests cannot, e.g. compose-time race conditions on TabbedContent or
DataTable storage allocation.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _load_example(rel_path: str) -> Any:
    """Load an example module by relative path from examples/."""
    path = EXAMPLES_DIR / rel_path
    spec = importlib.util.spec_from_file_location(f"_ex_{path.stem}", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


async def _pilot(rel_path: str) -> tuple[Any, Any]:
    """Instantiate the example app and run it through Textual pilot.

    Returns (live_app, root). The caller is responsible for any
    extra assertions and for letting the context manager close.
    """
    mod = _load_example(rel_path)
    app = mod.Application()
    live = app.as_textual_app()
    return app, live


# ----------------------------------------------------------------------
# Basic examples — leaf widgets, containers, layout
# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pilot_hello_world():
    """hello_world.py mounts two Static widgets under root."""
    from textual.widgets import Static
    _, live = await _pilot("basic/hello_world.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        statics = list(live.root.query(Static))
        assert len(statics) == 2


@pytest.mark.asyncio
async def test_pilot_nested_containers():
    """nested_containers.py: Static + Container with Static + Button inside."""
    from textual.containers import Container
    from textual.widgets import Button, Static
    _, live = await _pilot("basic/nested_containers.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        assert len(list(live.root.query(Container))) == 1
        assert len(list(live.root.query(Static))) >= 2
        assert len(list(live.root.query(Button))) == 1


@pytest.mark.asyncio
async def test_pilot_button_variants():
    """button_variants.py: 5 Button widgets all mounted."""
    from textual.widgets import Button
    _, live = await _pilot("basic/button_variants.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        buttons = list(live.root.query(Button))
        assert len(buttons) == 5


# ----------------------------------------------------------------------
# Widgets that populate post-mount via call_after_refresh
# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pilot_datatable_populates_post_mount():
    """datatable.py: DataTable has 4 columns and 5 rows after mount."""
    from textual.widgets import DataTable
    _, live = await _pilot("widgets/datatable.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()  # let call_after_refresh fire
        tables = list(live.root.query(DataTable))
        assert len(tables) == 1
        dt = tables[0]
        assert len(dt.columns) == 4
        assert dt.row_count == 5


# ----------------------------------------------------------------------
# TabbedContent — used to race against Textual's async compose
# ----------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pilot_tabs_three_panes_first_active():
    """tabs.py: TabbedContent with 3 TabPane, initial tab is 'overview'."""
    from textual.widgets import TabbedContent, TabPane
    _, live = await _pilot("widgets/tabs.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        tcs = list(live.root.query(TabbedContent))
        tps = list(live.root.query(TabPane))
        assert len(tcs) == 1
        assert len(tps) == 3
        assert tcs[0].active == "overview"


@pytest.mark.asyncio
async def test_pilot_showcase_full_tree():
    """showcase.py: TabbedContent with 4 panes containing many widgets."""
    from textual.widgets import Button, Static, TabbedContent, TabPane
    _, live = await _pilot("showcase.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        assert len(list(live.root.query(TabbedContent))) == 1
        assert len(list(live.root.query(TabPane))) == 4
        # showcase has at least the 5 button variants
        assert len(list(live.root.query(Button))) >= 5
        # and several Static widgets across the tabs
        assert len(list(live.root.query(Static))) >= 10


@pytest.mark.asyncio
async def test_pilot_complex_app_dashboard_active():
    """complex_app.py: TabbedContent with 3 panes, dashboard active first."""
    from textual.widgets import TabbedContent, TabPane
    _, live = await _pilot("complex_app.py")
    async with live.run_test() as pilot:
        await pilot.pause()
        await pilot.pause()
        tcs = list(live.root.query(TabbedContent))
        tps = list(live.root.query(TabPane))
        assert len(tcs) == 1
        assert len(tps) == 3
        assert tcs[0].active == "dashboard"
