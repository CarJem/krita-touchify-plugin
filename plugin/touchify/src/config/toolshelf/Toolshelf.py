
from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.extensions.file_extensions import FileExtensions
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions



   
class Toolshelf:
    def __defaults__(self):
        self.preset_name: str = "New Toolshelf Preset"
        self.preset_group: str = ""
        self.preset_data: ToolshelfContainer = ToolshelfContainer()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfContainer])

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        actual_name = self.preset_name.replace("\n", "\\n")
        if self.preset_group != "":
            return f"[{self.preset_group}] {actual_name}"
        else:
            return actual_name

    def forceLoad(self):
        pass

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "preset_group",
            "preset_data"
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row
    
    def propertygrid_view_type(self):
        return "tabs_vertical"

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["preset_group"] = "Preset Group"
        labels["preset_data"] = "Preset Data"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["preset_data"] = PropertyGrid_Restrictions.expandable()
        return restrictions


