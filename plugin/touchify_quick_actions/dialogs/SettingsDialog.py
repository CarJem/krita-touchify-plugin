
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions

from krita import *
from touchify_quick_actions.utils.data_manager import load_common_config, save_common_config

class SettingsDialog(QDialog):


    @staticmethod
    def Setup(dlg: "SettingsDialog", api_window: WindowAPI):
        if dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.close()
                dlg = None
        
        dlg = SettingsDialog(api_window)
        return dlg

    def __init__(self, qwin: WindowAPI):
        super().__init__(qwin.qwindow.window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow
        self.setWindowTitle("Preset Groups")
        self.resize(325, 420)
        
        self.editableConfig = load_common_config()
        self.propertyGrid = PropertyGrid(self)
        self.propertyGrid.setDataObject(self.editableConfig)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        self.btns = QDialogButtonBox(self)
        self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.onSave)
        self.btns.addButton(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.onApply)
        self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self.onClose)

        self.container.addWidget(self.propertyGrid)
        self.container.addWidget(self.btns)
        self.setLayout(self.container)     
    
    def _saveFile(self):
        save_common_config(self.editableConfig)

    def onSave(self):
        self._saveFile()
        self.accept()

    def onApply(self):
        self.btns.setEnabled(False)
        QTimer.singleShot(5000, lambda: self.btns.setDisabled(False))

        self._saveFile()

    def onClose(self):
        self.close()
        self.reject()

