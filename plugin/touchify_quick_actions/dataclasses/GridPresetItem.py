from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.config.triggers.Trigger import Trigger

class GridPresetItem:
    def __init__(self, **args):
        self.uuid = ""
        self.trigger_data: Trigger = Trigger()
        JsonExtensions.dictToObject(self, args, [Trigger])

    def itemUUID(self):
        return self.uuid
    
    def image(self):
        return None
