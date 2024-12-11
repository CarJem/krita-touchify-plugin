from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions

HAS_ALREADY_LOADED: bool = False

class ResourcePackMetadata:
    def __defaults__(self):
        self.json_version: int = 1
        self.registry_id: str = "NewActRegistry"
        self.registry_name: str = "New Action Registry"

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)

    def forceLoad(self):
        pass

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["registry_id"] = "Registry ID"
        labels["registry_name"] = "Registry Name"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions    