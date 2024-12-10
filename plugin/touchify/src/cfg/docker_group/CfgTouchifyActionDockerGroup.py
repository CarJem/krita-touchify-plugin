from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.docker_group.CfgTouchifyActionDockerGroupItem import CfgTouchifyActionDockerGroupItem
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat

class CfgTouchifyActionDockerGroup:
    id: str = ""
    tabs_mode: bool = True
    group_id: str = ""
    docker_names: TypedList[CfgTouchifyActionDockerGroupItem] = []

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgTouchifyActionDockerGroup(args)
        Extensions.dictToObject(self, args)
        self.docker_names = Extensions.init_list(args, "docker_names", CfgTouchifyActionDockerGroupItem)

    def getFileName(self):
        return FileExtensions.fileStringify(self.id)

    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, CfgTouchifyActionDockerGroupItem)

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