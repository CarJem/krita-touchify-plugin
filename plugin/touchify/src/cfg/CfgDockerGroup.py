from ..ext.extensions_json import JsonExtensions as Extensions
from ..ext.extensions import TypedList
from .CfgDockerGroupItem import CfgDockerGroupItem

class CfgDockerGroup:
    id: str = ""
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[CfgDockerGroupItem] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        self.docker_names = Extensions.list_assignment(docker_names, CfgDockerGroupItem)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgDockerGroupItem)

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