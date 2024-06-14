from ..ext.extensions import Extensions


class DockerGroupItems:
    id: str=""

    def create(args):
        obj = DockerGroupItems()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_ismodel(self):
        return True

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        return restrictions