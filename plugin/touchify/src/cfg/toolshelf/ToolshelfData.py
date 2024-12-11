
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.cfg.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions
from touchify.src.cfg.toolshelf.ToolshelfDataPage import ToolshelfDataPage
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions



   
class ToolshelfData:
    def __defaults__(self):
        self.pages: TypedList[ToolshelfDataPage] = []
        self.homepage: ToolshelfDataPage = ToolshelfDataPage() 
        self.header_options: ToolshelfDataOptions = ToolshelfDataOptions()
        self.preset_name: str = "New Toolshelf Preset"

        self.json_version: int = 3

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfData(args)
        Extensions.dictToObject(self, args, [ToolshelfDataOptions, ToolshelfDataPage])
        self.pages = Extensions.init_list(args, "pages", ToolshelfDataPage)

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        self.pages = TypedList(self.pages, ToolshelfDataPage)

    def propertygrid_sorted(self):
        return [
            "metadata",
            "header_options",
            "pages_group",
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["metadata"] = {"items": ["preset_name"], "is_group": True}
        row["pages_group"] = {"items": ["homepage", "pages"], "is_group": True}
        return row
    
    def propertygrid_view_type(self):
        return "tabs_vertical"

    def propertygrid_labels(self):
        labels = {}
        labels["metadata"] = "Metadata"
        labels["preset_name"] = "Preset Name"

        labels["header_options"] = "Options"
        
        labels["pages_group"] = "Pages"
        labels["homepage"] = "Home Page"
        labels["pages"] = "Other Pages"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["homepage"] = {"type": "expandable"}
        restrictions["header_options"] = {"type": "expandable"}
        return restrictions


