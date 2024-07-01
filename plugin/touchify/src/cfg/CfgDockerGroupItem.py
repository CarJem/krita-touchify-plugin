from ..ext.extensions_json import JsonExtensions as Extensions


class CfgDockerGroupItem:
    id: str=""

    def create(args):
        obj = CfgDockerGroupItem()
        Extensions.dictToObject(obj, args)
        return obj

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