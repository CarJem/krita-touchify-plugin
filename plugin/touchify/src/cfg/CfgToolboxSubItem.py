from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions

class CfgToolboxSubItem:

    name: str = ""

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
    
    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Action ID"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = {"type": "action_selection"}
        return restrictions