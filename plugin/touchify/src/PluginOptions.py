
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from jemlib.alib_propertygrid.data.DataHandler import DataHandler
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid
from jemlib.managers.GlobalEvents import GlobalEvents
from touchify.src.alib_propertygrid.data.TouchifyDataHandler import TouchifyDataHandler
from touchify.src.settings.TouchifySettings import TouchifySettings
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions

from krita import *

class PluginOptions(QDialog):


    @staticmethod
    def Setup(dlg: "PluginOptions", api_window: WindowAPI):
        if dlg != None:
            if PyQtExtensions.CommonHelpers.isDeleted(dlg) == False:
                dlg.close()
                dlg = None
        
        dlg = PluginOptions(api_window)
        return dlg

    def __init__(self, qwin: WindowAPI):
        super().__init__(qwin.qwindow.window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow
        
        self.editableConfig = TouchifySettings.configCopy()

        self.praser = DataHandler()
        self.praser.installExtension(TouchifyDataHandler())

        self.propertyGrid = PropertyGrid(self, self.praser)
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
        self.editableConfig.save()
        TouchifySettings.load()
        GlobalEvents().SIGNAL_TOUCHIFY_CONFIG_UPDATED.emit()

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

