from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.toolbox.ToolboxDataItem import *

class ToolboxDataCategory:
    def __defaults__(self):
        self.id: str=""
        self.items: TypedList[ToolboxDataItem] = []
        self.column_count: int = 0

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)
        self.items = Extensions.init_list(args, "items", ToolboxDataItem)

    def addAction(self, action_id: str):
        newItem = ToolboxDataItem()
        newItem.name = action_id
        self.items.append(newItem)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        self.items = TypedList(self.items, ToolboxDataItem)


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