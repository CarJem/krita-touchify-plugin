from ...ext.JsonExtensions import JsonExtensions as Extensions
from .CfgWidgetPadOptions import CfgWidgetPadOptions

class CfgWidgetPadToolboxOptions:

    position_x: int = 0
    position_y: int = 0

    alignment_y: str = "top"
    alignment_x: str = "left"

    stretch_x: int = 0
    stretch_y: int = 0

    span_x: int = -1
    span_y: int = -1

    horizontal_mode: bool = False

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def propertygrid_sorted(self):
        return [
            "position_x",
            "position_y",
            "alignment_x",
            "alignment_y",
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
        labels["horizontal_mode"] = "Horizontal Mode"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["position_x"] = {"type": "range", "min": 0}
        restrictions["position_y"] = {"type": "range", "min": 0}
        restrictions["stretch_x"] = {"type": "range", "min": 0}
        restrictions["stretch_y"] = {"type": "range", "min": 0}
        restrictions["span_x"] = {"type": "range", "min": -1}
        restrictions["span_y"] = {"type": "range", "min": -1}
        restrictions["alignment_x"] = {"type": "values", "entries": CfgWidgetPadOptions.HorizontalAlignment.values()}
        restrictions["alignment_y"] = {"type": "values", "entries": CfgWidgetPadOptions.VerticalAlignment.values()}
        return restrictions