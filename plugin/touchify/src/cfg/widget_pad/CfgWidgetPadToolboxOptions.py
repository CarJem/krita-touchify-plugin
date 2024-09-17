from ...ext.types.TypedList import TypedList
from ...ext.JsonExtensions import JsonExtensions as Extensions
from .CfgWidgetPadOptions import CfgWidgetPadOptions
from ...ext.types.StrEnum import StrEnum
from PyQt5.QtCore import Qt

class CfgWidgetPadToolboxOptions:

    position_x: int = 0
    position_y: int = 0

    alignment_y: str = "top"
    alignment_x: str = "left"

    stretch_x: int = 0
    stretch_y: int = 0

    horizontal_mode: bool = False

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def propertygrid_sorted(self):
        return [
            "position_x",
            "position_y",
            "alignment_x",
            "alignment_y",
            "stretch_x",
            "stretch_y"

        ]

    def propertygrid_labels(self):
        labels = {}
        labels["position_x"] = "Position X"
        labels["position_y"] = "Position Y"
        labels["alignment_x"] = "Horizontal Alignment"
        labels["alignment_y"] = "Vertical Alignment"
        labels["stretch_x"] = "Horizontal Stretch"
        labels["stretch_y"] = "Vertical Stretch"
        labels["horizontal_mode"] = "Horizontal Mode"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["position_x"] = {"type": "range", "min": 0}
        restrictions["position_y"] = {"type": "range", "min": 0}
        restrictions["stretch_x"] = {"type": "range", "min": 0}
        restrictions["stretch_y"] = {"type": "range", "min": 0}
        restrictions["alignment_x"] = {"type": "values", "entries": CfgWidgetPadOptions.HorizontalAlignment.values()}
        restrictions["alignment_y"] = {"type": "values", "entries": CfgWidgetPadOptions.VerticalAlignment.values()}
        return restrictions