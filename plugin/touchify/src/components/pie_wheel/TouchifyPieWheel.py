
from PyQt5.QtGui import QColor
from typing import TypeVar
from functools import cached_property
from jemlib.api_krita import KritaAPI
from krita import *
from jemlib.alib_kis.dataclass.KisColor import KisColor
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_widgets.buttons.RoundButton import RoundButton


from shortcut_composer.core_components import Controller, Instruction
from shortcut_composer.templates import RawInstructions
from shortcut_composer.data_components.strategies import PieDeadzoneStrategy
from shortcut_composer.templates import PieMenu as ComposerPieMenu
from shortcut_composer.composer_utils import GroupOrderHolder
from shortcut_composer.templates.pie_menu_utils import PieStyleHolder
from shortcut_composer.templates.pie_menu_utils import PieLabelCreator, PieWidget

from touchify.src.components.pie_wheel.api_composer.preset_pie_config import PresetPieConfig

T = TypeVar('T')

from touchify.src.components.pie_wheel.api_composer.touchify_constants import SEPERATOR



from touchify.src.config.various.PieWheelData import PieWheelData
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from jemlib.managers.GlobalEvents import GlobalEvents


class TouchifyPieWheel(ComposerPieMenu):



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
        max_lines_amount=2,
        max_signs_amount=8,
        abbreviate_with_dot=True
    ) -> None:
        RawInstructions.__init__(self, name, instructions)
        self._controller = controller

        self._config = PresetPieConfig(
            name=f"Touchify: {name}",
            values=values,
            controller=controller,
            pie_radius_scale=pie_radius_scale,
            icon_radius_scale=icon_radius_scale,
            save_local=save_local,
            background_color=background_color,
            active_color=active_color,
            pie_opacity=pie_opacity,
            deadzone_strategy=deadzone_strategy,
            max_lines_amount=max_lines_amount,
            max_signs_amount=max_signs_amount,
            abbreviate_with_dot=abbreviate_with_dot)

        self._style_holder = PieStyleHolder(self._config)
        self._label_creator = PieLabelCreator(self._controller)
        self._group_order_holder = GroupOrderHolder(self._controller.TYPE)

        self._is_in_edit_mode = False
        self._force_reload = False

        # Usually, when values stay same, recreating widgets is not
        # needed, but when widget scale changes, they have to be
        # reloaded even when values were not changed.
        def raise_flag():
            self._force_reload = True
        self._register_callback_to_size_change(raise_flag)
        self._config.MAX_SIGNS_AMOUNT.register_callback(raise_flag)
        self._config.MAX_LINES_AMOUNT.register_callback(raise_flag)
        self._config.ABBREVIATE_WITH_DOT.register_callback(raise_flag)
    
    def PieWheel_OnKeyRelease(self):
        self.Close()
        
    def PieWheel_OnMouseRelease(self):
        self.Close()

    def Show(self):
        ComposerPieMenu.on_key_press(self)
        GlobalEvents().SIGNAL_KEY_RELEASED.connect(self.PieWheel_OnKeyRelease)
        GlobalEvents().SIGNAL_MOUSE_RELEASED.connect(self.PieWheel_OnMouseRelease)

    def Close(self):
        ComposerPieMenu.on_every_key_release(self)
        try: GlobalEvents().SIGNAL_KEY_RELEASED.disconnect(self.PieWheel_OnKeyRelease)
        except: pass
        try: GlobalEvents().SIGNAL_MOUSE_RELEASED.disconnect(self.PieWheel_OnMouseRelease)
        except: pass

    @staticmethod
    def generate(data: PieWheelData):
        from shortcut_composer import templates
        from shortcut_composer.api_krita.enums import Action, Tool, Toggle, BlendingMode, TransformMode
        from shortcut_composer.core_components import instructions, controllers
        from shortcut_composer.input_adapter import ComplexActionInterface
        from shortcut_composer.templates.pie_menu_utils import PieWidget
        from touchify.src.components.pie_wheel.api_composer.pie_controller import PieActionController
        from shortcut_composer.data_components import (
            RotationDeadzoneStrategy,
            PieDeadzoneStrategy,
            CurrentLayerStack,
            PickLayerStrategy,
            Slider,
            Range,
            Group)

        converted_values: list[str] = []

        for group in data.actions_items:
            group: TriggerGroup
            for action in group.actions:
                action: Trigger
                #"ACTION_ID::TOUCHIFY_ICON_PATH::TOUCHIFY_CUSTOM_TEXT"  

                jsonData = JsonExtensions.saveClass(action)
                if action.display_custom_text_enabled:
                    entry = f"{jsonData}{SEPERATOR}{action.display_custom_icon}{SEPERATOR}{action.display_custom_text}"
                else:
                    entry = f"{jsonData}{SEPERATOR}{action.display_custom_icon}"
                converted_values.append(entry)


        background_color = KisColor.toQt(data.background_color)
        active_color = KisColor.toQt(data.active_color)

                
        result = TouchifyPieWheel(
            name=data.id,
            controller=PieActionController(),
            background_color=background_color,
            active_color=active_color,
            pie_radius_scale=data.pie_radius_scale,
            icon_radius_scale=data.icon_radius_scale,
            pie_opacity=data.pie_opacity,
            values=converted_values
        )

        return result
    

    #region Native Functions

    @cached_property
    def _pie_widget(self) -> PieWidget:
        """GUI of the radial menu for activating values."""

        pie_widget = PieWidget(
            style=self._style_holder.pie_widget_style,
            allowed_types=self._controller.TYPE)
        pie_widget.draggable = False

        def allow_value_edit():
            pie_widget.only_order_change = self._config.GROUP_MODE.read()
        self._config.GROUP_MODE.register_callback(allow_value_edit)
        allow_value_edit()

        def reset_size():
            pie_widget.hide()
            pie_widget.reset_size()
        self._register_callback_to_size_change(reset_size)

        self._settings_button.setParent(pie_widget)

        return pie_widget

    @cached_property
    def _settings_button(self) -> RoundButton:
        """Create button with which user can enter the edit mode."""
        pie_style = self._style_holder.pie_widget_style

        settings_button = RoundButton(
            radius_callback=lambda: pie_style.widget_radius,
            background_color_callback=lambda: pie_style.background_color,
            active_color_callback=lambda: pie_style.active_color,
            icon=KritaAPI.get_icon("properties"),
            icon_scale=1.1,
            parent=None)
        settings_button.setVisible(False)
        return settings_button
    
    def on_key_press(self) -> None:
        """Handle the event of user pressing the action key."""
        super().on_key_press()

        # Following cached_property are created in this method:
        # self._pie_widget
        # self._settings_button (technically created by pie_widget)
        # self._label_selector

        # Abort handling when the widget is already being displayed
        if self._pie_widget.isVisible():
            return

        # Read values selected for display from config
        new_labels = self._label_creator.labels_from_config(self._config)
        current_labels = self._pie_widget.order_handler.labels

        # Replace labels in pie_widget when values or label size changed
        if new_labels != current_labels or self._force_reload:
            self._force_reload = False
            self._pie_widget.order_handler.replace_labels(new_labels)

        # Fill current_value_holder with value from controller
        self._controller.refresh()
        try:
            current_value = self._controller.get_value()
        except NotImplementedError:
            label = None
        else:
            label = self._label_creator.label_from_value(current_value)
        self._current_value_holder.replace(label)
        self._current_value_holder.enabled = label not in new_labels

        # Start tracker which highlights/selects the values under cursor
        self._label_selector.start_tracking()

    #endregion