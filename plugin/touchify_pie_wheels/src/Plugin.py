from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.datatypes.dataclass.KisColor import KisColor
from touchify.__env__ import *

from touchify.src.managers.shared.settings import *
from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
from touchify.src.managers.shared.resources import *

from krita import *

from touchify_pie_wheels.src.PieActionController import PieActionController
from touchify_pie_wheels.src.PieMenu import PieMenu
from touchify.src.extensions.krita_extensions import *

class TouchifyPieWheelsPlugin(Extension):

    def __init__(self, parent) -> None:
         super().__init__(parent)
         self.setObjectName("touchify-pie-wheels-api")

    def setup(self):
        pass

    def createActions(self, window: Window):
        pass

    def generate(self, data: PieWheelData):
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


        background_color = KisColor.toQt(data.background_color)
        active_color = KisColor.toQt(data.active_color)

                
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