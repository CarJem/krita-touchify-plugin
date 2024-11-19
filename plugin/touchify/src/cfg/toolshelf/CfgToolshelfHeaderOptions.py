from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.StrEnum import StrEnum
from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection

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

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        
        self.stack_actions = Extensions.init_list(args, "stack_actions", CfgTouchifyActionCollection)
    
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