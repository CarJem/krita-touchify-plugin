from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from ...ext.StrEnum import StrEnum
from ..action.CfgTouchifyActionCollection import CfgTouchifyActionCollection

class CfgToolshelfHeaderOptions:
    class StackPreview(StrEnum):
        Default = "default"
        Tabbed = "tabbed"
        TabbedExclusive = "tabbed_exclusive"

    class Position(StrEnum):
        Top = "top"
        Bottom = "bottom"
        Left = "left"
        Right = "right"

    class StackAlignment(StrEnum):
        Default = "default"
        Left = "left"
        Center = "center"
        Right = "right"


    button_size: int = 32
    header_size: int = 16

    default_to_resize_mode: bool = False


    position: str = "top"
    stack_preview: str = "default"
    stack_alignment: str = "default"
    stack_actions: TypedList[CfgTouchifyActionCollection] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

        stack_actions = Extensions.default_assignment(args, "stack_actions", [])
        self.stack_actions = Extensions.list_assignment(stack_actions, CfgTouchifyActionCollection)
    
    def forceLoad(self):
        self.stack_actions = TypedList(self.stack_actions, CfgTouchifyActionCollection)

    def propertygrid_sorted(self):
        return [
            "button_size",
            "header_size",
            "default_to_resize_mode",
            "position",
            "stack_preview",
            "stack_alignment",
            "stack_actions"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["button_size"] = "Button Size"
        labels["header_size"] = "Button Size"
        labels["default_to_resize_mode"] = "Default to Resize Mode"
        labels["position"] = "Header Position"
        labels["stack_preview"] = "Stack Preview"
        labels["stack_alignment"] = "Stack Alignment"
        labels["stack_actions"] = "Stack Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["stack_preview"] = {"type": "values", "entries": self.StackPreview.values()}
        restrictions["stack_alignment"] = {"type": "values", "entries": self.StackAlignment.values()}
        restrictions["position"] = {"type": "values", "entries": self.Position.values()}
        return restrictions