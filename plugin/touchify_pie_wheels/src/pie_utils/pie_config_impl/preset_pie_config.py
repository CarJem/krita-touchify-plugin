# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
from PyQt5.QtGui import QColor

from touchify_pie_wheels.src.pie_utils.pie_deadzone_strategy import PieDeadzoneStrategy
from touchify_pie_wheels.src.pie_utils.pie_config import PieConfig


class PresetPieConfig(PieConfig[str]):
    """
    FieldGroup representing config of PieMenu of presets.

    Values are calculated according to presets belonging to handled tag
    and the custom order saved by the user in kritarc.
    """

    def __init__(
        self,
        name: str,
        values: list[str],
        pie_radius_scale: float,
        icon_radius_scale: float,
        save_local: bool,
        background_color: QColor | None,
        active_color: QColor | None,
        pie_opacity: int,
        deadzone_strategy: PieDeadzoneStrategy
    ) -> None:
        super().__init__(
            name=name,
            values=values,
            pie_radius_scale=pie_radius_scale,
            icon_radius_scale=icon_radius_scale,
            save_local=save_local,
            background_color=background_color,
            active_color=active_color,
            pie_opacity=pie_opacity,
            deadzone_strategy=deadzone_strategy)


        self.ORDER = self._create_editable_dual_field(
            field_name="Values",
            default=[],
            parser_type=str)

    @property
    def allow_value_edit(self) -> bool:
        """Return whether user can add and remove items from the pie."""
        return True

    def values(self) -> list[str]:
        """Return all presets based on mode and stored order."""
        return self.ORDER.read()

    def set_values(self, values: list[str]) -> None:
        self.ORDER.write(values)

    def refresh_order(self) -> None:
        """Refresh the values in case the active document changed."""
        self.ORDER.write(self.values())

    def set_current_as_default(self) -> None:
        """Set current pie values as a new default list of values."""
        self.ORDER.default = self.ORDER.read()

    def reset_the_default(self) -> None:
        """Set empty pie as a new default list of values."""
        self.ORDER.default = []

    def reset_to_default(self) -> None:
        """Replace current list of values in pie with the default list."""
        self.ORDER.reset_default()
        self.refresh_order()

    def is_order_default(self) -> bool:
        """Return whether order is the same as default one."""
        return (self.ORDER.read() == self.ORDER.default)

    def register_to_order_related(self, callback: Callable[[], None]) -> None:
        """Register callback to all fields related to value order."""
        self.ORDER.register_callback(callback)
