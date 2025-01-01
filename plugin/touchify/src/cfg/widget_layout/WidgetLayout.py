from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.cfg.widget_layout.WidgetLayoutPadOptions import WidgetLayoutPadOptions
from touchify.src.cfg.widget_layout.WidgetLayoutToolboxOptions import WidgetLayoutToolboxOptions
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
   
class WidgetLayout:

    def __defaults__(self):
        self.preset_name: str = "WidgetPad Preset"

        self.toolbox_enabled: bool = True
        self.toolshelf_count: int = 2

        self.toolbox: WidgetLayoutToolboxOptions = WidgetLayoutToolboxOptions()
        self.toolshelf_alpha: WidgetLayoutPadOptions = WidgetLayoutPadOptions()
        self.toolshelf_beta: WidgetLayoutPadOptions = WidgetLayoutPadOptions()
        self.toolshelf_gamma: WidgetLayoutPadOptions = WidgetLayoutPadOptions()
        self.toolshelf_delta: WidgetLayoutPadOptions = WidgetLayoutPadOptions()

        self.json_version: int = 2

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.WidgetLayout(args)
        Extensions.dictToObject(self, args, [WidgetLayoutPadOptions, WidgetLayoutToolboxOptions])

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        pass

    def propertygrid_hidden(self):
        result = []
        if self.toolshelf_count < 4:
            result.append("toolshelf_delta")
        if self.toolshelf_count < 3:
            result.append("toolshelf_gamma")
        if self.toolshelf_count < 2:
            result.append("toolshelf_beta")
        if self.toolshelf_count < 1:
            result.append("toolshelf_alpha")
        if not self.toolbox_enabled:
            result.append("toolbox")
        return result

    def propertygrid_sorted(self):
        return [
            "#NEW_SECTION",

            "preset_name",
            "toolbox_enabled",
            "toolshelf_count",

            "#NEW_COLUMN",

            "toolbox",
            "toolshelf_alpha",
            "toolshelf_beta",
            "toolshelf_gamma",
            "toolshelf_delta"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["toolbox_enabled"] = "Enable Toolbox"
        labels["toolshelf_count"] = "Number of Toolshelves"
        labels["toolbox"] = "Toolbox"
        labels["toolshelf_alpha"] = "Toolshelf (Alpha)"
        labels["toolshelf_beta"]  = "Toolshelf (Beta)"
        labels["toolshelf_gamma"] = "Toolshelf (Gamma)"
        labels["toolshelf_delta"] = "Toolshelf (Delta)"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["toolbox"] = {"type": "expandable"}
        restrictions["toolshelf_count"] = {"type": "range", "min": 0, "max": 4}
        restrictions["toolshelf_alpha"] = {"type": "expandable"}
        restrictions["toolshelf_beta"]  = {"type": "expandable"}
        restrictions["toolshelf_gamma"] = {"type": "expandable"}
        restrictions["toolshelf_delta"] = {"type": "expandable"}
        return restrictions


