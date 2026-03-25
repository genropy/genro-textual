# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Builder component mixins for genro-textual.

Each mixin defines @component methods that can be composed into a builder
via MRO. TextualBuilder includes FoundationMixin by default.

To add custom components, create a mixin and compose it::

    from genro_textual.components.foundation import FoundationMixin

    class MyMixin:
        @component(sub_tags="")
        def login_form(self, comp, **kwargs):
            comp.input(placeholder="Username")
            comp.button("Login")

    class MyBuilder(MyMixin, TextualBuilder):
        pass
"""
from genro_textual.components.foundation import FoundationMixin

__all__ = ["FoundationMixin"]
