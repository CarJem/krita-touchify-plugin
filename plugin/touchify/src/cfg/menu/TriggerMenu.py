from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.menu.TriggerMenuItem import TriggerMenuItem

class TriggerMenu:

    def __defaults__(self):
        self.registry_id: str = ""    
        self.registry_name: str = "New Trigger Menu"  

        #Menu Params
        self.context_menu_actions: TypedList["TriggerMenuItem"] = []

        self.json_version: int = 1
    

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args, [])
        self.context_menu_actions = Extensions.init_list(args, "context_menu_actions", TriggerMenuItem)

    def getFileName(self):
        return FileExtensions.fileStringify(self.registry_id)
        
    def __str__(self):
        return self.registry_name


    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, TriggerMenuItem)

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}

        return row

    def propertygrid_sorted(self):
        return [
            "registry_id",
            "registry_name",
            "context_menu_actions"
        ]

    def propertygrid_hidden(self):
        result = []
        return result
    
    def propertygrid_hints(self):
        hints = {}
        return hints

    def propertygrid_labels(self):
        labels = {}
        
        labels["registry_id"] = "Registry ID"
        labels["registry_name"] = "Registry Name"

        labels["context_menu_actions"] = "Menu Triggers"

        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions