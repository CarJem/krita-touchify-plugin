from typing import Any
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.src.alib_datatypes.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.alib_datatypes.EnumStr import EnumStr
from touchify.src.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class TriggerList:

    class SectionAlignmentX(EnumStr):
        Nothing = "none"
        Left = "left"
        Center = "center"
        Right = "right"
        Expanding = "expanding"
    
    class SectionAlignmentY(EnumStr):
        Nothing = "none"
        Top = "top"
        Center = "center"
        Bottom = "bottom"
        Expanding = "expanding"

    class ActionSectionDisplayMode(EnumStr):
        Normal = "normal"
        Flat = "flat"
        Detailed = "detailed"



    def __defaults__(self):
        self.display_name: str = ""

        self.size_x: int = 0
        self.size_y: int = 0

        self.min_size_x: int = 0
        self.min_size_y: int = 0

        self.max_size_x: int = 0
        self.max_size_y: int = 0

        self.ignore_scaling: bool = False

        self.action_section_id: str = "Panel"
        self.display_mode: str = "normal"
        self.action_section_contents: TypedList[TriggerGroup] = []
        self.action_section_alignment_x: str = "none"
        self.action_section_alignment_y: str = "none"
        self.action_section_btn_width: int = 0
        self.action_section_btn_height: int = 0
        self.action_section_icon_size: int = 0

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [])
        self.action_section_contents = JsonExtensions.init_list(args, "action_section_contents", TriggerGroup)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, TriggerGroup)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def __str__(self):
        name = self.action_section_id.replace("\n", "\\n")
        suffix = "(Actions)"

        if self.hasDisplayName(): name = self.display_name
            
        return f"{name} {suffix}"
    
    def convertFrom(self, type: type, cls: Any):
        if type == type(ToolshelfDock):
            actionInfo: ToolshelfDock = cls
            self.action_section_alignment_x = actionInfo.action_section_alignment_x
            self.action_section_alignment_y = actionInfo.action_section_alignment_y
            self.action_section_btn_height = actionInfo.action_section_btn_height
            self.action_section_btn_width = actionInfo.action_section_btn_width
            self.action_section_contents = actionInfo.action_section_contents
            self.display_mode = actionInfo.action_section_display_mode
            self.action_section_icon_size = actionInfo.action_section_icon_size
            self.action_section_id = actionInfo.action_section_id
            self.display_name = actionInfo.display_name
            self.min_size_x = actionInfo.min_size_x
            self.min_size_y = actionInfo.min_size_y
            self.max_size_x = actionInfo.max_size_x
            self.max_size_y = actionInfo.max_size_y
            self.size_x = actionInfo.size_x
            self.size_y = actionInfo.size_y
            self.ignore_scaling = actionInfo.ignore_scaling
    
    def propertygrid_hints(self):
        hints = {}
        hints["size"] = "the base size of this section; leave set to 0 for automatic sizing"
        hints["min_size"] = "the minimum size of this section; leave set to 0 for automatic sizing"
        hints["max_size"] = "the maximum size of this section; leave set to 0 for automatic sizing"
        return hints
    
    def propertygrid_view_type(self):
        return "tabs_vertical"
    
    def propertygrid_sorted(self):
        return [
            "general_groups",
            "variant_data_group"
        ]
    
    def propertygrid_hidden(self):
        action_groups = [
            "action_section_id", 
            "action_section_display_mode",
            "action_section_btn_width", 
            "action_section_btn_height",
            "action_section_btn_size",
            "action_section_alignment_x", 
            "action_section_alignment_y", 
            "action_section_alignment",
            "action_section_icon_size",
            "action_section_contents", 
        ]

        result = []

        for item in action_groups:
            result.append(item)

        return result

    def propertygrid_labels(self):
        labels = {}

        labels["general_group"] = "General"
        labels["variant_group"] = "Variant Options"

        labels["display_name"] = "Display Name"

        labels["size"] = "Base Width / Height"
        labels["max_size"] = "Max Width / Height"
        labels["min_size"] = "Min Width / Height"
        labels["panel_location"] = "Panel Position"
        labels["ignore_scaling"] = "Ignore Scaling"
        labels["section_type"] = "Section Type"

        labels["docker_id"] = "Docker ID"
        labels["docker_nesting_mode"] = "Nesting Mode"
        labels["docker_unloaded_visibility"] = "Unloaded Visibility"
        labels["docker_loading_priority"] = "Loading Priority"

        labels["action_section_display_mode"] = "Display Mode"
        labels["action_section_id"] = "Section ID"
        labels["action_section_contents"] = "Actions"
        labels["action_section_btn_size"] = "Button Width / Height"
        labels["action_section_alignment"] = "Horizontal / Vertical Alignment"
        labels["action_section_icon_size"] = "Icon Size"
        return labels
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}

        global_groups = [
            "display_name",
            "min_size",
            "max_size",
            "size",
            "panel_location",
            "ignore_scaling"
        ]

        variant_group = [
            "section_type",
            "docker_id", 
            "docker_nesting_mode", 
            "docker_unloaded_visibility", 
            "docker_loading_priority",
            "action_section_id", 
            "action_section_display_mode",
            "action_section_btn_size",
            "action_section_alignment", 
            "action_section_icon_size",
            "action_section_contents"
        ]

        row["general_group"] = {"items": global_groups, "is_group": True}
        row["variant_group"] = {"items": variant_group, "is_group": True}

        row["action_section_btn_size"] = {"items": ["action_section_btn_width", "action_section_btn_height"]}
        row["action_section_alignment"] = {"items": ["action_section_alignment_x","action_section_alignment_y"]}
        row["size"] = {"items": ["size_x","size_y"]}
        row["min_size"] = {"items": ["min_size_x","min_size_y"]}
        row["max_size"] = {"items": ["max_size_x","max_size_y"]}
        row["panel_location"] = {"items": ["panel_x", "panel_y"]}
        return row

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["panel_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["panel_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["size_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["size_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["min_size_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["min_size_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["max_size_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["max_size_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["section_type"] = PropertyGrid_Restrictions.strValues(self.SectionType.values())

        restrictions["docker_id"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.DockerSelection)
        restrictions["docker_nesting_mode"] = PropertyGrid_Restrictions.strValues(self.DockerNestingMode.values())
        restrictions["docker_unloaded_visibility"] = PropertyGrid_Restrictions.strValues(self.DockerUnloadedVisibility.values())
        restrictions["docker_loading_priority"] = PropertyGrid_Restrictions.strValues(self.DockerLoadingPriority.values())

        restrictions["action_section_display_mode"] = PropertyGrid_Restrictions.strValues(self.ActionSectionDisplayMode.values())
        restrictions["action_section_btn_width"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["action_section_btn_height"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["action_section_alignment_x"] = PropertyGrid_Restrictions.strValues(self.SectionAlignmentX.values())
        restrictions["action_section_alignment_y"] = PropertyGrid_Restrictions.strValues(self.SectionAlignmentY.values())
        restrictions["action_section_icon_size"] = PropertyGrid_Restrictions.range(min=0)
        return restrictions