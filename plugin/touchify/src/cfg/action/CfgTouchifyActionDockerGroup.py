from ...ext.JsonExtensions import JsonExtensions as Extensions
from ...ext.types.TypedList import TypedList
from .CfgTouchifyActionDockerGroupItem import CfgTouchifyActionDockerGroupItem
from ..CfgBackwardsCompat import CfgBackwardsCompat

class CfgTouchifyActionDockerGroup:
    id: str = ""
    tabs_mode: bool = True
    group_id: str = ""
    docker_names: TypedList[CfgTouchifyActionDockerGroupItem] = []

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgTouchifyActionDockerGroup(args)
        Extensions.dictToObject(self, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        self.docker_names = Extensions.list_assignment(docker_names, CfgTouchifyActionDockerGroupItem)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgTouchifyActionDockerGroupItem)
    
    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Group ID (should be unique)"
        labels["tabs_mode"] = "Tab Mode"
        labels["group_id"] = "Tab Mode Group ID"
        labels["docker_names"] = "Dockers"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions