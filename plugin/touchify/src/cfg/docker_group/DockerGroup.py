from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.docker_group.DockerGroupItem import DockerGroupItem
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility

class DockerGroup:

    def __defaults__(self):
        self.id: str = ""
        self.tabs_mode: bool = True
        self.group_id: str = ""
        self.docker_names: TypedList[DockerGroupItem] = []

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.DockerGroup(args)
        Extensions.dictToObject(self, args)
        self.docker_names = Extensions.init_list(args, "docker_names", DockerGroupItem)

    def getFileName(self):
        return FileExtensions.fileStringify(self.id)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, DockerGroupItem)

    def propertygrid_sorted(self):
        return [
            "id",
            "group_id",
            "tabs_mode",
            "docker_names"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Group ID"
        labels["tabs_mode"] = "Tab Mode"
        labels["group_id"] = "Tab Mode Group ID"
        labels["docker_names"] = "Dockers"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions