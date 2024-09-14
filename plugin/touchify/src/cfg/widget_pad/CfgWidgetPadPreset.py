import string
from .CfgWidgetPadOptions import CfgWidgetPadOptions
from .CfgWidgetPadToolboxOptions import CfgWidgetPadToolboxOptions
from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
   
class CfgWidgetPadPreset:
    preset_name: str = "WidgetPad Preset"

    toolbox: CfgWidgetPadToolboxOptions = CfgWidgetPadToolboxOptions()
    toolshelf_alt: CfgWidgetPadOptions = CfgWidgetPadOptions()
    toolshelf: CfgWidgetPadOptions = CfgWidgetPadOptions()

    

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args, [CfgWidgetPadOptions, CfgWidgetPadToolboxOptions])

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.preset_name if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

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


