from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions

class ToolboxDataSubitem:

    def __defaults__(self):
        self.name: str = ""
        self.icon: str = ""

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args)
    
    def __str__(self):
        return KritaExtensions.getActionText(self.name)
    
    def propertygrid_ismodel(self):
        return True
    
    def propertygrid_hidden(self):
        return [
            "name"
        ]

    def propertygrid_sorted(self):
        return [
            "name",
            "icon"
        ]
    
    def propertygrid_icon(self):
        from PyQt5.QtGui import QIcon
        from jemlib.api_krita import KritaAPI
        try:
            return KritaAPI.get_action(self.name).icon()
        except:
            return QIcon()
    
    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Action ID"
        labels["icon"] = "Custom Icon"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["name"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["icon"] = DataConstraints.strMod(DataConstraints.StrMod.IconSelection)
        return restrictions