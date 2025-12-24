from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class GridPresetItem:
    def __init__(self, **args):
        self.displayName = ""
        JsonExtensions.dictToObject(self, args, [])

    def name(self):
        return self.displayName
    
    def image(self):
        return None
