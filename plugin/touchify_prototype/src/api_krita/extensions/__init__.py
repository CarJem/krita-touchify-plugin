# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Wrappers of classes in krita API.

Adds typing, docstrings and changes the interface to be PEP8 compatible.
"""

from touchify_prototype.src.api_krita.extensions.window_manager import WindowNotifier, WindowManager
from touchify_prototype.src.api_krita.extensions.tool_descriptor import ToolDescriptor

__all__ = [

    "ToolDescriptor",
    "WindowNotifier",
    "WindowManager"
]
