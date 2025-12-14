
from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
from touchify.src.extensions.file_extensions import FileExtensions
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions



   
class Toolshelf:
    def __defaults__(self):
        self.preset_name: str = "New Toolshelf Preset"
        self.preset_group: str = ""
        self.preset_data: ToolshelfArea = ToolshelfArea()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [ToolshelfArea])

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
    
    def propertygrid_hidden(self):
        return [
            "preset_data"
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["preset_group"] = "Preset Group"
        labels["preset_data"] = "Preset Data"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


