from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_datatypes.EnumStr import EnumStr
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from jemlib.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolshelfAreaSettings:
    class StackPreview(EnumStr):
        Default = "default"
        Tabbed = "tabbed"
        TabbedExclusive = "tabbed_exclusive"

    class ResizeStyle(EnumStr):
        Default = "default"
        Minimum = "minimum"
        AdjustSize = "adjust_size"
        SizeHint = "size_hint"
        SizeHintMinimum = "minimum_size_hint"

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

        self.enable_pinning: bool = False

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
            "enable_pinning",
            "stack_preview",
            "stack_alignment",
            "button_size",
            "header_size",
            "stack_actions",
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["button_size"] = "Button Size"
        labels["header_size"] = "Header Size"
        labels["position"] = "Header Position"
        labels["stack_preview"] = "Stack Preview"
        labels["enable_pinning"] = "Enable Pinning"
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