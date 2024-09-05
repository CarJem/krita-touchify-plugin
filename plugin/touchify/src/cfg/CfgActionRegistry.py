from .action.CfgTouchifyActionDockerGroup import *
from .action.CfgTouchifyActionPopup import *
from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions
from .action.CfgTouchifyAction import *
    
class CfgActionRegistry:
    actions_registry: TypedList[CfgTouchifyAction] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        actions_registry = Extensions.default_assignment(args, "actions_registry", [])
        self.actions_registry = Extensions.list_assignment(actions_registry, CfgTouchifyAction)

    def forceLoad(self):
        self.actions_registry = TypedList(self.actions_registry, CfgTouchifyAction)

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["actions_registry"] = "Registered Actions"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions