from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog


class QuickToolItemPickerDialog(QDialog):
    sigOnNewItem = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget)

        self.tabWidget.addTab(self.createTab(self.onAddAction, DataConstraints.StrMod.ActionSelection), "Action")
        self.tabWidget.addTab(self.createTab(self.onAddTool, DataConstraints.StrMod.ToolSelection), "Tool")

    def createTab(self, onAccept: any, mode: DataConstraints.StrMod):
        dlg = PropertyGrid_SelectorDialog(None)
        dlg.header_buttons.buttons()[0].setText("Insert")
        dlg.header_buttons.buttons()[1].setText("Cancel")
        dlg.header_buttons.accepted.connect(lambda: onAccept(dlg))
        dlg.header_buttons.rejected.connect(self.onReject)
        dlg.load_list(mode)
        return dlg

    def onAddTool(self, source: PropertyGrid_SelectorDialog):
        self.sigOnNewItem.emit(source.selected_item)

    def onAddAction(self, source: PropertyGrid_SelectorDialog):
        self.sigOnNewItem.emit(source.selected_item)

    def onReject(self):
        self.reject()

