from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.toolbox.CfgToolboxItem import *

class CfgToolboxCategory:
    id: str=""
    items: TypedList[CfgToolboxItem] = []
    column_count: int = 0

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        self.items = Extensions.init_list(args, "items", CfgToolboxItem)

    def addAction(self, action_id: str):
        newItem = CfgToolboxItem()
        newItem.name = action_id
        self.items.append(newItem)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        self.items = TypedList(self.items, CfgToolboxItem)


    def propertygrid_ismodel(self):
        return True
    
    def propertygrid_sorted(self):
        return [
            "id",
            "column_count",
            "items"
        ]

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