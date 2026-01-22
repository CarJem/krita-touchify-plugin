from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify_quick_actions.widgets.DraggableGridWidgetHeader import DraggableGridWidgetHeader
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify_quick_actions.widgets.DraggableGridContainer import DraggableGridContainer
from touchify_quick_actions.widgets.DraggableGridWidget import DraggableGridWidget
from touchify_quick_actions.widgets.DraggableGridWidgetHeader import DraggableGridWidgetHeaderToggle

class SourceGridComponents:
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