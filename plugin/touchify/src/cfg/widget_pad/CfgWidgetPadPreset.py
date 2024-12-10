from touchify.src.cfg.widget_pad.CfgWidgetPadOptions import CfgWidgetPadOptions
from touchify.src.cfg.widget_pad.CfgWidgetPadToolboxOptions import CfgWidgetPadToolboxOptions
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
   
class CfgWidgetPadPreset:
    preset_name: str = "WidgetPad Preset"

    toolbox: CfgWidgetPadToolboxOptions = CfgWidgetPadToolboxOptions()
    toolshelf_alt: CfgWidgetPadOptions = CfgWidgetPadOptions()
    toolshelf: CfgWidgetPadOptions = CfgWidgetPadOptions()

    json_version: int = 1

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args, [CfgWidgetPadOptions, CfgWidgetPadToolboxOptions])

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


