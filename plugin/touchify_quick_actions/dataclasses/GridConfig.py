from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .GridInfo import GridInfo

class GridConfig:
    def __init__(self, **args) -> None:
        self.grids: list["GridInfo"] = []
        JsonExtensions.dictToObject(self, args, [GridInfo])
        self.grids = JsonExtensions.init_list(args, "grids", GridInfo)

    def restore(self):
        result = []
        for x in self.grids:
            item = GridInfo()
            item.brush_presets = x.brush_presets
            item.is_active = x.is_active
            item.is_collapsed = x.is_collapsed
            item.layout = x.layout
            item.name = x.name
            result.append(item)
        return result

