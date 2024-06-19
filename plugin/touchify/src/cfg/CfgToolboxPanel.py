from ..ext.extensions import Extensions
from .CfgToolboxPanelDocker import *
from ..ext.typedlist import *


class CfgToolboxPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    isEnabled: bool = False
    additional_dockers: TypedList[CfgToolboxPanelDocker] = []

    def create(args):
        obj = CfgToolboxPanel()
        Extensions.dictToObject(obj, args)
        additional_dockers = Extensions.default_assignment(args, "additional_dockers", [])
        obj.additional_dockers = Extensions.list_assignment(additional_dockers, CfgToolboxPanelDocker)
        return obj
    
    def forceLoad(self):
        self.additional_dockers = TypedList(self.additional_dockers, CfgToolboxPanelDocker)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        if not self.isEnabled:
            name = "(Disabled) " + name
        return name

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID (must be unique)"
        labels["icon"] = "Display Icon"
        labels["isEnabled"] = "Active"
        labels["size_x"] = "Panel Width"
        labels["size_y"] = "Panel Height"
        labels["additional_dockers"] = "Dockers"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions