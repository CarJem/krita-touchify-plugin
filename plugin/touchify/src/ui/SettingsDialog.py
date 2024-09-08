
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
from ..components.touchify.property_grid.PropertyGrid import PropertyGrid
from ..settings.TouchifyConfig import *
from ..resources import *
from ..ext.extensions import *
from ..components.touchify.property_grid.PropertyGrid_Panel import *
from ...paths import BASE_DIR

from krita import *


NOTICE_MESSAGE = """

"""

class SettingsDialog(QDialog):

    def __init__(self, qwin: Window):
        super().__init__(qwin.qwindow().window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow()
        self.editableConfig = copy.copy(TouchifyConfig.instance().getConfig())


        self.propertyGrid = PropertyGrid()
        self.propertyGrid.updateDataObject(self.editableConfig)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)
        self.btns = self.createButtons()
        self.container.addWidget(self.propertyGrid)
        self.container.addWidget(self.btns)
        self.setLayout(self.container)     

    def createButtons(self):
        buttonBox = QDialogButtonBox(self)
        buttonBox.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.onSave)
        buttonBox.addButton(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.onApply)
        buttonBox.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self.onClose)
        return buttonBox
    
    def _saveFile(self):
        self.editableConfig.save()
        TouchifyConfig.instance().notifyUpdate()
        self.propertyGrid.forceUpdate()

    def onSave(self):
        self._saveFile()
        self.accept()

    def onApply(self):
        self._saveFile()

    def onClose(self):
        self.close()
        self.reject()

