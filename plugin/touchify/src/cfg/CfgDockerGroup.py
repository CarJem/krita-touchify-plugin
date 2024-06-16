from .CfgDockerGroupItem import CfgDockerGroupItem
from ..ext.extensions import Extensions, TypedList


class CfgDockerGroup:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[CfgDockerGroupItem] = []

    def create(args):
        obj = CfgDockerGroup()
        Extensions.dictToObject(obj, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        obj.docker_names = Extensions.list_assignment(docker_names, CfgDockerGroupItem)
        return obj

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgDockerGroupItem)

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions