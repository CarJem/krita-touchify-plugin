from typing import TYPE_CHECKING
from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify.src.config.TouchifyCompatibility import TouchifyCompatibility

if TYPE_CHECKING:
    from touchify.src.config.triggers.Trigger import Trigger

class ContextMenu:

    def __defaults__(self):
        self.registry_id: str = "NewTriggerMenu" 
        self.registry_name: str = "New Trigger Menu"

        #Menu Params
        self.context_menu_actions: TypedList["Trigger"] = []

        self.json_version: int = 2
    

    def __init__(self, **args) -> None:
        from touchify.src.config.triggers.Trigger import Trigger
        self.__defaults__()
        args = TouchifyCompatibility.TriggerContextMenu(args)
        JsonExtensions.dictToObject(self, args, [])
        self.context_menu_actions = JsonExtensions.init_list(args, "context_menu_actions", Trigger)

    def getDisplayName(self):
        return self.registry_name

    def getFileName(self):
        return FileExtensions.fileStringify(self.registry_id)
        
    def __str__(self):
        return self.getDisplayName()

    def propertygrid_listload(self):
        from touchify.src.config.triggers.Trigger import Trigger
        self.context_menu_actions = TypedList(self.context_menu_actions, Trigger)

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
        labels["registry_name"] = "Display Name"

        labels["context_menu_actions"] = "Menu Triggers"

        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions