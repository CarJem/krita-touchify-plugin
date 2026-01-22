from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.config.quick_actions.QuickActionsPageConfig import QuickActionsPageConfig

from .QuickActionsGrid import QuickActionsGrid

class QuickActionsPage:

    def __init__(self, **args) -> None:
        self.name = ""
        self.icon = ""
        self.grids: list["QuickActionsGrid"] = []
        self.settings: QuickActionsPageConfig = QuickActionsPageConfig()

        JsonExtensions.dictToObject(self, args, [QuickActionsGrid, QuickActionsPageConfig])
        self.grids = JsonExtensions.init_list(args, "grids", QuickActionsGrid)

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

