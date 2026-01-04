
from typing import Any, Callable
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.data.DataHandler import DataHandler
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions
import copy

from krita import *

class PropertyGrid_Window(QDialog):

    @staticmethod
    def StandardButtons():
        return [
            QDialogButtonBox.StandardButton.Save,
            QDialogButtonBox.StandardButton.Close
        ]

    @staticmethod
    def Setup(dlg: "PropertyGrid_Window", parent: QWidget, options: any, prasers: DataHandler = None, buttons: list[QDialogButtonBox.StandardButton] = None, cls: "type[PropertyGrid_Window]" = None):
        if dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.close()
                dlg = None

        if not cls:
            cls = PropertyGrid_Window
        
        dlg = cls(parent, options, prasers, buttons)
        return dlg

    def __init__(self, qwin: QWidget, options: Any, prasers: DataHandler = None, buttons: list[QDialogButtonBox.StandardButton] = None):
        super().__init__(qwin)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

        if prasers:
            self.praser = prasers
        else:
            self.praser = DataHandler()
        
        self.container = QGridLayout(self)
        self.container.setContentsMargins(0,0,0,0)
        self.container.setSpacing(0)
        self.setLayout(self.container)     
        
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        self.btns = QDialogButtonBox(self)
        self.btns.setContentsMargins(5,5,5,5)
        if not buttons: buttons = PropertyGrid_Window.StandardButtons()

        if QDialogButtonBox.StandardButton.Apply in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._onApply)

        if QDialogButtonBox.StandardButton.Save in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self._onSave)

        if QDialogButtonBox.StandardButton.Close in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self._onClose)            


        self.onApply: Callable[[PropertyGrid_Window], None] = None
        self.onSave: Callable[[PropertyGrid_Window], None] = None
        self.onClose: Callable[[PropertyGrid_Window], None] = None


        self.editableConfig = copy.deepcopy(options)
        self.propertyGrid = PropertyGrid(self, self.praser)
        self.propertyGrid.setDataObject(self.editableConfig)

        self.container.addWidget(self.propertyGrid, 0, 0)
        self.container.addWidget(self.btns, 1, 0)
        

    def _onApply(self):
        if self.onApply: self.onApply(self)

    def _onSave(self):
        if self.onApply: self.onSave(self)
        self.accept()

    def _onClose(self):
        if self.onApply: self.onClose(self)
        self.reject()

