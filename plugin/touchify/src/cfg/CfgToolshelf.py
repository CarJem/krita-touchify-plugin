from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions


class CfgToolshelfActionSubItem:
    id: str=""

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_ismodel(self):
        return True
    
    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Action ID"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "action_selection"}
        return restrictions

class CfgToolshelfAction:
    icon: str = ""
    row: int = 0
    text: str = ""
    use_icon: bool = True
    
    action_type: str = "action"
    
    action_id: str = ""
    action_use_default_icon: bool = False

    context_menu_actions: TypedList[CfgToolshelfActionSubItem] = []
    context_menu_name: str = ""
    
    brush_name: str = ""
    brush_override_icon: bool = False

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        context_menu_actions = Extensions.default_assignment(args, "context_menu_actions", [])
        self.context_menu_actions = Extensions.list_assignment(context_menu_actions, CfgToolshelfActionSubItem)

    def __str__(self):
        if self.action_type == "brush":
            name = self.brush_name.replace("\n", "\\n") + " (Brush)"
        elif self.action_type == "menu":
            name = self.context_menu_name.replace("\n", "\\n") + " (Menu)"
        else:
            name = self.action_id.replace("\n", "\\n") 
        return name

    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, CfgToolshelfActionSubItem)

    def propertygrid_hidden(self):
        result = []
        if self.action_type != "action":
            result.append("action_id")
            result.append("action_use_default_icon")
        if self.action_type != "menu":
            result.append("context_menu_name")
            result.append("context_menu_actions")
        if self.action_type != "brush":
            result.append("brush_name")
            result.append("brush_override_icon")  
        if self.action_type == "brush" and self.brush_override_icon == False:
            result.append("icon") 
            result.append("use_icon")
            result.append("text")  
        result.append("text" if self.use_icon else "icon")
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["action_id"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["row"] = "Tab Row"
        labels["action_type"] = "Action Type"
        labels["use_icon"] = "Use Icon"
        
        labels["action_use_default_icon"] = "Use Default Icon"

        labels["context_menu_name"] = "Menu Name"
        labels["context_menu_actions"] = "Menu Actions"
        
        labels["brush_name"] = "Brush"
        labels["brush_override_icon"] = "Override Brush Icon"

        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["action_type"] = {"type": "values", "entries": ["action", "menu", "brush"]}
        restrictions["brush_name"] = {"type": "brush_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action_id"] = {"type": "action_selection"}
        return restrictions

class CfgToolshelfSection:
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
    action_section_contents: TypedList[CfgToolshelfAction] = []
    action_section_alignment_x: str = "none"
    action_section_alignment_y: str = "none"
    action_section_btn_width: int = 0
    action_section_btn_height: int = 0
    action_section_icon_size: int = 0

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        action_section_contents = Extensions.default_assignment(args, "action_section_contents", [])
        self.action_section_contents = Extensions.list_assignment(action_section_contents, CfgToolshelfAction)

    def forceLoad(self):
        self.action_section_contents = TypedList(self.action_section_contents, CfgToolshelfAction)

    def __str__(self):
        if self.section_type == "actions":
            name = self.action_section_name.replace("\n", "\\n") + " (Actions)"
        else:
            name = self.id.replace("\n", "\\n")
            
        name += f" [{self.panel_x}, {self.panel_y}]"
        return name
    
    def propertygrid_hints(self):
        hints = {}
        hints["size_x"] = "leave set to 0 for automatic sizing"
        hints["size_y"] = "leave set to 0 for automatic sizing"
        return hints
    
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

        result = []
        if self.section_type != "docker":
            for item in docker_groups:
                result.append(item)
        if self.section_type != "actions":
            for item in action_groups:
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

    def propertygrid_groups(self):
        groups = {}
        return groups

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
        restrictions["section_type"] = {"type": "values", "entries": ["docker", "actions"]}

        restrictions["docker_nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["docker_unloaded_visibility"] = {"type": "values", "entries": ["normal", "hidden"]}
        restrictions["docker_loading_priority"] = {"type": "values", "entries": ["normal", "passive"]}

        restrictions["action_section_display_mode"] = {"type": "values", "entries": ["normal", "flat"]}
        restrictions["action_section_btn_width"] = {"type": "range", "min": 0}
        restrictions["action_section_btn_height"] = {"type": "range", "min": 0}
        restrictions["action_section_alignment_x"] = {"type": "values", "entries": ["none", "left", "center", "right", "expanding"]}
        restrictions["action_section_alignment_y"] = {"type": "values", "entries": ["none", "top", "center", "bottom", "expanding"]}
        restrictions["action_section_icon_size"] = {"type": "range", "min": 0}
        return restrictions

class CfgToolshelfPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    actions: TypedList[CfgToolshelfAction] = []
    sections: TypedList[CfgToolshelfSection] = []
    section_show_tabs: bool = False
    
    actionHeight: int = 10

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        sections = Extensions.default_assignment(args, "sections", [])
        actions = Extensions.default_assignment(args, "actions", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)
        self.actions = Extensions.list_assignment(actions, CfgToolshelfAction)

    def forceLoad(self):
        self.sections = TypedList(self.sections, CfgToolshelfSection)
        self.actions = TypedList(self.actions, CfgToolshelfAction)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["size"] = {"name": "Panel Width / Height", "items": ["size_x","size_y"]}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID (must be unique)"
        labels["icon"] = "Display Icon"
        labels["size_x"] = "Panel Width"
        labels["size_y"] = "Panel Height"
        labels["row"] = "Tab Row"
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        labels["actionHeight"] = "Action Button Height"
        labels["section_show_tabs"] = "Show Tabs"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
        
class CfgToolshelf:
    panels: TypedList[CfgToolshelfPanel] = []
    actions: TypedList[CfgToolshelfAction] = []
    sections: TypedList[CfgToolshelfSection] = []
    
    dockerButtonHeight: int = 32
    dockerBackHeight: int = 16
    actionHeight: int = 16

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        panels = Extensions.default_assignment(args, "panels", [])
        self.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgToolshelfAction)
        sections = Extensions.default_assignment(args, "sections", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)
    
    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolshelfPanel)
        self.actions = TypedList(self.actions, CfgToolshelfAction)
        self.sections = TypedList(self.sections, CfgToolshelfSection)

    def propertygrid_labels(self):
        labels = {}
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["sections"] = "Sections"
        labels["dockerButtonHeight"] = "Docker Button Height"
        labels["dockerBackHeight"] = "Back Button Height"
        labels["actionHeight"] = "Action Button Height"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


