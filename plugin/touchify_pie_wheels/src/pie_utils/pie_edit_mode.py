# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify_pie_wheels.src.templates.pie_menu import PieMenu


class PieEditMode:
    """
    Handles the edit mode of the PieMenu action.

    Changing its state to between False and True performs actions on
    PieMenu widgets and components.
    """

    def __init__(self, obj: 'PieMenu') -> None:
        self._edit_mode = False
        self._obj = obj

    def get(self) -> bool:
        """Return whether the Pie is in edit mode"""
        return self._edit_mode

    def set(self, mode_to_set: bool) -> None:
        """Update the mode and change Pie's content accordingly."""
        if not self._edit_mode ^ mode_to_set:
            return

        if mode_to_set:
            self.set_edit_mode_true()
        else:
            self.set_edit_mode_false()
        self._edit_mode = mode_to_set

    def set_edit_mode_true(self) -> None:
        """Set the edit mode on."""

    def _move_settings_next_to_pie(self) -> None:
        """Move settings window so that it lies on right side of pie."""

    def set_edit_mode_false(self) -> None:
        """Set the edit mode off."""

    def swap_mode(self) -> None:
        """Change the edit mode to the other one."""
        self.set(not self._edit_mode)

    def __bool__(self) -> bool:
        return self.get()
