from ..ext.typedlist import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions
from ..ext.extensions import nameof

class CfgToolshelfAction:
    id: str = ""
    icon: str = ""
    row: int = 0
    column: int = 0
    useActionIcon: bool = False

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["row"] = "Tab Row"
        labels["row"] = "Tab Column"
        labels["useActionIcon"] = "Use Default Icon"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["id"] = {"type": "action_selection"}
        return restrictions

class CfgToolshelfDocker:
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

    action_section_name: str = "Panel"
    action_section_contents: TypedList[CfgToolshelfAction] = []
    action_section_alignment_x: str = "none"
    action_section_alignment_y: str = "none"
    action_section_btn_width: int = 0
    action_section_btn_height: int = 0

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
        return name
    
    def propertygrid_hints(self):
        hints = {}
        hints["size_x"] = "leave set to 0 for automatic sizing"
        hints["size_y"] = "leave set to 0 for automatic sizing"
        return hints

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
        labels["docker_nesting_mode"] = "Nesting Mode"
        labels["docker_unloaded_visibility"] = "Unloaded Visibility"
        labels["docker_loading_priority"] = "Loading Priority"
        labels["section_type"] = "Section Type"

        labels["action_section_name"] = "Section Name"
        labels["action_section_contents"] = "Actions"
        labels["action_section_alignment_x"] = "Horizontal Alignment"
        labels["action_section_alignment_y"] = "Vertical Alignment"
        labels["action_section_btn_width"] = "Button Width"
        labels["action_section_btn_height"] = "Button Height"
        return labels

    def propertygrid_groups(self):

        action_groups = [
            "action_section_name", 
            "action_section_contents", 
            "action_section_alignment_x", 
            "action_section_alignment_y", 
            "action_section_btn_width", 
            "action_section_btn_height"
        ]

        docker_groups = [
            "id", 
            "docker_nesting_mode", 
            "docker_unloaded_visibility", 
            "docker_loading_priority"
        ]

        groups = {}
        groups["dockers"] = {"name": "Docker Panel...", "items": docker_groups}
        groups["actions"] = {"name": "Action Panel...", "items": action_groups}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["docker_nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["docker_unloaded_visibility"] = {"type": "values", "entries": ["normal", "hidden"]}
        restrictions["docker_loading_priority"] = {"type": "values", "entries": ["normal", "passive"]}
        restrictions["panel_x"] = {"type": "range", "min": 0}
        restrictions["panel_y"] = {"type": "range", "min": 0}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
        restrictions["min_size_x"] = {"type": "range", "min": 0}
        restrictions["min_size_y"] = {"type": "range", "min": 0}
        restrictions["max_size_x"] = {"type": "range", "min": 0}
        restrictions["max_size_y"] = {"type": "range", "min": 0}
        restrictions["section_type"] = {"type": "values", "entries": ["docker", "actions"]}
        restrictions["action_section_btn_width"] = {"type": "range", "min": 0}
        restrictions["action_section_btn_height"] = {"type": "range", "min": 0}
        restrictions["action_section_alignment_x"] = {"type": "values", "entries": ["none", "left", "center", "right", "expanding"]}
        restrictions["action_section_alignment_y"] = {"type": "values", "entries": ["none", "top", "center", "bottom", "expanding"]}
        return restrictions

class CfgToolshelfPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    quick_actions: TypedList[CfgToolshelfAction] = []
    additional_dockers: TypedList[CfgToolshelfDocker] = []
    actionHeight: int = 10

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        additional_dockers = Extensions.default_assignment(args, "additional_dockers", [])
        quick_actions = Extensions.default_assignment(args, "quick_actions", [])
        self.additional_dockers = Extensions.list_assignment(additional_dockers, CfgToolshelfDocker)
        self.quick_actions = Extensions.list_assignment(quick_actions, CfgToolshelfAction)

    def forceLoad(self):
        self.additional_dockers = TypedList(self.additional_dockers, CfgToolshelfDocker)
        self.quick_actions = TypedList(self.quick_actions, CfgToolshelfAction)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID (must be unique)"
        labels["icon"] = "Display Icon"
        labels["size_x"] = "Panel Width"
        labels["size_y"] = "Panel Height"
        labels["row"] = "Tab Row"
        labels["additional_dockers"] = "Dockers"
        labels["quick_actions"] = "Actions"
        labels["actionHeight"] = "Action Button Height"
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
    dockers: TypedList[CfgToolshelfDocker] = []
    
    titleButtonHeight: int = 10
    dockerButtonHeight: int = 32
    dockerBackHeight: int = 16
    sliderHeight: int = 16
    actionHeight: int = 16

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        panels = Extensions.default_assignment(args, "panels", [])
        self.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgToolshelfAction)
        dockers = Extensions.default_assignment(args, "dockers", [])
        self.dockers = Extensions.list_assignment(dockers, CfgToolshelfDocker)
    
    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolshelfPanel)
        self.actions = TypedList(self.actions, CfgToolshelfAction)
        self.dockers = TypedList(self.dockers, CfgToolshelfDocker)

    def propertygrid_labels(self):
        labels = {}
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["titleButtonHeight"] = "Title Button Height"
        labels["dockerButtonHeight"] = "Docker Button Height"
        labels["dockerBackHeight"] = "Back Button Height"
        labels["sliderHeight"] = "Slider Height"
        labels["actionHeight"] = "Action Button Height"
        labels["dockers"] = "Dockers"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


