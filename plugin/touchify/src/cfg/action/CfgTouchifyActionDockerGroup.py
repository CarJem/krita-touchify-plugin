from ...ext.extensions_json import JsonExtensions as Extensions
from ...ext.extensions import TypedList
from .CfgTouchifyActionDockerGroupItem import CfgTouchifyActionDockerGroupItem

class CfgTouchifyActionDockerGroup:
    id: str = ""
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[CfgTouchifyActionDockerGroupItem] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        self.docker_names = Extensions.list_assignment(docker_names, CfgTouchifyActionDockerGroupItem)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgTouchifyActionDockerGroupItem)

    def propertygrid_groups(self):
        groups = {}
        return groups
    
    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Group ID (should be unique)"
        labels["tabsMode"] = "Tab Mode"
        labels["groupId"] = "Tab Mode Group ID"
        labels["docker_names"] = "Dockers"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions