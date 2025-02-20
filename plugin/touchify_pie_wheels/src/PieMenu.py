from touchify.src.api_krita import KritaAPI
from touchify_pie_wheels.src.core_components import Controller, Instruction
from touchify_pie_wheels.src.pie_utils.pie_deadzone_strategy import PieDeadzoneStrategy
from PyQt5.QtGui import QColor
from typing import TypeVar
from functools import cached_property
from touchify.src.components.common.buttons.RoundButton import RoundButton
from krita import *
from touchify_pie_wheels.src.pie_utils.pie_menu import PieMenu as BaseClass
from touchify.src.managers.shared.events import GlobalEvents
T = TypeVar('T')

class PieMenu(BaseClass):
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


    
    def PieWheel_OnKeyRelease(self):
        self.Close()
        
    def PieWheel_OnMouseRelease(self):
        self.Close()

    def Show(self):
        self.on_key_press()
        GlobalEvents.instance().SIGNAL_KEY_RELEASED.connect(self.PieWheel_OnKeyRelease)

    def Close(self):
        self.on_every_key_release()
        GlobalEvents.instance().SIGNAL_KEY_RELEASED.disconnect(self.PieWheel_OnKeyRelease)


    @cached_property
    def settings_button(self) -> RoundButton:
        """Create button with which user can enter the edit mode."""
        pie_style = self._style_holder.pie_style

        settings_button = RoundButton(
            radius_callback=lambda: pie_style.setting_button_radius,
            background_color_callback=lambda: pie_style.background_color,
            active_color_callback=lambda: pie_style.active_color,
            icon=KritaAPI.get_icon("properties"),
            icon_scale=1.1,
            parent=self.pie_widget)
        settings_button.setVisible(False)
        return settings_button