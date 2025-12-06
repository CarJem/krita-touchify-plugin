from touchify.src.datatypes.sequence.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.datatypes.metaclass.EnumStr import EnumStr
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolshelfSettings:
    class StackPreview(EnumStr):
        Default = "default"
        Tabbed = "tabbed"
        TabbedExclusive = "tabbed_exclusive"

    class ResizeStyle(EnumStr):
        Default = "default"
        Minimum = "minimum"

    class Position(EnumStr):
        Top = "top"
        Bottom = "bottom"
        Left = "left"
        Right = "right"

    class StackAlignment(EnumStr):
        Default = "default"
        Left = "left"
        Center = "center"
        Right = "right"

    def __defaults__(self):
        self.button_size: int = 32
        self.header_size: int = 16

        self.show_pin_button: bool = True
        self.show_menu_button: bool = True

        self.show_tabs: bool = True
        self.show_titlebar: bool = True

        self.position: str = "top"
        self.resize_style: str = "default"

        self.stack_preview: str = "default"
        self.stack_alignment: str = "default"
        self.stack_actions: TypedList[TriggerGroup] = []

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args)
        
        self.stack_actions = JsonExtensions.init_list(args, "stack_actions", TriggerGroup)
    
    def forceLoad(self):
        self.stack_actions = TypedList(self.stack_actions, TriggerGroup)

    def propertygrid_sorted(self):
        return [
            "position",
            "resize_style",
            "stack_preview",
            "stack_alignment",
            "button_size",
            "header_size",
            "visibility_options",
            "show_menu_button",
            "show_pin_button",
            "stack_actions",
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["visibility_options"] = {"items": ["show_tabs","show_titlebar","show_menu_button","show_pin_button"], "use_labels": True}
        return row

    def propertygrid_labels(self):
        labels = {}
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
        labels["resize_style"] = "Resize Style"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["stack_preview"] = PropertyGrid_Restrictions.strValues(self.StackPreview.values())
        restrictions["stack_alignment"] = PropertyGrid_Restrictions.strValues(self.StackAlignment.values())
        restrictions["resize_style"] = PropertyGrid_Restrictions.strValues(self.ResizeStyle.values())
        restrictions["position"] = PropertyGrid_Restrictions.strValues(self.Position.values())
        return restrictions