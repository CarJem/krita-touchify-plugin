from touchify.src.cfg.widget_layout.WidgetLayoutPadOptions import WidgetLayoutPadOptions
from touchify.src.cfg.widget_layout.WidgetLayoutToolboxOptions import WidgetLayoutToolboxOptions
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
   
class WidgetLayout:

    def __defaults__(self):
        self.preset_name: str = "WidgetPad Preset"

        self.toolbox: WidgetLayoutToolboxOptions = WidgetLayoutToolboxOptions()
        self.toolshelf_alt: WidgetLayoutPadOptions = WidgetLayoutPadOptions()
        self.toolshelf: WidgetLayoutPadOptions = WidgetLayoutPadOptions()

        self.json_version: int = 1

    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args, [WidgetLayoutPadOptions, WidgetLayoutToolboxOptions])

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "toolbox",
            "toolbox_isHorizontal"
            "toolshelf",
            "toolshelf_alt"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["toolbox"] = "Toolbox"
        labels["toolbox_isHorizontal"] = "Horizontal Toolbox"
        labels["toolshelf"] = "Toolshelf"
        labels["toolshelf_alt"] = "Toolshelf (Alt.)"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["toolbox"] = {"type": "expandable"}
        restrictions["toolshelf_alt"] = {"type": "expandable"}
        restrictions["toolshelf"] = {"type": "expandable"}
        return restrictions


