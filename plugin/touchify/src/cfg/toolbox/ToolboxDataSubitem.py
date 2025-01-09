from touchify.src.components.python.json_extensions import JsonExtensions as Extensions
from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolboxDataSubitem:

    def __defaults__(self):
        self.name: str = ""
        self.icon: str = ""

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args)
    
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
        restrictions["name"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.Actions)
        restrictions["icon"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.Icon)
        return restrictions