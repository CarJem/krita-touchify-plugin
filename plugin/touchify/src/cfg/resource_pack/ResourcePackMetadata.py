import textwrap
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

    def propertygrid_hints(self):
        labels = {}

        labels["registry_id"] = textwrap.dedent("""\
        The internal id used for this resource pack registry.
        It is used to register triggers to krita's action system and initalize the folder name of the resource pack.
        Keep it unique to prevent conflicts with other resource packs, and avoid changing it""")

        labels["registry_name"] = textwrap.dedent("""\
        The display name for this resource pack registry.
        Can be freely changed and set to anything you desire""")

        return labels
    
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