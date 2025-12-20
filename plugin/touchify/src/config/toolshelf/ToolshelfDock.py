from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolshelfDock:

    class SectionType(EnumStr):
        Actions = "actions"
        Docker = "docker"
        Special = "special"
        Placeholder = "placeholder"

    class SliderOrientation(EnumStr):
        Horizontal="horizontal"
        Vertical="vertical"

    class SpecialItemType(EnumStr):
        Nothing = "none"
        BrushBlendingMode = "brush_blending_options"
        LayerBlendingMode = "layer_blending_options"
        LayerLabelBox = "layer_label_box"
        BrushSizeSlider = "brush_size_slider"
        BrushOpacitySlider = "brush_opacity_slider"
        BrushFlowSlider = "brush_flow_slider"
        BrushAngleSelector = "brush_rotation_slider"
        ForegroundColorBox = "foreground_color_box"
        BackgroundColorBox = "background_color_box"
        ForegroundBackgroundColorPicker = "foreground_background_color_picker"
        BrushPicker = "brush_preset_picker"
        GradientPicker = "pattern_chooser_popup"
        PatternPicker = "gradient_chooser_popup"
        NestedShelf = "nested_shelf"

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

    class DockerNestingMode(EnumStr):
        Normal = "normal"
        Docking = "docking"

    class DockerUnloadedVisibility(EnumStr):
        Normal = "normal"
        Hidden = "hidden"

    class DockerLoadingPriority(EnumStr):
        Normal = "normal"
        Passive = "passive"


    def __defaults__(self):
        self.display_name: str = ""

        self.docker_id: str = ""

        self.min_size_x: int = 0
        self.min_size_y: int = 0

        self.max_size_x: int = 0
        self.max_size_y: int = 0

        self.section_type: str = "docker"
        self.requires_specific_tool: str = ""
        self.invert_required_tools: bool = False

        self.docker_nesting_mode: str = "normal"
        self.docker_unloaded_visibility: str = "normal"
        self.docker_loading_priority: str = "normal"
        self.docker_size_hint_x: int = 0
        self.docker_size_hint_y: int = 0

        self.action_section_id: str = "Panel"
        self.action_section_display_mode: str = "normal"
        self.action_section_contents: TypedList[TriggerGroup] = []
        self.action_section_alignment_x: str = "none"
        self.action_section_alignment_y: str = "none"
        self.action_section_btn_width: int = 0
        self.action_section_btn_height: int = 0
        self.action_section_icon_size: int = 0

        self.special_item_type: str = "none"
        self.special_slider_orientation: str = "horizontal"
        self.special_nested_show_titlebar: bool = True

        from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
        self.special_nested_data: ToolshelfArea = ToolshelfArea()

        self.json_version: int = 5

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfDock(args)
        from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
        JsonExtensions.dictToObject(self, args, [ToolshelfArea])
        self.action_section_contents = JsonExtensions.init_list(args, "action_section_contents", TriggerGroup)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, TriggerGroup)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def __str__(self):
        if self.section_type == ToolshelfDock.SectionType.Actions:
            name = self.action_section_id.replace("\n", "\\n")
            suffix = "(Actions)"
        elif self.section_type == ToolshelfDock.SectionType.Special:
            name = self.special_item_type.replace("\n", "\\n")
            suffix = "(Special)"
        elif self.section_type == ToolshelfDock.SectionType.Docker:
            name = self.docker_id.replace("\n", "\\n")
            suffix = "(Docker)"
        else:
            name = self.display_name.replace("\n", "\\n")
            suffix = "(Unknown)"

        if self.hasDisplayName():
            name = self.display_name
            
        return f"{name} {suffix}"
    
    def propertygrid_hints(self):
        hints = {}
        hints["docker_size_hint"] = "the size hint of this docker; leave set to 0 for automatic sizing"
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
            "special_item_type",
        ]

        known_sliders = [
            str(self.SpecialItemType.BrushFlowSlider), 
            str(self.SpecialItemType.BrushOpacitySlider), 
            str(self.SpecialItemType.BrushSizeSlider)
        ]

        slider_groups = [
            "special_slider_orientation"
        ]

        nested_shelf_groups = [
            "special_nested_show_titlebar"
        ]

        result = []
        if self.section_type != ToolshelfDock.SectionType.Docker:
            for item in docker_groups:
                result.append(item)
        if self.section_type != ToolshelfDock.SectionType.Actions:
            for item in action_groups:
                result.append(item)
        if self.section_type != ToolshelfDock.SectionType.Special:
            for item in special_groups:
                result.append(item)

        if self.section_type != ToolshelfDock.SectionType.Special or self.special_item_type not in known_sliders:
            for item in slider_groups:
                result.append(item)

        if self.section_type != ToolshelfDock.SectionType.Special or self.special_item_type != ToolshelfDock.SpecialItemType.NestedShelf:
            for item in nested_shelf_groups:
                result.append(item)
                
        result.append("special_nested_data")

        return result

    def propertygrid_labels(self):
        labels = {}

        labels["general_group"] = "General"
        labels["variant_group"] = "Variant Options"

        labels["display_name"] = "Display Name"

        labels["max_size"] = "Max Width / Height"
        labels["min_size"] = "Min Width / Height"
        labels["section_type"] = "Section Type"

        labels["requires_specific_tool"] = "Requires Specific Tool"
        labels["invert_required_tools"] = "Invert Requirements"

        labels["docker_id"] = "Docker ID"
        labels["docker_size_hint"] = "Docker Width / Height Hint"
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
        labels["special_slider_orientation"] = "Orientation"
        labels["special_nested_show_titlebar"] = "Show Titlebar"
        return labels
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}

        global_groups = [
            "display_name",
            "min_size",
            "max_size",
            "requires_specific_tool",
            "invert_required_tools"
        ]

        variant_group = [
            "section_type",
            "docker_id", 
            "docker_size_hint",
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
            "special_slider_orientation",
            "special_nested_data",
            "special_nested_show_titlebar"
        ]

        row["general_group"] = {"items": global_groups, "is_group": True}
        row["variant_group"] = {"items": variant_group, "is_group": True}

        row["action_section_btn_size"] = {"items": ["action_section_btn_width", "action_section_btn_height"]}
        row["action_section_alignment"] = {"items": ["action_section_alignment_x","action_section_alignment_y"]}
        row["docker_size_hint"] = {"items": ["docker_size_hint_x","docker_size_hint_y"]}
        row["min_size"] = {"items": ["min_size_x","min_size_y"]}
        row["max_size"] = {"items": ["max_size_x","max_size_y"]}
        return row

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_size_hint_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["docker_size_hint_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["min_size_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["min_size_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["max_size_x"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["max_size_y"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["section_type"] = PropertyGrid_Restrictions.strValues(self.SectionType.values())
        restrictions["requires_specific_tool"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.MultiToolSelection)


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

        restrictions["special_item_type"] = PropertyGrid_Restrictions.strValues(self.SpecialItemType.values())
        restrictions["special_slider_orientation"] = PropertyGrid_Restrictions.strValues(self.SliderOrientation.values())
        return restrictions