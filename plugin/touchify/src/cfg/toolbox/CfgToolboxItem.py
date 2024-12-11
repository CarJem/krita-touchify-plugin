from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.toolbox.CfgToolboxSubItem import CfgToolboxSubItem
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat

class CfgToolboxItem:

    def __defaults__(self):
        self.name: str = ""
        self.items: TypedList[CfgToolboxSubItem] = []
        self.icon: str = ""
        self.open_on_click: bool = False

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = CfgBackwardsCompat.CfgToolboxItem(args)
        Extensions.dictToObject(self, args)
        self.items = Extensions.init_list(args, "items", CfgToolboxSubItem)

    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def toSubItem(self):
        result = CfgToolboxSubItem()
        result.name = self.name
        return result
    
    def propertygrid_sorted(self):
        return [
            "name",
            "icon",
            "open_on_click",
            "items"
        ]
    
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