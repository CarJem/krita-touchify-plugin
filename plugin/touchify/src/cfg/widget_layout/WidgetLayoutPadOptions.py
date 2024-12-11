from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.StrEnum import StrEnum
from PyQt5.QtCore import Qt

class WidgetLayoutPadOptions:

    class VerticalAlignment(StrEnum):
        Top = "top"
        Center = "center"
        Bottom = "bottom"

        def toAlignmentFlag(en: str):
            if en == WidgetLayoutPadOptions.VerticalAlignment.Top:
                return Qt.AlignmentFlag.AlignTop
            elif en == WidgetLayoutPadOptions.VerticalAlignment.Center:
                return Qt.AlignmentFlag.AlignVCenter
            elif en == WidgetLayoutPadOptions.VerticalAlignment.Bottom:
                return Qt.AlignmentFlag.AlignBottom
            else:
                return Qt.AlignmentFlag.AlignTop
    
    class HorizontalAlignment(StrEnum):
        Left = "left"
        Center = "center"
        Right = "right"

        def toAlignmentFlag(en: str):
            if en == WidgetLayoutPadOptions.HorizontalAlignment.Left:
                return Qt.AlignmentFlag.AlignLeft
            elif en == WidgetLayoutPadOptions.HorizontalAlignment.Center:
                return Qt.AlignmentFlag.AlignHCenter
            elif en == WidgetLayoutPadOptions.HorizontalAlignment.Right:
                return Qt.AlignmentFlag.AlignRight
            else:
                return Qt.AlignmentFlag.AlignLeft

    def __defaults__(self):
        self.position_x: int = 0
        self.position_y: int = 0

        self.stretch_x: int = 0
        self.stretch_y: int = 0

        self.span_x: int = -1
        self.span_y: int = -1

        self.alignment_y: str = "top"
        self.alignment_x: str = "left"

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)

    def propertygrid_sorted(self):
        return [
            "position_x",
            "position_y",
            "alignment_x",
            "alignment_y"
            "stretch_x",
            "stretch_y",
            "span_x",
            "span_y"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["position_x"] = "Position X"
        labels["position_y"] = "Position Y"
        labels["alignment_x"] = "Horizontal Alignment"
        labels["alignment_y"] = "Vertical Alignment"
        labels["stretch_x"] = "Horizontal Stretch"
        labels["stretch_y"] = "Vertical Stretch"
        labels["span_x"] = "Horizontal Span"
        labels["span_y"] = "Vertical Span"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["position_x"] = {"type": "range", "min": 0}
        restrictions["position_y"] = {"type": "range", "min": 0}
        restrictions["stretch_x"] = {"type": "range", "min": 0}
        restrictions["stretch_y"] = {"type": "range", "min": 0}
        restrictions["span_x"] = {"type": "range", "min": -1}
        restrictions["span_y"] = {"type": "range", "min": -1}
        restrictions["alignment_x"] = {"type": "values", "entries": self.HorizontalAlignment.values()}
        restrictions["alignment_y"] = {"type": "values", "entries": self.VerticalAlignment.values()}
        return restrictions