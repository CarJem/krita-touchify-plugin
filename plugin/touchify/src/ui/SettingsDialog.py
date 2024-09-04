
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


    def getNoticeMessage(self):
        filePath = os.path.join(BASE_DIR, 'src', 'data', 'settings_message.txt')
        result = ""
        with open(filePath) as f:
            result = f.read()
        return result

    def __init__(self, qwin: Window):
        super().__init__(qwin.qwindow())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow()
        self.editableConfig = TouchifyConfig.instance().copyConfig()
        self.gridLayout = QGridLayout()

        self.notice = QLabel()
        self.notice.setWordWrap(True)
        self.notice.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notice.setText(self.getNoticeMessage())
        self.notice.setMinimumWidth(150)
        self.notice.setStyleSheet('''font-size: 10px''')

        self.propertyGrid = PropertyGrid()
        self.propertyGrid.updateDataObject(self.editableConfig)
        self.gridLayout.addWidget(self.propertyGrid, 0, 0)



        self.gridLayout.addWidget(self.notice, 0, 1)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)
        self.btns = self.createButtons()
        self.container.addLayout(self.gridLayout)
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

