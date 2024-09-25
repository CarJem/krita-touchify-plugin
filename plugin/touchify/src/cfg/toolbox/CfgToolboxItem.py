from ...ext.types.TypedList import TypedList
from ...ext.JsonExtensions import JsonExtensions as Extensions
from .CfgToolboxSubItem import CfgToolboxSubItem
from ..CfgBackwardsCompat import CfgBackwardsCompat

class CfgToolboxItem:

    name: str = ""
    items: TypedList[CfgToolboxSubItem] = []
    icon: str = ""
    open_on_click: bool = False

    json_version: int = 1

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolboxItem(args)
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
        labels["icon"] = "Custom Icon"
        labels["open_on_click"] = "Open Submenu on Click"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = {"type": "action_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions