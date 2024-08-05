from .CfgDockerGroup import *
from .CfgPopup import *
from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions
from .CfgTouchifyAction import *
    
class CfgTouchifyRegistry:
    actions_registry: TypedList[CfgTouchifyAction] = []
    popups_registry: TypedList[CfgPopup] = []
    docker_groups_registry: TypedList[CfgDockerGroup] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        actions_registry = Extensions.default_assignment(args, "actions_registry", [])
        self.actions_registry = Extensions.list_assignment(actions_registry, CfgTouchifyAction)
        
        popups_registry = Extensions.default_assignment(args, "popups_registry", [])
        self.popups_registry = Extensions.list_assignment(popups_registry, CfgPopup)
        
        docker_groups_registry = Extensions.default_assignment(args, "docker_groups_registry", [])
        self.docker_groups_registry = Extensions.list_assignment(docker_groups_registry, CfgDockerGroup)

    def forceLoad(self):
        self.actions_registry = TypedList(self.actions_registry, CfgTouchifyAction)
        self.popups_registry = TypedList(self.popups_registry, CfgPopup)
        self.docker_groups_registry = TypedList(self.docker_groups_registry, CfgDockerGroup)

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["actions_registry"] = "Registered Actions"
        labels["popups_registry"] = "Popups"
        labels["docker_groups_registry"] = "Docker Groups"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions