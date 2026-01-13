from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_propertygrid.PropertySystem import PropertySystem
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.data.DataHandler import DataHandler
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog

from touchify.src.config.triggers.Trigger import Trigger

class QuickTriggerPickerDialog(QDialog):
    sigOnNewItem = pyqtSignal(Trigger)
    
    class TriggerTab(QDialog):
        def __init__(self, parent: "QuickTriggerPickerDialog"):
            super().__init__(parent)
            self.pickerParent = parent

            from touchify.src.alib_propertygrid.data.TouchifyDataExtension import TouchifyDataExtension
            self.praser = DataHandler()
            self.praser.installExtension(TouchifyDataExtension())

            self.propertyGrid = PropertyGrid(self, self.praser)
            self.propertyGrid.setDataObject(Trigger())

            self.container = QVBoxLayout(self)
            self.setMinimumSize(600,400)
            self.setBaseSize(800,800)

            self.btns = QDialogButtonBox(self)

            insert = self.btns.addButton(QDialogButtonBox.StandardButton.Save)
            insert.setText("Insert")
            insert.clicked.connect(self.onInsert)

            cancel = self.btns.addButton(QDialogButtonBox.StandardButton.Cancel)
            cancel.setText("Cancel")
            cancel.clicked.connect(self.onCancel)

            self.container.addWidget(self.propertyGrid)
            self.container.addWidget(self.btns)
            self.setLayout(self.container)     

        def onInsert(self):
            self.pickerParent.onAddTrigger(self.propertyGrid.getDataObject())

        def onCancel(self):
            self.pickerParent.onReject()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget)

        self.tabWidget.addTab(self.createTab(self.onAddAction, DataConstraints.StrMod.ActionSelection), "Action")
        self.tabWidget.addTab(self.createTab(self.onAddBrush, DataConstraints.StrMod.BrushSelection), "Brush")
        self.tabWidget.addTab(QuickTriggerPickerDialog.TriggerTab(self), "Custom")

    def createTab(self, onAccept: any, mode: DataConstraints.StrMod):
        dlg = None
        dlg = PropertyGrid_SelectorDialog.Setup(dlg, None, "", { 'button_names': [ "Insert", "Cancel" ], 'close_on_save': False })
        dlg.onAcceptFunction = onAccept
        dlg.onRejectFunction = self.onReject
        dlg.load_list(mode)
        return dlg

    def onAddBrush(self, source: str):
        trigger = Trigger()
        trigger.variant = str(Trigger.Variants.Brush)
        trigger.display_custom_text_enabled = False
        trigger.brush_name = source
        self.sigOnNewItem.emit(trigger)

    def onAddAction(self, source: str):
        trigger = Trigger()
        trigger.variant = str(Trigger.Variants.Action)

        trigger.display_custom_text_enabled = False
        trigger.action_id = source
        self.sigOnNewItem.emit(trigger)

    def onAddTrigger(self, source: Trigger):
        self.sigOnNewItem.emit(PropertySystem.deepcopy(source))

    def onReject(self):
        self.reject()

