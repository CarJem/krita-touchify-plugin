from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from jemlib.api_touchify.config.quick_actions.QuickActionsPageConfig import QuickActionsPageConfig

from .QuickActionsGrid import QuickActionsGrid

class QuickActionsPage:

    def __init__(self, **args) -> None:
        self.name = ""
        self.icon = ""
        self.grids: list["QuickActionsGrid"] = []
        self.settings: QuickActionsPageConfig = QuickActionsPageConfig()

        JsonExtensions.dictToObject(self, args, [QuickActionsGrid, QuickActionsPageConfig])
        self.grids = JsonExtensions.init_list(args, "grids", QuickActionsGrid)
    
    def __str__(self):
        return self.name
    
    def propertygrid_labels(self):
        return {
            "name": "Page Name",
            "icon": "Page Icon",
            "grids": "Grids",
            "settings": "Page Settings",
        }
    
    def propertygrid_sorted(self):
        return [
            "name",
            "icon",
            "settings",
            "grids"
        ]

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["settings"] = DataConstraints.expandable()
        return restrictions

    @staticmethod
    def createEmpty(name: str):
        result = QuickActionsPage()
        result.name = name
        return result

    def restore(self):
        result = []
        for x in self.grids:
            item = QuickActionsGrid()
            item.brush_presets = x.brush_presets
            item.is_active = x.is_active
            item.is_collapsed = x.is_collapsed
            item.layout = x.layout
            item.name = x.name
            result.append(item)
        return result

