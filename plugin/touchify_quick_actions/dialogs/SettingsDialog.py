
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions

from krita import *
from touchify_quick_actions.utils.config_utils import save_common_config

class SettingsDialog(QDialog):


    @staticmethod
    def Setup(dlg: "SettingsDialog", api_window: WindowAPI, title: str, input: any):
        if dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.close()
                dlg = None
        
        dlg = SettingsDialog(api_window, title, input)
        return dlg

    def __init__(self, qwin: WindowAPI, title: str, input: any):
        super().__init__(qwin.qwindow.window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow
        self.setWindowTitle(title)
        self.resize(325, 420)
        
        self.editableConfig = input
        self.propertyGrid = PropertyGrid(self)
        self.propertyGrid.setDataObject(self.editableConfig)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        self.btns = QDialogButtonBox(self)
        self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.onSave)
        self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self.onClose)

        self.container.addWidget(self.propertyGrid)
        self.container.addWidget(self.btns)
        self.setLayout(self.container)     
    
    def _saveFile(self):
        save_common_config(self.editableConfig)

    def onSave(self):
        self._saveFile()
        self.accept()

    def onClose(self):
        self.close()
        self.reject()

