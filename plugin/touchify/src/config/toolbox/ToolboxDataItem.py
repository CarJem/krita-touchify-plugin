from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from touchify.src.config.toolbox.ToolboxDataSubitem import ToolboxDataSubitem
from touchify.src.config.TouchifyCompatibility import TouchifyCompatibility
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class ToolboxDataItem:

    def __defaults__(self):
        self.name: str = ""
        self.items: TypedList[ToolboxDataSubitem] = []
        self.icon: str = ""
        self.open_on_click: bool = False

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = TouchifyCompatibility.ToolboxDataItem(args)
        JsonExtensions.dictToObject(self, args)
        self.items = JsonExtensions.init_list(args, "items", ToolboxDataSubitem)

    def __str__(self):
        return KritaExtensions.getActionText(self.name)
    
    def toSubItem(self):
        result = ToolboxDataSubitem()
        result.name = self.name
        return result
    
    def propertygrid_icon(self):
        from PyQt5.QtGui import QIcon
        from jemlib.api_krita import KritaAPI
        try:
            return KritaAPI.get_action(self.name).icon()
        except:
            return QIcon()
    
    def propertygrid_hidden(self):
        return [

        ]
    
    def propertygrid_view_type(self):
        return "form_alt"
    
    def propertygrid_sorted(self):
        return [
            "name",
            "icon",
            "open_on_click",
            "items"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Action"
        labels["icon"] = "Custom Icon"
        labels["open_on_click"] = "Click to Open Menu"
        labels["items"] = "Menu Items"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["icon"] = DataConstraints.strMod(DataConstraints.StrMod.IconSelection)
        return restrictions