from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from touchify_toolshelves.src.config.ToolshelfDock import ToolshelfDock
from touchify_toolshelves.src.config.ToolshelfPageSettings import ToolshelfPageSettings
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions


from typing import Any


class ToolshelfPage:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDock] = {}
        self.options: ToolshelfPageSettings = ToolshelfPageSettings()
        self.name: str = ""

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDock, ToolshelfPageSettings])

        for entry in self.items:
            self.items[entry] = ToolshelfDock(**self.items[entry])
    
    def __str__(self):
        if self.name != "":
            return self.name
        else:
            return "(unnamed page)"

    def propertygrid_labels(self):
        labels = {}
        labels["name"] = "Name"
        labels["items"] = "Items"
        labels["options"] = "Page Options"
        return labels

    def propertygrid_hidden(self):
        return [
            "layout"
        ]
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["items"] = DataConstraints.dictMod(DataConstraints.DictMod.ListLike)
        restrictions["options"] = DataConstraints.expandable()
        return restrictions