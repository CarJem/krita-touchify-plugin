from ..action.CfgTouchifyAction import *
from ..action.CfgTouchifyActionCollection import *
from ...ext.types.TypedList import TypedList
from ...ext.JsonExtensions import JsonExtensions as Extensions
from ...ext.types.StrEnum import StrEnum

class CfgToolshelfSection:

    class SectionType(StrEnum):
        Actions = "actions"
        Docker = "docker"
        Special = "special"

    class SpecialItemType(StrEnum):
        Nothing = "none"
        BrushBlendingMode = "brush_blending_options"
        LayerBlendingMode = "layer_blending_options"
        LayerLabelBox = "layer_label_box"

    id: str = ""

    size_x: int = 0
    size_y: int = 0

    min_size_x: int = 0
    min_size_y: int = 0

    max_size_x: int = 0
    max_size_y: int = 0

    panel_y: int = 0
    panel_x: int = 0

    section_type: str = "docker"

    docker_nesting_mode: str = "normal"
    docker_unloaded_visibility: str = "normal"
    docker_loading_priority: str = "normal"

    action_section_display_mode: str = "normal"
    action_section_name: str = "Panel"
    action_section_contents: TypedList[CfgTouchifyActionCollection] = []
    action_section_alignment_x: str = "none"
    action_section_alignment_y: str = "none"
    action_section_btn_width: int = 0
    action_section_btn_height: int = 0
    action_section_icon_size: int = 0

    special_item_type: str = "none"

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        action_section_contents = Extensions.default_assignment(args, "action_section_contents", [])
        self.action_section_contents = Extensions.list_assignment(action_section_contents, CfgTouchifyActionCollection)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, CfgTouchifyActionCollection)

    def __str__(self):
        if self.section_type == CfgToolshelfSection.SectionType.Actions:
            name = self.action_section_name.replace("\n", "\\n") + " (Actions)"
        elif self.section_type == CfgToolshelfSection.SectionType.Special:
            name = self.action_section_name.replace("\n", "\\n") + " (Special)"
        else:
            name = self.id.replace("\n", "\\n")
            
        name += f" [{self.panel_x}, {self.panel_y}]"
        return name
    
    def propertygrid_hints(self):
        hints = {}
        hints["size_x"] = "leave set to 0 for automatic sizing"
        hints["size_y"] = "leave set to 0 for automatic sizing"
        return hints
    
    def propertygrid_sorted(self):
        global_groups = [
            "section_type",
            "min_size_x",
            "min_size_y",
            "max_size_x",
            "max_size_y",
            "size_x",
            "size_y",
            "panel_x",
            "panel_y"
        ]

        docker_groups = [
            "id", 
            "docker_nesting_mode", 
            "docker_unloaded_visibility", 
            "docker_loading_priority"
        ]

        action_groups = [
            "action_section_name", 
            "action_section_display_mode",
            "action_section_alignment_x", 
            "action_section_alignment_y", 
            "action_section_btn_width", 
            "action_section_btn_height",
            "action_section_icon_size",
            "action_section_contents", 
        ]

        special_groups = [
            "special_item_type"
        ]

        return global_groups + docker_groups + action_groups + special_groups
    
    def propertygrid_hidden(self):
        action_groups = [
            "action_section_name", 
            "action_section_display_mode",
            "action_section_alignment_x", 
            "action_section_alignment_y", 
            "action_section_btn_width", 
            "action_section_btn_height",
            "action_section_icon_size",
            "action_section_contents", 
        ]

        docker_groups = [
            "id", 
            "docker_nesting_mode", 
            "docker_unloaded_visibility", 
            "docker_loading_priority"
        ]

        special_groups = [
            "special_item_type"
        ]

        result = []
        if self.section_type != CfgToolshelfSection.SectionType.Docker:
            for item in docker_groups:
                result.append(item)
        if self.section_type != CfgToolshelfSection.SectionType.Actions:
            for item in action_groups:
                result.append(item)
        if self.section_type != CfgToolshelfSection.SectionType.Special:
            for item in special_groups:
                result.append(item)

        return result

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Docker ID"
        labels["size_x"] = "Base Width"
        labels["size_y"] = "Base Height"
        labels["max_size_x"] = "Max Width"
        labels["max_size_y"] = "Max Height"
        labels["min_size_x"] = "Min Width"
        labels["min_size_y"] = "Min Height"
        labels["panel_y"] = "Panel Row"
        labels["panel_x"] = "Panel Column"
        labels["section_type"] = "Section Type"

        labels["docker_nesting_mode"] = "Nesting Mode"
        labels["docker_unloaded_visibility"] = "Unloaded Visibility"
        labels["docker_loading_priority"] = "Loading Priority"

        labels["action_section_display_mode"] = "Display Mode"
        labels["action_section_name"] = "Section Name"
        labels["action_section_contents"] = "Actions"
        labels["action_section_alignment_x"] = "Horizontal Alignment"
        labels["action_section_alignment_y"] = "Vertical Alignment"
        labels["action_section_btn_width"] = "Button Width"
        labels["action_section_btn_height"] = "Button Height"
        labels["action_section_icon_size"] = "Icon Size"

        labels["special_item_type"] = "Component Type"
        return labels
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["action_section_btn_size"] = {"name": "Button Width / Height", "items": ["action_section_btn_width", "action_section_btn_height"]}
        row["action_section_alignment"] = {"name": "Horizontal / Vertical Alignment", "items": ["action_section_alignment_x","action_section_alignment_y"]}
        row["size"] = {"name": "Base Width / Height", "items": ["size_x","size_y"]}
        row["min_size"] = {"name": "Min Width / Height", "items": ["min_size_x","min_size_y"]}
        row["max_size"] = {"name": "Max Width / Height", "items": ["max_size_x","max_size_y"]}
        row["panel_location"] = {"name": "Panel Position", "items": ["panel_x", "panel_y"]}
        return row

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["panel_x"] = {"type": "range", "min": 0}
        restrictions["panel_y"] = {"type": "range", "min": 0}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
        restrictions["min_size_x"] = {"type": "range", "min": 0}
        restrictions["min_size_y"] = {"type": "range", "min": 0}
        restrictions["max_size_x"] = {"type": "range", "min": 0}
        restrictions["max_size_y"] = {"type": "range", "min": 0}
        restrictions["section_type"] = {"type": "values", "entries": self.SectionType.values()}

        restrictions["docker_nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["docker_unloaded_visibility"] = {"type": "values", "entries": ["normal", "hidden"]}
        restrictions["docker_loading_priority"] = {"type": "values", "entries": ["normal", "passive"]}

        restrictions["action_section_display_mode"] = {"type": "values", "entries": ["normal", "flat"]}
        restrictions["action_section_btn_width"] = {"type": "range", "min": 0}
        restrictions["action_section_btn_height"] = {"type": "range", "min": 0}
        restrictions["action_section_alignment_x"] = {"type": "values", "entries": ["none", "left", "center", "right", "expanding"]}
        restrictions["action_section_alignment_y"] = {"type": "values", "entries": ["none", "top", "center", "bottom", "expanding"]}
        restrictions["action_section_icon_size"] = {"type": "range", "min": 0}

        restrictions["special_item_type"] = {"type": "values", "entries": self.SpecialItemType.values()}
        return restrictions