from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from ...ext.StrEnum import StrEnum
from PyQt5.QtCore import Qt

class CfgWidgetPadOptions:

    class VerticalAlignment(StrEnum):
        Top = "top"
        Center = "center"
        Bottom = "bottom"

        def toAlignmentFlag(en: str):
            if en == CfgWidgetPadOptions.VerticalAlignment.Top:
                return Qt.AlignmentFlag.AlignTop
            elif en == CfgWidgetPadOptions.VerticalAlignment.Center:
                return Qt.AlignmentFlag.AlignVCenter
            elif en == CfgWidgetPadOptions.VerticalAlignment.Bottom:
                return Qt.AlignmentFlag.AlignBottom
            else:
                return Qt.AlignmentFlag.AlignTop
    
    class HorizontalAlignment(StrEnum):
        Left = "left"
        Center = "center"
        Right = "right"

        def toAlignmentFlag(en: str):
            if en == CfgWidgetPadOptions.HorizontalAlignment.Left:
                return Qt.AlignmentFlag.AlignLeft
            elif en == CfgWidgetPadOptions.HorizontalAlignment.Center:
                return Qt.AlignmentFlag.AlignHCenter
            elif en == CfgWidgetPadOptions.HorizontalAlignment.Right:
                return Qt.AlignmentFlag.AlignRight
            else:
                return Qt.AlignmentFlag.AlignLeft

    position_x: int = 0
    position_y: int = 0

    stretch_x: int = 0
    stretch_y: int = 0

    alignment_y: str = "top"
    alignment_x: str = "left"

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def propertygrid_sorted(self):
        return [
            "position_x",
            "position_y",
            "alignment_x",
            "alignment_y"
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
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["position_x"] = {"type": "range", "min": 0}
        restrictions["position_y"] = {"type": "range", "min": 0}
        restrictions["stretch_x"] = {"type": "range", "min": 0}
        restrictions["stretch_y"] = {"type": "range", "min": 0}
        restrictions["alignment_x"] = {"type": "values", "entries": self.HorizontalAlignment.values()}
        restrictions["alignment_y"] = {"type": "values", "entries": self.VerticalAlignment.values()}
        return restrictions