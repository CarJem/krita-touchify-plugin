
from typing import Any, Callable
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.PropertySystem import PropertySystem
from jemlib.alib_propertygrid.data.DataHandler import DataHandler
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.alib_vaporjem import Logger
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions

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
                dlg.deleteLater()
                dlg = None

        if not cls:
            cls = PropertyGrid_Window
    
        dlg = cls(parent, options, prasers, buttons)
        Logger.logDebug("JemLib", "PropertyGrid_Window", "Setup", f"Dialog Created")
        return dlg

    def __init__(self, qwin: QWidget, options: Any, prasers: DataHandler = None, buttons: list[QDialogButtonBox.StandardButton] = None):
        super().__init__(qwin)

        if prasers:
            self.praser = prasers
        else:
            self.praser = DataHandler()

        self.__is_exec = False
        self.__dialogFullyLoaded = False
        
        self.container = QGridLayout(self)
        self.container.setContentsMargins(0,0,0,0)
        self.container.setSpacing(0)
        self.setLayout(self.container)     
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
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

        self.onObjectSave: Callable[[any], None] = None
        self.onWindowDeleted: Callable[[], None] = None

        self.data_object = PropertySystem.deepcopy(options)
        self.propertyGrid = PropertyGrid(self, self.praser)
        self.propertyGrid.setDataObject(self.data_object)

        self.container.addWidget(self.propertyGrid, 0, 0)
        self.container.addWidget(self.btns, 1, 0)

        self.__dialogFullyLoaded = True

    def show(self):
        return super().show()

    def close(self):
        response = super().close()
        if response:
            if self.onWindowDeleted: self.onWindowDeleted()
        return response
    
    def closeEvent(self, a0):
        if not self.__dialogFullyLoaded:
            a0.ignore()
        a0.accept()

    def exec(self):
        self.__is_exec = True
        response = super().exec()
        self.__is_exec = False
        if response:
            return self.data_object
        return response
    
    def exec_(self):
        self.__is_exec = True
        response = super().exec_()
        self.__is_exec = False
        if response:
            return self.data_object
        return response

    def _onApply(self):
        if self.onObjectSave: self.onObjectSave(self.data_object)

    def _onSave(self):
        if not self.__is_exec:
            if self.onObjectSave: self.onObjectSave(self.data_object)
            self.accept()
        else:
            self.accept()

    def _onClose(self):
        self.reject()

