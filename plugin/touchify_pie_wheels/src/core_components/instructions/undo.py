# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from touchify.src.api_krita import KritaAPI
from touchify_pie_wheels.src.core_components.instruction_base import Instruction


class UndoOnPress(Instruction):
    """
    Undo last activity when key was pressed.

    ### Example usage:
    ```python
    instructions.UndoOnPress()
    ```
    """

    def on_key_press(self) -> None:
        """Trigger the undo action."""
        KritaAPI.trigger_action("edit_undo")
