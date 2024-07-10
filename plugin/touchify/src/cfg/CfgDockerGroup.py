from .CfgDockerGroupItem import CfgDockerGroupItem
from ..ext.extensions_json import JsonExtensions as Extensions
from ..ext.extensions import TypedList


class CfgDockerGroup:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[CfgDockerGroupItem] = []

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        self.docker_names = Extensions.list_assignment(docker_names, CfgDockerGroupItem)

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgDockerGroupItem)

    def propertygrid_groups(self):
        groups = {}
        return groups
    
    def propertygrid_labels(self):
        labels = {}
        labels["display_name"] = "Display Name"
        labels["id"] = "Group ID (should be unique)"
        labels["icon"] = "Preview Icon"
        labels["tabsMode"] = "Tab Mode"
        labels["groupId"] = "Tab Mode Group ID"
        labels["docker_names"] = "Dockers"
        labels["hotkeyNumber"] = "Activation Hotkey"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions