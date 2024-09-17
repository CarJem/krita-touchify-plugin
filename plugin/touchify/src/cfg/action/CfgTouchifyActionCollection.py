from touchify.src.cfg.action.CfgTouchifyAction import *
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions

class CfgTouchifyActionCollection:
    actions: TypedList["CfgTouchifyAction"] = []
    row_name: str = "Actions Row"

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgTouchifyAction)

    def forceLoad(self):
        self.actions = TypedList(self.actions, CfgTouchifyAction)

    def __str__(self):
        return self.row_name
    
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