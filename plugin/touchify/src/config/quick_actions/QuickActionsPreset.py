from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS


class QuickActionsPreset:
    def __defaults__(self):
        from touchify_quick_actions.dataclasses.GridConfig import GridConfig
        self.registry_name: str = "New Preset Group"
        self.preset_data: GridConfig = GridConfig()

    def __init__(self, **args) -> None:
        from touchify_quick_actions.dataclasses.GridConfig import GridConfig
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [GridConfig])

    def __str__(self):
        return self.registry_name

    def getFileName(self):
        return FileExtensions.fileStringify(self.registry_name)

    def propertygrid_sorted(self):
        return [
            "registry_name",
            "preset_data"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["registry_name"] = "Registry Name"
        labels["preset_data"] = "Configuration"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["preset_data"] = RS.expandable()
        return restrictions