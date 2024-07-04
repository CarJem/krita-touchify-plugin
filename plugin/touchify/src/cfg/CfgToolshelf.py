from ..ext.typedlist import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions

class CfgToolshelfAction:
    id: str = ""
    icon: str = ""
    row: int = 0
    column: int = 0

    def create(args):
        obj = CfgToolshelfAction()
        Extensions.dictToObject(obj, args)
        return obj

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
    panel_y: int = 0
    panel_x: int = 0

    nesting_mode: str = "normal"
    unloaded_visibility: str = "normal"
    loading_priority: str = "normal"

    section_type: str = "docker"
    

    action_section_name: str = "Panel"
    action_section_contents: TypedList[CfgToolshelfAction] = []
    action_section_alignment_x: str = "none"
    action_section_alignment_y: str = "none"
    action_section_btn_width: int = 0
    action_section_btn_height: int = 0

    def create(args):
        obj = CfgToolshelfDocker()
        Extensions.dictToObject(obj, args)
        action_section_contents = Extensions.default_assignment(args, "action_section_contents", [])
        obj.action_section_contents = Extensions.list_assignment(action_section_contents, CfgToolshelfAction)
        return obj

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
        labels["size_x"] = "Docker Width"
        labels["size_y"] = "Docker Height"
        labels["panel_y"] = "Panel Row"
        labels["panel_x"] = "Panel Column"
        labels["nesting_mode"] = "Nesting Mode"
        labels["unloaded_visibility"] = "Unloaded Visibility"
        labels["loading_priority"] = "Loading Priority"
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
            "nesting_mode", 
            "unloaded_visibility", 
            "loading_priority"
        ]

        groups = {}
        groups["dockers"] = {"name": "Docker Panel...", "items": docker_groups}
        groups["actions"] = {"name": "Action Panel...", "items": action_groups}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["unloaded_visibility"] = {"type": "values", "entries": ["normal", "hidden"]}
        restrictions["loading_priority"] = {"type": "values", "entries": ["normal", "passive"]}
        restrictions["panel_x"] = {"type": "range", "min": 0}
        restrictions["panel_y"] = {"type": "range", "min": 0}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
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

    def create(args):
        obj = CfgToolshelfPanel()
        Extensions.dictToObject(obj, args)
        additional_dockers = Extensions.default_assignment(args, "additional_dockers", [])
        quick_actions = Extensions.default_assignment(args, "quick_actions", [])
        obj.additional_dockers = Extensions.list_assignment(additional_dockers, CfgToolshelfDocker)
        obj.quick_actions = Extensions.list_assignment(quick_actions, CfgToolshelfAction)
        return obj

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
        labels["additional_action_areas"] = "Action Dockers"
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

    def create(args):
        obj = CfgToolshelf()
        Extensions.dictToObject(obj, args)
        panels = Extensions.default_assignment(args, "panels", [])
        obj.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        obj.actions = Extensions.list_assignment(actions, CfgToolshelfAction)
        dockers = Extensions.default_assignment(args, "dockers", [])
        obj.dockers = Extensions.list_assignment(dockers, CfgToolshelfDocker)
        return obj
    
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
        labels["action_dockers"] = "Action Dockers"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


