from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

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
        restrictions["page_icon"] = DataConstraints.strMod(DataConstraints.StrMod.IconSelection)
        return restrictions