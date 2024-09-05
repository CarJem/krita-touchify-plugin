from ...ext.extensions_json import JsonExtensions as Extensions
from ...ext.extensions import TypedList, nameof


class CfgTouchifyActionDockerGroupItem:
    id: str=""

    def __init__(self, **args) -> None:
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