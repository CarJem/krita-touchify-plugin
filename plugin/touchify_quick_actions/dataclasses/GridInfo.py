from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify_quick_actions.widgets.DraggableGridRow import DraggableGridRow
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify_quick_actions.widgets.DraggableGridContainer import DraggableGridContainer
from touchify_quick_actions.widgets.ClickableGridWidget import ClickableGridWidget
from .GridPresetItem import GridPresetItem

class GridInfo:

    def __init__(self, **args):
        self.brush_presets: list["GridPresetItem"] = []
        self.is_collapsed: bool = False
        self.name: str = ""
        self.is_active: bool = False

        JsonExtensions.dictToObject(self, args, [GridPresetItem])
        self.brush_presets = JsonExtensions.init_list(args, "brush_presets", GridPresetItem)

        self.container: DraggableGridContainer = None
        self.name_label: QPushButton = None
        self.collapse_button: QPushButton = None
        self.name_button: QPushButton = None
        self.header_layout: QLayout = None
        self.header_row: DraggableGridRow = None
        self.widget: ClickableGridWidget = None
        self.layout: QGridLayout = None
        self.name_editor: QLineEdit = None

    @staticmethod
    def createEmpty(name: str):
        """Create an empty grid info dictionary."""
        return GridInfo(
            container=None,
            widget=None,
            layout=None,
            name_label=None,
            rename_button=None,
            name=name,
            brush_presets=[],
            is_active=False,
            name_editor=None
        )