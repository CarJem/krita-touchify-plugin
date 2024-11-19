from touchify.src.cfg.action.CfgTouchifyActionDockerGroup import *
from touchify.src.cfg.action.CfgTouchifyActionPopup import *
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.action.CfgTouchifyAction import *
    
class CfgActionRegistry:
    actions_registry: TypedList[CfgTouchifyAction] = []

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        self.actions_registry = Extensions.init_list(args, "actions_registry", CfgTouchifyAction)

    def forceLoad(self):
        self.actions_registry = TypedList(self.actions_registry, CfgTouchifyAction)

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["actions_registry"] = "Registered Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions