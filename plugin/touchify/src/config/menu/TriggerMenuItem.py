from touchify.src.config.triggers.Trigger import Trigger
from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class TriggerMenuItem(Trigger):

    class Variants(EnumStr):
        Action = "action"
        Menu = "menu"
        Seperator = "seperator"

    def __defaults__(self):
        self.context_menu_actions: TypedList["TriggerMenuItem"] = []
        self.variant: str = "action"
    

    def __init__(self, **args) -> None:
        super().__defaults__()
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [])
        self.registry_id = ""
        self.context_menu_actions = JsonExtensions.init_list(args, "context_menu_actions", TriggerMenuItem)

    def getFileName(self):
        super().getFileName()
        
    def __str__(self):
        return super().__str__()

    def propertygrid_listload(self):
        super().propertygrid_listload()
        self.context_menu_actions = TypedList(self.context_menu_actions, TriggerMenuItem)

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = super().propertygrid_sisters()
        return row

    def propertygrid_sorted(self):
        result = super().propertygrid_sorted()
        result.append("context_menu_actions")
        return result

    def propertygrid_hidden(self):
        result = super().propertygrid_hidden()
        result.append("context_menu_id")   
        result.append("registry_id")
        if self.variant != TriggerMenuItem.Variants.Menu:
            result.append("context_menu_actions")
            
        return result
    
    def propertygrid_hints(self):
        hints = super().propertygrid_hints()
        return hints

    def propertygrid_labels(self):
        labels = super().propertygrid_labels()
        labels["context_menu_actions"] = "Menu Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = super().propertygrid_restrictions()
        restrictions["variant"] = DataConstraints.strEnumValues(self.Variants)
        return restrictions