from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .GridInfo import GridInfo

class GridConfig:
    def __init__(self, **args) -> None:
        self.grids: list["GridInfo"] = []
        JsonExtensions.dictToObject(self, args, [GridInfo])
        self.grids = JsonExtensions.init_list(args, "grids", GridInfo)

    def dump(self):
        return {
            "grids": [{
                "brush_presets": x.brush_presets,
                "name": x.name,
                "is_collapsed": x.is_collapsed,
                "is_active": x.is_active,
                "layout": x.layout
            } for x in self.grids]
        }

