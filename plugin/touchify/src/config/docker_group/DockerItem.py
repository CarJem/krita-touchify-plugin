from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints


class DockerItem:
    
    def __defaults__(self):
        self.id: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_ismodel(self):
        return True

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Docker ID"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = DataConstraints.strMod(DataConstraints.StrMod.DockerSelection)
        return restrictions