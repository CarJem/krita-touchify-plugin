from .DockerGroupItems import DockerGroupItems
from ..ext.extensions import Extensions, TypedList


class DockerGroup:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[DockerGroupItems] = []

    def create(args):
        obj = DockerGroup()
        Extensions.dictToObject(obj, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        obj.docker_names = Extensions.list_assignment(docker_names, DockerGroupItems)
        return obj

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, DockerGroupItems)

    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions