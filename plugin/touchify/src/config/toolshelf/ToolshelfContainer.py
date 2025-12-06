
from typing import Any
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.datatypes.sequence.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions


   
class ToolshelfContainer:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDock] = {}
        self.pages: TypedList[ToolshelfSubState] = []
        self.options: ToolshelfSettings = ToolshelfSettings()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDock, ToolshelfSettings, ToolshelfSubState])
        try:
            self.pages = JsonExtensions.init_list(args, "pages", ToolshelfSubState)
        except:
            pass

        for entry in self.items:
            self.items[entry] = ToolshelfDock(**self.items[entry])

    def forceLoad(self):
        self.pages = TypedList(self.pages, ToolshelfSubState)

class ToolshelfSubState:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDock] = {}
        self.name: str = ""
    
    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDock])

        for entry in self.items:
            self.items[entry] = ToolshelfDock(**self.items[entry])




    