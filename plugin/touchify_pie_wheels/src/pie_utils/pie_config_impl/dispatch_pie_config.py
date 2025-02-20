# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Type, TypeVar
from touchify_pie_wheels.src.core_components import Controller
from touchify_pie_wheels.src.pie_utils.pie_config import PieConfig
from touchify_pie_wheels.src.pie_utils.pie_config_impl.preset_pie_config import PresetPieConfig
from touchify_pie_wheels.src.pie_utils.pie_config_impl.non_preset_pie_config import NonPresetPieConfig

T = TypeVar('T')


def dispatch_pie_config(controller: Controller[T]) -> Type[PieConfig[T]]:
    """Return type of PieConfig specialization based on controller type."""
    if issubclass(controller.TYPE, str):
        return PresetPieConfig   # type: ignore
    return NonPresetPieConfig
