from .CfgToolboxAction import CfgToolboxAction
from .CfgToolboxPanel import CfgToolboxPanel
from ..ext.extensions import Extensions
from .CfgToolboxPanelDocker import *
from ..ext.typedlist import *


class CfgToolshelf:

    panels: TypedList[CfgToolboxPanel] = []
    actions: TypedList[CfgToolboxAction] = []
    
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
        return obj
    
    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolboxPanel)
        self.actions = TypedList(self.actions, CfgToolboxAction)

    def propertygrid_labels(self):
        labels = {}
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["titleButtonHeight"] = "Title Button Height"
        labels["dockerButtonHeight"] = "Docker Button Height"
        labels["dockerBackHeight"] = "Back Button Height"
        labels["sliderHeight"] = "Slider Height"
        labels["actionHeight"] = "Action Button Height"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions