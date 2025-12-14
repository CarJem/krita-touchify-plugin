from touchify.src.extensions.file_extensions import FileExtensions
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.alib_datatypes.TypedList import TypedList
from touchify.src.config.docker_group.DockerItem import DockerItem
from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility

class DockerGroup:

    def __defaults__(self):
        self.registry_name: str = "New Docker Group"
        self.id: str = "NewDockerGroup"
        self.tabs_mode: bool = True
        self.group_id: str = ""
        self.docker_names: TypedList[DockerItem] = []

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.DockerGroup(args)
        JsonExtensions.dictToObject(self, args)
        self.docker_names = JsonExtensions.init_list(args, "docker_names", DockerItem)

    def __str__(self):
        return self.registry_name

    def getFileName(self):
        return FileExtensions.fileStringify(self.id)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, DockerItem)

    def propertygrid_sorted(self):
        return [
            "registry_name",
            "id",
            "group_id",
            "tabs_mode",
            "docker_names"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["registry_name"] = "Registry Name"
        labels["id"] = "Group ID"
        labels["tabs_mode"] = "Tab Mode"
        labels["group_id"] = "Tab Mode Group ID"
        labels["docker_names"] = "Dockers"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions