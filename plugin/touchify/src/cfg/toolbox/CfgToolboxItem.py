from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from .CfgToolboxSubItem import CfgToolboxSubItem

class CfgToolboxItem:

    name: str = ""
    items: TypedList[CfgToolboxSubItem] = []



    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

        items = Extensions.default_assignment(args, "items", [])
        self.items = Extensions.list_assignment(items, CfgToolboxSubItem)

    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def toSubItem(self):
        result = CfgToolboxSubItem()
        result.name = self.name
        return result
    
    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Action ID"
        labels["items"] = "Subitems"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = {"type": "action_selection"}
        return restrictions