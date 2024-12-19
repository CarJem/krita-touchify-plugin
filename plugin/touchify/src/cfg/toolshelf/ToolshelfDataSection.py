from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.StrEnum import StrEnum

class ToolshelfDataSection:

    class SubpanelMode(StrEnum):
        Data = "data"
        Reference = "reference"

    class SectionType(StrEnum):
        Actions = "actions"
        Docker = "docker"
        Special = "special"
        Subpanel = "subpanel"

    class SpecialItemType(StrEnum):
        Nothing = "none"
        BrushBlendingMode = "brush_blending_options"
        LayerBlendingMode = "layer_blending_options"
        LayerLabelBox = "layer_label_box"
        BrushSizeSlider = "brush_size_slider"
        BrushOpacitySlider = "brush_opacity_slider"
        BrushFlowSlider = "brush_flow_slider"
        BrushRotationSlider = "brush_rotation_slider"
        ForegroundColorBox = "foreground_color_box"
        BackgroundColorBox = "background_color_box"

    class SectionAlignmentX(StrEnum):
        Nothing = "none"
        Left = "left"
        Center = "center"
        Right = "right"
        Expanding = "expanding"
    
    class SectionAlignmentY(StrEnum):
        Nothing = "none"
        Top = "top"
        Center = "center"
        Bottom = "bottom"
        Expanding = "expanding"

    class ActionSectionDisplayMode(StrEnum):
        Normal = "normal"
        Flat = "flat"
        Detailed = "detailed"

    class DockerNestingMode(StrEnum):
        Normal = "normal"
        Docking = "docking"

    class DockerUnloadedVisibility(StrEnum):
        Normal = "normal"
        Hidden = "hidden"

    class DockerLoadingPriority(StrEnum):
        Normal = "normal"
        Passive = "passive"



    def __defaults__(self):
        self.display_name: str = ""

        self.docker_id: str = ""

        self.size_x: int = 0
        self.size_y: int = 0

        self.min_size_x: int = 0
        self.min_size_y: int = 0

        self.max_size_x: int = 0
        self.max_size_y: int = 0

        self.panel_y: int = 0
        self.panel_x: int = 0

        self.ignore_scaling: bool = False
        self.section_type: str = "docker"

        self.docker_nesting_mode: str = "normal"
        self.docker_unloaded_visibility: str = "normal"
        self.docker_loading_priority: str = "normal"

        self.action_section_id: str = "Panel"
        self.action_section_display_mode: str = "normal"
        self.action_section_contents: TypedList[TriggerGroup] = []
        self.action_section_alignment_x: str = "none"
        self.action_section_alignment_y: str = "none"
        self.action_section_btn_width: int = 0
        self.action_section_btn_height: int = 0
        self.action_section_icon_size: int = 0

        self.special_item_type: str = "none"

        self.subpanel_id: str = ""
        self.subpanel_mode: str = "data"

        self.json_version: int = 4

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfDataSection(args)
        from .ToolshelfDataPage import ToolshelfDataPage
        self.subpanel_data: ToolshelfDataPage = ToolshelfDataPage()
        Extensions.dictToObject(self, args, [ToolshelfDataPage])
        self.action_section_contents = Extensions.init_list(args, "action_section_contents", TriggerGroup)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, TriggerGroup)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def __str__(self):
        if self.section_type == ToolshelfDataSection.SectionType.Actions:
            name = self.action_section_id.replace("\n", "\\n")
            suffix = "(Actions)"
        elif self.section_type == ToolshelfDataSection.SectionType.Subpanel:
            name = self.subpanel_data.id.replace("\n", "\\n")
            suffix = "(Subpanel)"
        elif self.section_type == ToolshelfDataSection.SectionType.Special:
            name = self.special_item_type.replace("\n", "\\n")
            suffix = "(Special)"
        elif self.section_type == ToolshelfDataSection.SectionType.Docker:
            name = self.docker_id.replace("\n", "\\n")
            suffix = "(Docker)"
        else:
            name = self.display_name.replace("\n", "\\n")
            suffix = "(Unknown)"

        if self.hasDisplayName():
            name = self.display_name
            
        return f"{name} {suffix} [{self.panel_x}, {self.panel_y}]"
    
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
            "variant_data_group",
            "subpanel_data"
        ]
    
    def propertygrid_hidden(self):
        docker_groups = [
            "docker_id", 
            "docker_nesting_mode", 
            "docker_unloaded_visibility", 
            "docker_loading_priority"
        ]

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

        special_groups = [
            "special_item_type"
        ]

        subgroup_groups = [
            "subpanel_mode"
        ]

        subgroup_data_groups = [
            "subpanel_data"
        ]

        subgroup_refrence_groups = [
            "subpanel_id"
        ]

        result = []
        if self.section_type != ToolshelfDataSection.SectionType.Docker:
            for item in docker_groups:
                result.append(item)
        if self.section_type != ToolshelfDataSection.SectionType.Actions:
            for item in action_groups:
                result.append(item)

        if self.section_type != ToolshelfDataSection.SectionType.Subpanel:
            all_groups = subgroup_groups + subgroup_data_groups + subgroup_refrence_groups
            for item in all_groups: result.append(item)
        else:
            if self.subpanel_mode != self.SubpanelMode.Data:
                for item in subgroup_data_groups:
                    result.append(item)
            if self.subpanel_mode != self.SubpanelMode.Reference:
                for item in subgroup_refrence_groups:
                    result.append(item)
        if self.section_type != ToolshelfDataSection.SectionType.Special:
            for item in special_groups:
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

        labels["special_item_type"] = "Component Type"

        labels["subpanel_mode"] = "Subpanel Mode"
        labels["subpanel_data"] = "Subpanel Options"
        labels["subpanel_id"] = "Subshelf ID"
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
            "action_section_contents",
            "special_item_type",
            "subpanel_mode",
            "subpanel_id"
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
        restrictions["panel_x"] = {"type": "range", "min": 0}
        restrictions["panel_y"] = {"type": "range", "min": 0}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
        restrictions["min_size_x"] = {"type": "range", "min": 0}
        restrictions["min_size_y"] = {"type": "range", "min": 0}
        restrictions["max_size_x"] = {"type": "range", "min": 0}
        restrictions["max_size_y"] = {"type": "range", "min": 0}
        restrictions["section_type"] = {"type": "values", "entries": self.SectionType.values()}

        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["docker_nesting_mode"] = {"type": "values", "entries": self.DockerNestingMode.values()}
        restrictions["docker_unloaded_visibility"] = {"type": "values", "entries": self.DockerUnloadedVisibility.values()}
        restrictions["docker_loading_priority"] = {"type": "values", "entries": self.DockerLoadingPriority.values()}

        restrictions["action_section_display_mode"] = {"type": "values", "entries": self.ActionSectionDisplayMode.values()}
        restrictions["action_section_btn_width"] = {"type": "range", "min": 0}
        restrictions["action_section_btn_height"] = {"type": "range", "min": 0}
        restrictions["action_section_alignment_x"] = {"type": "values", "entries": self.SectionAlignmentX.values()}
        restrictions["action_section_alignment_y"] = {"type": "values", "entries": self.SectionAlignmentY.values()}
        restrictions["action_section_icon_size"] = {"type": "range", "min": 0}

        restrictions["special_item_type"] = {"type": "values", "entries": self.SpecialItemType.values()}

        restrictions["subpanel_data"] = {"type": "expandable"}
        restrictions["subpanel_mode"] = {"type": "values", "entries": self.SubpanelMode.values()}
        restrictions["subpanel_id"] = {"type": "registry_toolshelf_selection"}
        return restrictions