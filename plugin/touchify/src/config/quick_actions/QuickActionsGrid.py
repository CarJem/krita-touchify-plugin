from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify_quick_actions.dataclasses.SourceGridComponents import SourceGridComponents
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .QuickActionsItem import QuickActionsItem
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class QuickActionsGrid:

    class Layout:
        def __init__(self, **args) -> None:
            self.override_global_style = False

            self.max_brush_per_row = 8
            self.spacing_between_buttons = 1
            self.brush_icon_size = 65
            self.list_mode = False
            self.list_column_count = 1
            self.display_brush_names = True
            
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_labels(self):
            labels = {}
            labels["max_brush_per_row"] = "Max buttons per row"
            labels["spacing_between_buttons"] = "Spacing between buttons"
            labels["brush_icon_size"] = "Button icon size"
            labels["list_mode"] = "List mode"
            labels["list_column_count"] = "Number of list columns"
            labels["display_brush_names"] = "Display brush names"
            return labels
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["max_brush_per_row"] = RS.range(min=1)
            restrictions["spacing_between_buttons"] = RS.range(min=0)
            restrictions["brush_icon_size"] = RS.range(min=4)
            restrictions["list_column_count"] = RS.range(min=1)
            return restrictions

        def propertygrid_view_type(self):
            return "form_alt"
    
    def __init__(self, **args):
        self.name: str = ""
        self.is_collapsed: bool = False
        self.is_active: bool = False
        self.layout = QuickActionsGrid.Layout()
        self.brush_presets: list["QuickActionsItem"] = []
        
        JsonExtensions.dictToObject(self, args, [QuickActionsItem, QuickActionsGrid.Layout])
        self.brush_presets = JsonExtensions.init_list(args, "brush_presets", QuickActionsItem)

        self.ui = SourceGridComponents()

    def propertygrid_view_type(self):
        return "sections"
    
    def dump(self):
        result = QuickActionsGrid()
        result.brush_presets = self.brush_presets
        result.name = self.name
        result.is_collapsed = self.is_collapsed
        result.is_active = self.is_active
        result.layout = self.layout
        result.ui = None
        return result

    @staticmethod
    def createEmpty(name: str):
        """Create an empty grid info dictionary."""
        result = QuickActionsGrid()
        result.name = name
        return result