from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify_quick_actions.widgets.DraggableGridWidgetHeader import DraggableGridWidgetHeader
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify_quick_actions.widgets.DraggableGridContainer import DraggableGridContainer
from touchify_quick_actions.widgets.DraggableGridWidget import DraggableGridWidget
from touchify_quick_actions.widgets.DraggableGridWidgetHeader import DraggableGridWidgetHeaderToggle
from .GridPresetItem import GridPresetItem
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class GridInfo:

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
        
    class Internal:
        def __init__(self, **args) -> None:
            JsonExtensions.dictToObject(self, args, [])

            self.container: DraggableGridContainer = None
            self.name_label: QPushButton = None
            self.collapse_button: DraggableGridWidgetHeaderToggle = None
            self.name_button: QPushButton = None
            self.header_layout: QLayout = None
            self.header_row: DraggableGridWidgetHeader = None
            self.widget: DraggableGridWidget = None
            self.layout: QGridLayout = None
            self.name_editor: QLineEdit = None

    def __init__(self, **args):
        self.brush_presets: list["GridPresetItem"] = []
        self.name: str = ""
        self.is_collapsed: bool = False
        self.is_active: bool = False
        self.layout = GridInfo.Layout()
        
        JsonExtensions.dictToObject(self, args, [GridPresetItem, GridInfo.Layout])
        self.brush_presets = JsonExtensions.init_list(args, "brush_presets", GridPresetItem)

        self.ui = GridInfo.Internal()

    def propertygrid_view_type(self):
        return "sections"

    @staticmethod
    def createEmpty(name: str):
        """Create an empty grid info dictionary."""
        result = GridInfo()
        result.name = name
        return result