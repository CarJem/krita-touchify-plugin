from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions


class DockerGroupItem:
    
    def __defaults__(self):
        self.id: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)

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
        restrictions["id"] = {"type": "docker_selection"}
        return restrictions