
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat
from touchify.src.cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from touchify.src.cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions



   
class CfgToolshelf:
    def __defaults__(self):
        self.pages: TypedList[CfgToolshelfPanel] = []
        self.homepage: CfgToolshelfPanel = CfgToolshelfPanel() 
        self.header_options: CfgToolshelfHeaderOptions = CfgToolshelfHeaderOptions()
        self.preset_name: str = "New Toolshelf Preset"

        self.json_version: int = 3

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = CfgBackwardsCompat.CfgToolshelf(args)
        Extensions.dictToObject(self, args, [CfgToolshelfHeaderOptions, CfgToolshelfPanel])
        self.pages = Extensions.init_list(args, "pages", CfgToolshelfPanel)

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        self.pages = TypedList(self.pages, CfgToolshelfPanel)

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "header_options",
            "homepage",
            "pages"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["homepage"] = "Home Page"
        labels["pages"] = "Pages"
        labels["header_options"] = "Header Options"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["tab_type"] = {"type": "values", "entries": ["buttons", "tabs"]}
        restrictions["homepage"] = {"type": "expandable"}
        restrictions["header_options"] = {"type": "expandable"}
        return restrictions


