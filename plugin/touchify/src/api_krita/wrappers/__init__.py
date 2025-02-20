# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wrappers of classes in krita API.

Adds typing, docstrings and changes the interface to be PEP8 compatible.
"""

from touchify.src.api_krita.wrappers.version import Version, UnknownVersion
from touchify.src.api_krita.wrappers.tool_descriptor import ToolDescriptor
from touchify.src.api_krita.wrappers.document import Document
from touchify.src.api_krita.wrappers.canvas import Canvas
from touchify.src.api_krita.wrappers.cursor import Cursor
from touchify.src.api_krita.wrappers.node import Node
from touchify.src.api_krita.wrappers.view import View

__all__ = [
    "UnknownVersion",
    "ToolDescriptor",
    "Document",
    "Version",
    "Canvas",
    "Cursor",
    "Node",
    "View"]
