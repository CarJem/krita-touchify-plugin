# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wrappers of classes in krita API.

Adds typing, docstrings and changes the interface to be PEP8 compatible.
"""

from touchify_prototype.src.api_krita.wrappers.notifier import NotifierAPI
from touchify_prototype.src.api_krita.wrappers.version import Version, UnknownVersion
from touchify_prototype.src.api_krita.wrappers.document import DocumentAPI
from touchify_prototype.src.api_krita.wrappers.canvas import CanvasAPI
from touchify_prototype.src.api_krita.wrappers.cursor import CursorAPI
from touchify_prototype.src.api_krita.wrappers.node import NodeAPI
from touchify_prototype.src.api_krita.wrappers.view import ViewAPI
from touchify_prototype.src.api_krita.wrappers.window import WindowAPI
from touchify_prototype.src.api_krita.wrappers.docker_factory import DockWidgetFactoryAPI


__all__ = [
    "DocumentAPI",
    "DockWidgetFactoryAPI",
    "CanvasAPI",
    "CursorAPI",
    "NodeAPI",
    "ViewAPI",
    "WindowAPI",
    "NotifierAPI",
    "UnknownVersion",
    "Version",
]
