from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.config.triggers.Trigger import Trigger

class QuickActionsItem:
    def __init__(self, **args):
        self.uuid = ""
        self.trigger_data: Trigger = Trigger()
        JsonExtensions.dictToObject(self, args, [Trigger])

    @staticmethod
    def fromBrush(uuid: str, brush_id: str):
        trigger_data = Trigger()
        trigger_data.variant = Trigger.Variants.Brush
        trigger_data.brush_name = brush_id
        return QuickActionsItem(uuid=uuid,trigger_data=trigger_data)

    def itemUUID(self):
        return self.uuid
    
    def image(self):
        return None
