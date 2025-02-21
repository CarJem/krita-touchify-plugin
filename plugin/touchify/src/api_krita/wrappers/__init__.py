# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wrappers of classes in krita API.

Adds typing, docstrings and changes the interface to be PEP8 compatible.
"""

from touchify.src.api_krita.wrappers.notifier import NotifierAPI
from touchify.src.api_krita.wrappers.version import Version, UnknownVersion
from touchify.src.api_krita.wrappers.tool_descriptor import ToolDescriptor
from touchify.src.api_krita.wrappers.document import DocumentAPI
from touchify.src.api_krita.wrappers.canvas import CanvasAPI
from touchify.src.api_krita.wrappers.cursor import CursorAPI
from touchify.src.api_krita.wrappers.node import NodeAPI
from touchify.src.api_krita.wrappers.view import ViewAPI
from touchify.src.api_krita.wrappers.window import WindowAPI


__all__ = [
    "UnknownVersion",
    "ToolDescriptor",
    "DocumentAPI",
    "Version",
    "CanvasAPI",
    "CursorAPI",
    "NodeAPI",
    "ViewAPI",
    "NotifierAPI",
    "WindowAPI"]
