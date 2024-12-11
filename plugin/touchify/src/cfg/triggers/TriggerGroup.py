
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions

class TriggerGroup:
    
    def __defaults__(self):
        self.row_name: str = "Actions Row"

        from touchify.src.cfg.triggers.Trigger import Trigger
        self.actions: TypedList[Trigger] = []

    def __init__(self, **args) -> None:
        
        self.__defaults__()
        Extensions.dictToObject(self, args)
        from touchify.src.cfg.triggers.Trigger import Trigger
        self.actions = Extensions.init_list(args, "actions", Trigger)

    def forceLoad(self):
        from touchify.src.cfg.triggers.Trigger import Trigger
        self.actions = TypedList(self.actions, Trigger)

    def __str__(self):
        return self.row_name.replace("\n", "\\n")
    
    def propertygrid_hints(self):
        hints = {}
        return hints
    
    def propertygrid_hidden(self):
        result = []
        return result
    
    def propertygrid_sorted(self):
        return [
            "row_name",
            "actions",
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["actions"] = "Actions"
        labels["row_name"] = "Row Name"
        return labels
    
    
    def propertygrid_ismodel(self):
        return True

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions