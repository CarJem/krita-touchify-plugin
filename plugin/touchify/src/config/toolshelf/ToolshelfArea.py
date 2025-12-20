
from typing import Any
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
from touchify.src.config.toolshelf.ToolshelfAreaSettings import ToolshelfAreaSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfPage import ToolshelfPage
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions


   
class ToolshelfArea:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDock] = {}
        self.pages: TypedList[ToolshelfPage] = []
        self.options: ToolshelfAreaSettings = ToolshelfAreaSettings()
        self.pageOptions: ToolshelfPageSettings = ToolshelfPageSettings()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDock, ToolshelfAreaSettings, ToolshelfPage, ToolshelfPageSettings])
        self.pages = JsonExtensions.init_list(args, "pages", ToolshelfPage)

        for entry in self.items:
            self.items[entry] = ToolshelfDock(**self.items[entry])

    def forceLoad(self):
        self.pages = TypedList(self.pages, ToolshelfPage)

    def propertygrid_labels(self):
        labels = {}
        labels["items"] = "Items"
        labels["pages"] = "Pages"
        labels["options"] = "Options"
        labels["pageOptions"] = "Homepage Options"
        return labels

    def propertygrid_hidden(self):
        return [
            "layout"
        ]

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["items"] = DataConstraints.dictMod(DataConstraints.DictMod.ListLike)
        restrictions["options"] = DataConstraints.expandable()
        restrictions["pageOptions"] = DataConstraints.expandable()
        return restrictions





    