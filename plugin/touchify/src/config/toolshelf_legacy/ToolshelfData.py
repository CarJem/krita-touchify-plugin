
from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.config.toolshelf_legacy.ToolshelfDataOptions import ToolshelfDataOptions
from touchify.src.config.toolshelf_legacy.ToolshelfDataPage import ToolshelfDataPage
from touchify.src.extensions.file_extensions import FileExtensions
from touchify.src.datatypes.sequence.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions



   
class ToolshelfData:
    def __defaults__(self):
        self.pages: TypedList[ToolshelfDataPage] = []
        self.homepage: ToolshelfDataPage = ToolshelfDataPage() 
        self.header_options: ToolshelfDataOptions = ToolshelfDataOptions()
        self.preset_name: str = "New Toolshelf Preset"
        self.preset_group: str = ""

        self.json_version: int = 3

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfData(args)
        JsonExtensions.dictToObject(self, args, [ToolshelfDataOptions, ToolshelfDataPage])
        self.pages = JsonExtensions.init_list(args, "pages", ToolshelfDataPage)

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        actual_name = self.preset_name.replace("\n", "\\n")
        if self.preset_group != "":
            return f"[{self.preset_group}] {actual_name}"
        else:
            return actual_name

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
        row["metadata"] = {"items": ["preset_name", "preset_group"], "is_group": True}
        row["pages_group"] = {"items": ["homepage", "pages"], "is_group": True}
        return row
    
    def propertygrid_view_type(self):
        return "tabs_vertical"

    def propertygrid_labels(self):
        labels = {}
        labels["metadata"] = "Metadata"
        labels["preset_name"] = "Preset Name"
        labels["preset_group"] = "Preset Group"

        labels["header_options"] = "Options"
        
        labels["pages_group"] = "Pages"
        labels["homepage"] = "Home Page"
        labels["pages"] = "Other Pages"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["homepage"] = PropertyGrid_Restrictions.expandable()
        restrictions["header_options"] = PropertyGrid_Restrictions.expandable()
        return restrictions


