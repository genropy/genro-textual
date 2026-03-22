# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""DataTable example with columns and rows.

Run with:
    textual run examples/widgets/datatable.py

Shows how to create a DataTable with column and row definitions.
"""

from genro_textual import TextualApp


class Application(TextualApp):
    """DataTable with columns and rows defined in Bag."""

    def recipe(self, page):
        page.css("DataTable { height: 1fr; }")

        page.static("DataTable Example")

        table = page.datatable(id="users-table", zebra_stripes=True)
        table.column("Name", key="name")
        table.column("Age", key="age")
        table.column("City", key="city")
        table.column("Role", key="role")

        table.row(["Alice", 30, "Rome", "Developer"], key="r1")
        table.row(["Bob", 25, "Milan", "Designer"], key="r2")
        table.row(["Charlie", 35, "Naples", "Manager"], key="r3")
        table.row(["Diana", 28, "Turin", "Developer"], key="r4")
        table.row(["Eve", 32, "Florence", "Analyst"], key="r5")

        page.static("Press 'q' to quit")
