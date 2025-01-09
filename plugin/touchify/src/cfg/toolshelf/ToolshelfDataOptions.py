from touchify.src.components.python.datatypes.TypedList import TypedList
from touchify.src.components.python.json_extensions import JsonExtensions as Extensions
from touchify.src.components.python.datatypes.StrEnum import StrEnum
from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolshelfDataOptions:
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

    def __defaults__(self):
        self.button_size: int = 32
        self.header_size: int = 16

        self.default_to_resize_mode: bool = False
        self.default_to_pinned: bool = False

        self.show_pin_button: bool = True
        self.show_menu_button: bool = True

        self.show_tabs: bool = True
        self.show_titlebar: bool = True


        self.position: str = "top"
        self.stack_preview: str = "default"
        self.stack_alignment: str = "default"
        self.stack_actions: TypedList[TriggerGroup] = []

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)
        
        self.stack_actions = Extensions.init_list(args, "stack_actions", TriggerGroup)
    
    def forceLoad(self):
        self.stack_actions = TypedList(self.stack_actions, TriggerGroup)

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
        row["visibility_options"] = {"items": ["show_tabs","show_titlebar","show_menu_button","show_pin_button"], "use_labels": True}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["default_options"] = "Defaults"
        labels["default_to_resize_mode"] = "Resizable"
        labels["default_to_pinned"] = "Pinned"
        labels["visibility_options"] = "Show"
        labels["show_tabs"] = "Tabs"
        labels["show_titlebar"] = "Titlebar"
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
        restrictions["stack_preview"] = PropertyGrid_Restrictions.strValues(self.StackPreview.values())
        restrictions["stack_alignment"] = PropertyGrid_Restrictions.strValues(self.StackAlignment.values())
        restrictions["position"] = PropertyGrid_Restrictions.strValues(self.Position.values())
        return restrictions