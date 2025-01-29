from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
from touchify.src.cfg.triggers.Trigger import Trigger
from touchify.src.components.krita.settings import KS_Color
from touchify.__env__ import *

from touchify.src.managers.shared.settings import *
from touchify.src.cfg.pie_wheel.PieWheelData import PieWheelData
from touchify.src.managers.shared.resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.PluginWindow import TouchifyWindow

try:
    from input_adapter import ActionManager
    import templates
    from touchify.src.components.touchify.shortcut_composer.PieActionController import PieActionController
    from touchify.src.components.touchify.shortcut_composer.PieMenu import PieMenu
    from touchify.src.components.krita.extensions import *
    SHORTCUT_COMPOSER_LOADED = True
except:
    SHORTCUT_COMPOSER_LOADED = False

FEATURE_ENABLED = True
    
class ShortcutComposerUtils:

    @staticmethod
    def PieWheel_TestObject():
            return PieMenu(
                name="[Touchify] Pie Menu #1",
                controller=PieActionController(),
                pie_radius_scale=1.5,
                icon_radius_scale=1.5,
                values=[
                    #"ACTION_ID::TOUCHIFY_ICON_PATH::TOUCHIFY_CUSTOM_TEXT"
                    "selection_tool_mode_add::selection_add",
                    "selection_tool_mode_replace::selection_replace",
                    "selection_tool_mode_subtract::selection_subtract",
                    "selection_tool_mode_intersect::selection_intersect",
                    "file_new::folder-documents",
                    "file_new::material:file",
                    "file_new::material:facebook",
                    "file_new::material:facebook-messenger",
                    "file_new::material:google",
                    "file_new::material:google-play",
                    "file_new::material:google-drive",
                    "file_new::material:apple",
                    "file_new::material:apple-ios",
                    "file_new::material:microsoft",
                    "file_new::material:microsoft-xbox",
                    "file_new::material:github",
                    "file_new::material:minecraft",
                    "file_new::material:sony-playstation",
                    "file_new::material:microsoft-windows",
                    "file_new::material:microsoft-visual-studio-code",
                    "file_new::material:nintendo-switch",
                    "file_new::material:nintendo-game-boy",
                    "file_new::material:nintendo-wii",
                    "file_new::material:microsoft-windows-classic",
                ]
            )

    @staticmethod
    def PieWheel_Generate(data: PieWheelData):
        if not SHORTCUT_COMPOSER_LOADED: return None
        if not FEATURE_ENABLED: return None
    
        converted_values = []

        for group in data.actions_items:
            group: TriggerGroup
            for action in group.actions:
                action: Trigger
                #"ACTION_ID::TOUCHIFY_ICON_PATH::TOUCHIFY_CUSTOM_TEXT"  
                if action.display_custom_text_enabled:
                    entry = f"{action.action_id}::{action.display_custom_icon}::{action.display_custom_text}"
                else:
                    entry = f"{action.action_id}::{action.display_custom_icon}"
                converted_values.append(entry)


        background_color = KS_Color.toQt(data.background_color)
        active_color = KS_Color.toQt(data.active_color)

                
        result = PieMenu(
            name=data.registry_name,
            controller=PieActionController(),
            pie_radius_scale=data.pie_radius_scale,
            icon_radius_scale=data.icon_radius_scale,
            background_color=background_color,
            active_color=active_color,
            pie_opacity=data.pie_opacity,
            values=converted_values
        )

        return result