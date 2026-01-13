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
        dlg = None
        dlg = PropertyGrid_SelectorDialog.Setup(dlg, None, "", { 'button_names': [ "Insert", "Cancel" ], 'close_on_save': False })
        dlg.onAcceptFunction = onAccept
        dlg.onRejectFunction = self.onReject
        dlg.load_list(mode)
        return dlg

    def onAddTool(self, source: str):
        self.sigOnNewItem.emit(source)

    def onAddAction(self, source: str):
        self.sigOnNewItem.emit(source)

    def onReject(self):
        self.reject()

