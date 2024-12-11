from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat
from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.StrEnum import StrEnum

class CfgToolshelfSection:

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
        self.action_section_contents: TypedList[CfgTouchifyActionCollection] = []
        self.action_section_alignment_x: str = "none"
        self.action_section_alignment_y: str = "none"
        self.action_section_btn_width: int = 0
        self.action_section_btn_height: int = 0
        self.action_section_icon_size: int = 0

        self.special_item_type: str = "none"

        self.json_version: int = 4

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = CfgBackwardsCompat.CfgToolshelfSection(args)
        from .CfgToolshelfPanel import CfgToolshelfPanel
        self.subpanel_data: CfgToolshelfPanel = CfgToolshelfPanel()
        Extensions.dictToObject(self, args, [CfgToolshelfPanel])
        self.action_section_contents = Extensions.init_list(args, "action_section_contents", CfgTouchifyActionCollection)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, CfgTouchifyActionCollection)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def __str__(self):
        if self.section_type == CfgToolshelfSection.SectionType.Actions:
            name = self.action_section_id.replace("\n", "\\n")
            suffix = "(Actions)"
        elif self.section_type == CfgToolshelfSection.SectionType.Subpanel:
            name = self.subpanel_data.id.replace("\n", "\\n")
            suffix = "(Subpanel)"
        elif self.section_type == CfgToolshelfSection.SectionType.Special:
            name = self.special_item_type.replace("\n", "\\n")
            suffix = "(Special)"
        elif self.section_type == CfgToolshelfSection.SectionType.Docker:
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
    
    def propertygrid_sorted(self):
        global_groups = [
            "display_name",
            "min_size",
            "min_size_x",
            "min_size_y",
            "max_size",
            "max_size_x",
            "max_size_y",
            "size",
            "size_x",
            "size_y",
            "panel_location",
            "panel_x",
            "panel_y",
            "ignore_scaling",
            "section_type"
        ]

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
            "action_section_alignment_x", 
            "action_section_alignment_y", 
            "action_section_icon_size",
            "action_section_contents", 
        ]

        special_groups = [
            "special_item_type"
        ]

        subgroup_groups = [
            "subpanel_data",
        ]

        return global_groups + docker_groups + action_groups + special_groups + subgroup_groups
    
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
            "subpanel_data",
        ]

        result = []
        if self.section_type != CfgToolshelfSection.SectionType.Docker:
            for item in docker_groups:
                result.append(item)
        if self.section_type != CfgToolshelfSection.SectionType.Actions:
            for item in action_groups:
                result.append(item)
        if self.section_type != CfgToolshelfSection.SectionType.Subpanel:
            for item in subgroup_groups:
                result.append(item)
        if self.section_type != CfgToolshelfSection.SectionType.Special:
            for item in special_groups:
                result.append(item)

        return result

    def propertygrid_labels(self):
        labels = {}

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

        labels["subpanel_data"] = "Panel Data"
        return labels
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
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
        return restrictions