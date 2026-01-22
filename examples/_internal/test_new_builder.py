# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Test the new TextualBuilder with mixed widgets and containers.

Run with:
    PYTHONPATH=src python examples/test_new_builder.py
"""

from __future__ import annotations

from genro_bag import Bag

from genro_textual.textual_builder import TextualBuilder


def test_schema():
    """Test that schema is generated correctly."""
    bag = Bag(builder=TextualBuilder)

    # Check some widgets exist in schema
    for name in ["button", "input", "static", "tabbedcontent", "tabpane", "collapsible"]:
        info = bag.builder.get_schema_info(name)
        print(f"{name}: sub_tags={info.get('sub_tags', 'ANY')}")


def test_build():
    """Test building a UI with mixed widgets and containers."""
    bag = Bag(builder=TextualBuilder)

    # Simple widgets
    bag.static("Welcome to the Test App")
    bag.button("Click Me", variant="primary")
    bag.input(placeholder="Enter your name...")

    # Container with children using path notation
    options = bag.collapsible(title="More Options")
    options.checkbox(label="Option 1", value=True)
    options.checkbox(label="Option 2")
    options.switch(value=False)

    # Tabs using path notation
    tabs = bag.tabbedcontent()
    tab1 = tabs.tabpane(title="Tab 1")
    tab1.static("Content of Tab 1")
    tab1.button("Button in Tab 1")
    tab2 = tabs.tabpane(title="Tab 2")
    tab2.static("Content of Tab 2")
    tab2.input(placeholder="Input in Tab 2")

    print("\nBag structure:")
    print(bag.to_xml())

    return bag


if __name__ == "__main__":
    print("=== Testing Schema ===")
    test_schema()

    print("\n=== Testing Build ===")
    test_build()
