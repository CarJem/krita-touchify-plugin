from typing import TYPE_CHECKING
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



if TYPE_CHECKING:
    from touchify.src.config.quick_actions.QuickActionsPage import QuickActionsPage
    from .QuickActionsGrid import QuickActionsGrid



class QuickActionsPreset:
    def __defaults__(self):
        from touchify.src.config.quick_actions.QuickActionsPage import QuickActionsPage
        from touchify.src.config.quick_actions.QuickActionsPresetConfig import QuickActionsPresetConfig
        self.preset_name: str = "New Preset Group"
        self.preset_pages: list[QuickActionsPage] = []
        self.preset_selected_page: int = 0
        self.preset_settings: QuickActionsPresetConfig = QuickActionsPresetConfig()

    def __init__(self, **args) -> None:
        from touchify.src.config.quick_actions.QuickActionsPage import QuickActionsPage
        from touchify.src.config.quick_actions.QuickActionsPresetConfig import QuickActionsPresetConfig
        self.__defaults__()
        JsonExtensions.dictToObject(self, args, [QuickActionsPage, QuickActionsPresetConfig])
        self.preset_pages = JsonExtensions.init_list(args, "preset_pages", QuickActionsPage)

    def __str__(self):
        return self.preset_name
    
    #region PropertyGrid Stuff
    
    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "preset_pages",
            "preset_settings"
        ]
    
    def propertygrid_hidden(self):
        return [
            "preset_selected_page"
        ]
    
    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["preset_pages"] = "Pages"
        labels["preset_settings"] = "Settings"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["preset_settings"] = DataConstraints.expandable()
        return restrictions
    
    #endregion
 
    def load_page(self, index: int):
        if (0 <= index) and (index < len(self.preset_pages)):
            return self.preset_pages[index].restore(), index
        else:
            return [], index

    def save_page(self, index: int, data: "list[QuickActionsGrid]"):
        if (0 <= index) and (index < len(self.preset_pages)):
            self.preset_pages[index].grids = data
