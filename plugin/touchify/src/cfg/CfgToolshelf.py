from re import A
from ..ext.typedlist import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions

class CfgToolboxPanelDocker:
    id: str = ""
    size_x: int = 0
    size_y: int = 0
    nesting_mode: str = "normal"
    unloaded_visibility: str = "normal"
    loading_priority: str = "normal"
    panel_y: int = 0

    def create(args):
        obj = CfgToolboxPanelDocker()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Docker ID"
        labels["size_x"] = "Docker Width (leave unset for auto)"
        labels["size_y"] = "Docker Height (leave unset for auto)"
        labels["panel_y"] = "Panel Row"
        labels["nesting_mode"] = "Nesting Mode"
        labels["unloaded_visibility"] = "Unloaded Visibility"
        labels["loading_priority"] = "Loading Priority"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        restrictions["nesting_mode"] = {"type": "values", "entries": ["normal", "docking"]}
        restrictions["unloaded_visibility"] = {"type": "values", "entries": ["normal", "hidden"]}
        restrictions["loading_priority"] = {"type": "values", "entries": ["normal", "passive"]}
        restrictions["panel_x"] = {"type": "range", "min": 0, "max": 10}
        restrictions["panel_y"] = {"type": "range", "min": 0, "max": 10}
        return restrictions

class CfgToolboxAction:
    id: str = ""
    icon: str = ""
    row: int = 0

    def create(args):
        obj = CfgToolboxAction()
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
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["id"] = {"type": "action_selection"}
        return restrictions

class CfgToolboxPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    quick_actions: TypedList[CfgToolboxAction] = []
    additional_dockers: TypedList[CfgToolboxPanelDocker] = []
    actionHeight: int = 10

    def create(args):
        obj = CfgToolboxPanel()
        Extensions.dictToObject(obj, args)
        additional_dockers = Extensions.default_assignment(args, "additional_dockers", [])
        quick_actions = Extensions.default_assignment(args, "quick_actions", [])
        obj.additional_dockers = Extensions.list_assignment(additional_dockers, CfgToolboxPanelDocker)
        obj.quick_actions = Extensions.list_assignment(quick_actions, CfgToolboxAction)
        return obj

    def forceLoad(self):
        self.additional_dockers = TypedList(self.additional_dockers, CfgToolboxPanelDocker)
        self.quick_actions = TypedList(self.quick_actions, CfgToolboxAction)

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

    panels: TypedList[CfgToolboxPanel] = []
    actions: TypedList[CfgToolboxAction] = []
    dockers: TypedList[CfgToolboxPanelDocker] = []
    
    titleButtonHeight: int = 10
    dockerButtonHeight: int = 32
    dockerBackHeight: int = 16
    sliderHeight: int = 16
    actionHeight: int = 16

    def create(args):
        obj = CfgToolshelf()
        Extensions.dictToObject(obj, args)
        panels = Extensions.default_assignment(args, "panels", [])
        obj.panels = Extensions.list_assignment(panels, CfgToolboxPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        obj.actions = Extensions.list_assignment(actions, CfgToolboxAction)
        dockers = Extensions.default_assignment(args, "dockers", [])
        obj.dockers = Extensions.list_assignment(dockers, CfgToolboxPanelDocker)
        return obj
    
    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolboxPanel)
        self.actions = TypedList(self.actions, CfgToolboxAction)
        self.dockers = TypedList(self.dockers, CfgToolboxAction)

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


