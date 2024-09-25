from ...ext.JsonExtensions import JsonExtensions as Extensions
from ...ext.types.TypedList import TypedList
from .CfgToolboxItem import *

class CfgToolboxCategory:
    id: str=""
    items: TypedList[CfgToolboxItem] = []
    column_count: int = 0

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)

        items = Extensions.default_assignment(args, "items", [])
        self.items = Extensions.list_assignment(items, CfgToolboxItem)

    def addAction(self, action_id: str):
        newItem = CfgToolboxItem()
        newItem.name = action_id
        self.items.append(newItem)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_ismodel(self):
        return True

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Category ID"
        labels["column_count"] = "Column Count"
        labels["items"] = "Items"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["column_count"] = {"type": "range", "min": 0}
        return restrictions