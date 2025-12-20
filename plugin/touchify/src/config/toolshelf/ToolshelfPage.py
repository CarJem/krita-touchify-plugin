from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
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

    def propertygrid_labels(self):
        labels = {}
        labels["items"] = "Items"
        labels["options"] = "Page Options"
        return labels

    def propertygrid_hidden(self):
        return [
            "layout"
        ]
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["options"] = DataConstraints.expandable()
        return restrictions