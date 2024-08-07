from .CfgTouchifyAction import *
from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions
from ..ext.extensions import nameof

class CfgTouchifyActionGroup:
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

    def propertygrid_groups(self):
        groups = {}
        return groups
    
    
    def propertygrid_ismodel(self):
        return True

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions