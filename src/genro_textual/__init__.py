# Copyright 2025 Softwell S.r.l. - SPDX-License-Identifier: Apache-2.0
"""Textual UI framework for Genro Bag-driven applications."""

from genro_textual.remote import connect
from genro_textual.textual_app import TextualApp
from genro_textual.textual_builder import TextualBuilder
from genro_textual.textual_renderer import TextualRenderer

__all__ = ["TextualApp", "TextualBuilder", "TextualRenderer", "connect"]
