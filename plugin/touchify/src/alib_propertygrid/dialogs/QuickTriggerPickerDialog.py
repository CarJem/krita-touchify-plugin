from copy import deepcopy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.data.DataHandler import DataHandler
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog

from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.menu.TriggerMenuItem import TriggerMenuItem

class QuickTriggerPickerDialog(QDialog):
    sigOnNewItem = pyqtSignal(Trigger)
    
    class TriggerTab(QDialog):
        def __init__(self, parent: "QuickTriggerPickerDialog", menuMode=False):
            super().__init__(parent)
            self.pickerParent = parent

            from touchify.src.alib_propertygrid.data.TouchifyDataHandler import TouchifyDataHandler
            self.praser = DataHandler()
            self.praser.installExtension(TouchifyDataHandler())

            self.propertyGrid = PropertyGrid(self, self.praser)
            if menuMode:
                self.propertyGrid.setDataObject(TriggerMenuItem())
            else:
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

    def __init__(self, parent: QWidget, menuMode=False):
        super().__init__(parent)
        self.__menuMode = menuMode

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        self.tabWidget = QTabWidget(self)
        self.layout().addWidget(self.tabWidget)

        if self.__menuMode:
            self.tabWidget.addTab(self.createTab(self.onAddAction, DataConstraints.StrMod.ActionSelection), "Action")
            self.tabWidget.addTab(QuickTriggerPickerDialog.TriggerTab(self, menuMode), "Custom")
        else:
            self.tabWidget.addTab(self.createTab(self.onAddAction, DataConstraints.StrMod.ActionSelection), "Action")
            self.tabWidget.addTab(self.createTab(self.onAddBrush, DataConstraints.StrMod.BrushSelection), "Brush")
            self.tabWidget.addTab(QuickTriggerPickerDialog.TriggerTab(self, menuMode), "Custom")

    def createTab(self, onAccept: any, mode: DataConstraints.StrMod):
        dlg = PropertyGrid_SelectorDialog(None)
        dlg.header_buttons.buttons()[0].setText("Insert")
        dlg.header_buttons.buttons()[1].setText("Cancel")
        dlg.header_buttons.accepted.connect(lambda: onAccept(dlg))
        dlg.header_buttons.rejected.connect(self.onReject)
        dlg.load_list(mode)
        return dlg

    def onAddBrush(self, source: PropertyGrid_SelectorDialog):
        if self.__menuMode == False:   
            trigger = Trigger()
            trigger.variant = str(Trigger.Variants.Brush)
            trigger.display_custom_text_enabled = False
            trigger.brush_name = source.selected_item
            self.sigOnNewItem.emit(deepcopy(trigger))

    def onAddAction(self, source: PropertyGrid_SelectorDialog):
        if self.__menuMode == False:
            trigger = Trigger()
            trigger.variant = str(Trigger.Variants.Action)
        else:
            trigger = TriggerMenuItem()
            trigger.variant = str(TriggerMenuItem.Variants.Action)

        trigger.display_custom_text_enabled = False
        trigger.action_id = source.selected_item
        self.sigOnNewItem.emit(deepcopy(trigger))

    def onAddTrigger(self, source: Trigger | TriggerMenuItem):
        self.sigOnNewItem.emit(deepcopy(source))

    def onReject(self):
        self.reject()

