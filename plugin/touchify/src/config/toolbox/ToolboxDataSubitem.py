from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class ToolboxDataSubitem:

    def __defaults__(self):
        self.name: str = ""
        self.icon: str = ""

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args)
    
    def __str__(self):
        return self.name.replace("\n", "\\n")
    
    def propertygrid_ismodel(self):
        return True
    

    def propertygrid_sorted(self):
        return [
            "name",
            "icon"
        ]
    
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