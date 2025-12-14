from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions

class ToolshelfPageSettings:
    def __defaults__(self):
        self.page_icon: str = "material:home"

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args)
    
    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["page_icon"] = "Page Icon"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["page_icon"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.IconSelection)
        return restrictions