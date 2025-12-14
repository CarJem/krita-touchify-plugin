
from typing import Any
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfPage import ToolshelfPage
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.alib_datatypes.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions


   
class ToolshelfContainer:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDock] = {}
        self.pages: TypedList[ToolshelfPage] = []
        self.options: ToolshelfSettings = ToolshelfSettings()
        self.pageOptions: ToolshelfPageSettings = ToolshelfPageSettings()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDock, ToolshelfSettings, ToolshelfPage, ToolshelfPageSettings])
        self.pages = JsonExtensions.init_list(args, "pages", ToolshelfPage)

        for entry in self.items:
            self.items[entry] = ToolshelfDock(**self.items[entry])

    def forceLoad(self):
        self.pages = TypedList(self.pages, ToolshelfPage)





    