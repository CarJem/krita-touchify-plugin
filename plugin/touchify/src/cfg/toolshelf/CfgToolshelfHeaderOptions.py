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
    default_to_pinned: bool = False

    show_pin_button: bool = True
    show_menu_button: bool = True


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
            "default_to_resize_mode",
            "default_to_pinned",
            "show_menu_button",
            "show_pin_button",
            "button_size",
            "header_size",
            "position",
            "stack_preview",
            "stack_alignment",
            "stack_actions",
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["default_options"] = {"items": ["default_to_resize_mode","default_to_pinned"], "use_labels": True}
        row["visibility_options"] = {"items": ["show_menu_button","show_pin_button"], "use_labels": True}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["default_options"] = "Defaults"
        labels["default_to_resize_mode"] = "Resizable"
        labels["default_to_pinned"] = "Pinned"
        labels["visibility_options"] = "Show"
        labels["show_menu_button"] = "Options Button"
        labels["show_pin_button"] = "Pin Button"
        labels["button_size"] = "Button Size"
        labels["header_size"] = "Header Size"
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