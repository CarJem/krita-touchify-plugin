"""Dialogs package for the Preset Groups docker.

Contains dialog windows for various user interactions like settings
and context menus.
"""

from .CommonConfigDialog import CommonConfigDialog
from .GridNameContextDialog import GridNameContextDialog

__all__ = [
    "CommonConfigDialog",
    "GridNameContextDialog",
]
