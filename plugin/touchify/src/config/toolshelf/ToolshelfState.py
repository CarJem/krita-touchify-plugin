
from typing import Any
from touchify.src.config.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions
from touchify.src.config.toolshelf.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.datatypes.sequence.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions


   
class ToolshelfState:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDataSection] = {}
        self.pages: TypedList[ToolshelfSubState] = []
        self.options: ToolshelfDataOptions = ToolshelfDataOptions()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDataSection, ToolshelfDataOptions, ToolshelfSubState])
        try:
            self.pages = JsonExtensions.init_list(args, "pages", ToolshelfSubState)
        except:
            pass

        for entry in self.items:
            self.items[entry] = ToolshelfDataSection(**self.items[entry])

    def forceLoad(self):
        self.pages = TypedList(self.pages, ToolshelfSubState)

class ToolshelfSubState:
    def __defaults__(self):
        self.layout: dict[str, Any] = {}
        self.items: dict[str, ToolshelfDataSection] = {}
        self.name: str = ""
    
    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfDataSection])

        for entry in self.items:
            self.items[entry] = ToolshelfDataSection(**self.items[entry])




    