
from typing import Any
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions
import copy

from krita import *

class PropertyGridDialog(QDialog):

    @staticmethod
    def Setup(dlg: "PropertyGridDialog", api_window: WindowAPI, options: any):
        if dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.close()
                dlg = None
        
        dlg = PropertyGridDialog(api_window, options)
        return dlg

    def __init__(self, qwin: WindowAPI, options: Any):
        super().__init__(qwin.qwindow.window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow
        
        self.editableConfig = copy.deepcopy(options)
        self.propertyGrid = PropertyGrid(self)
        self.propertyGrid.updateDataObject(self.editableConfig)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        self.btns = QDialogButtonBox(self)
        self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.onSave)
        self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self.onClose)

        self.container.addWidget(self.propertyGrid)
        self.container.addWidget(self.btns)
        self.setLayout(self.container)     

    def onSave(self):
        self.accept()

    def onClose(self):
        self.reject()

