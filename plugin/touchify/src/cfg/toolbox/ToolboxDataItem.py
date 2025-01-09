from touchify.src.components.python.datatypes.TypedList import TypedList
from touchify.src.components.python.json_extensions import JsonExtensions as Extensions
from touchify.src.cfg.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolboxDataItem:

    def __defaults__(self):
        self.name: str = ""
        self.items: TypedList[ToolboxDataSubitem] = []
        self.icon: str = ""
        self.open_on_click: bool = False

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolboxDataItem(args)
        Extensions.dictToObject(self, args)
        self.items = Extensions.init_list(args, "items", ToolboxDataSubitem)

    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def toSubItem(self):
        result = ToolboxDataSubitem()
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
        restrictions["name"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.Actions)
        restrictions["icon"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.Icon)
        return restrictions