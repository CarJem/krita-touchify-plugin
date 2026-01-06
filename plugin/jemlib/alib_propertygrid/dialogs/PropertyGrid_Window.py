
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

    APPLY_COUNT: int = 0
    CLOSE_COUNT: int = 0
    SAVE_COUNT: int = 0
    DELETE_COUNT: int = 0
    CREATE_COUNT: int = 0
    SHOW_COUNT: int = 0


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
                PropertyGrid_Window.DELETE_COUNT += 1
                Logger.logDebug("JemLib", "PropertyGrid_Window", "Setup", f"Global Delete Count: {PropertyGrid_Window.DELETE_COUNT}")
                dlg.close()
                #dlg.deleteLater()
                dlg = None

        if not cls:
            cls = PropertyGrid_Window
        
        PropertyGrid_Window.CREATE_COUNT += 1
        Logger.logDebug("JemLib", "PropertyGrid_Window", "Setup", f"Global Create Count: {PropertyGrid_Window.CREATE_COUNT}")
        dlg = cls(parent, options, prasers, buttons)
        Logger.logDebug("JemLib", "PropertyGrid_Window", "Setup", f"Dialog Created")
        return dlg

    def __init__(self, qwin: QWidget, options: Any, prasers: DataHandler = None, buttons: list[QDialogButtonBox.StandardButton] = None):
        super().__init__(qwin)
        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"Subclass Init")

        if prasers:
            self.praser = prasers
        else:
            self.praser = DataHandler()

        self.__is_exec = False
        self.__dialogFullyLoaded = False

        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"Data Handler: Created")
        
        self.container = QGridLayout(self)
        self.container.setContentsMargins(0,0,0,0)
        self.container.setSpacing(0)
        self.setLayout(self.container)     
        
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"Layout Settings: Applied")

        self.btns = QDialogButtonBox(self)
        self.btns.setContentsMargins(5,5,5,5)
        if not buttons: buttons = PropertyGrid_Window.StandardButtons()

        if QDialogButtonBox.StandardButton.Apply in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._onApply)

        if QDialogButtonBox.StandardButton.Save in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self._onSave)

        if QDialogButtonBox.StandardButton.Close in buttons: 
            self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self._onClose)            

        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"Dialog Btns: Created")

        self.onObjectSave: Callable[[any], None] = None
        self.onWindowDeleted: Callable[[], None] = None

        self.data_object = PropertySystem.deepcopy(options)
        self.propertyGrid = PropertyGrid(self, self.praser)
        self.propertyGrid.setDataObject(self.data_object)

        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"PropertyGrid: Created")

        self.container.addWidget(self.propertyGrid, 0, 0)
        self.container.addWidget(self.btns, 1, 0)
        Logger.logDebug("JemLib", "PropertyGrid_Window", "__init__", f"Init Finished")

        self.__dialogFullyLoaded = True

    def show(self):
        PropertyGrid_Window.SHOW_COUNT += 1
        Logger.logDebug("JemLib", "PropertyGrid_Window", "Setup", f"Global Show Count: {PropertyGrid_Window.SHOW_COUNT}")
        return super().show()

    def close(self):
        if not self.__dialogFullyLoaded:
            return False
        
        response = super().close()
        if response:
            PropertyGrid_Window.CLOSE_COUNT += 1
            Logger.logDebug("JemLib", "PropertyGrid_Window", "_onClose", f"Global Close Count: {PropertyGrid_Window.CLOSE_COUNT}")
            if self.onWindowDeleted: self.onWindowDeleted()
        return response

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
        PropertyGrid_Window.APPLY_COUNT += 1
        Logger.logDebug("JemLib", "PropertyGrid_Window", "_onApply", f"Global Apply Count: {PropertyGrid_Window.APPLY_COUNT}")
        if self.onObjectSave: self.onObjectSave(self.data_object)

    def _onSave(self):
        PropertyGrid_Window.SAVE_COUNT += 1
        Logger.logDebug("JemLib", "PropertyGrid_Window", "_onSave", f"Global Save Count: {PropertyGrid_Window.SAVE_COUNT}")
        if not self.__is_exec:
            if self.onObjectSave: self.onObjectSave(self.data_object)
            self.accept()
        else:
            self.accept()

    def _onClose(self):
        self.reject()

