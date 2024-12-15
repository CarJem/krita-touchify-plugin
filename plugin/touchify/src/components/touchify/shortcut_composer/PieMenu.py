from core_components import Controller, Instruction
from data_components import PieDeadzoneStrategy
from PyQt5.QtGui import QColor
import templates
from typing import TypeVar
from functools import cached_property
from api_krita.pyqt import RoundButton
from krita import *
T = TypeVar('T')

class PieMenu(templates.PieMenu):
    def __init__(
        self, *,
        name: str,
        controller: Controller[T],
        values: list[T],
        instructions: list[Instruction] | None = None,
        pie_radius_scale: float = 1.0,
        icon_radius_scale: float = 1.0,
        background_color: QColor | None = None,
        active_color: QColor | None = None,
        pie_opacity: int = 75,
        save_local: bool = False,
        deadzone_strategy=PieDeadzoneStrategy.DO_NOTHING,
        short_vs_long_press_time: float | None = None
    ) -> None:
        super().__init__(
            name=name, 
            controller=controller, 
            values=values, 
            instructions=instructions, 
            pie_radius_scale=pie_radius_scale, 
            icon_radius_scale=icon_radius_scale, 
            background_color=background_color, 
            active_color=active_color, 
            pie_opacity=pie_opacity, 
            save_local=save_local, 
            deadzone_strategy=deadzone_strategy, 
            short_vs_long_press_time=short_vs_long_press_time
        )
    
    @cached_property
    def settings_button(self) -> RoundButton:
        """Create button with which user can enter the edit mode."""
        pie_style = self._style_holder.pie_style

        settings_button = RoundButton(
            radius_callback=lambda: pie_style.setting_button_radius,
            background_color_callback=lambda: pie_style.background_color,
            active_color_callback=lambda: pie_style.active_color,
            icon=Krita.instance().icon("properties"),
            icon_scale=1.1,
            parent=self.pie_widget)
        settings_button.setVisible(False)
        return settings_button