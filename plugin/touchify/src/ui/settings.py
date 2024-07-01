from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
import sys
import importlib.util
from ..components.propertygrid.PropertyGrid import PropertyGrid
from ..config import *
from ...resources import *
from ..ext.extensions import *
import xml.etree.ElementTree as ET
import re
import functools
import copy
import json
from ..components.propertygrid.PropertyGridPanel import *
import datetime


from krita import *


NOTICE_MESSAGE = """

"""

class SettingsDialog:


    def getNoticeMessage(self):
        filePath = os.path.join(os.path.dirname(__file__), 'notice_message.txt')
        result = ""
        with open(filePath) as f:
            result = f.read()
        return result

    def __init__(self, qwin: Window):
        self.qwin = qwin.qwindow()
        self.cfg = copy.deepcopy(ConfigManager.instance().cfg)

        self.dlg = QDialog(self.qwin)

        self.layout = QGridLayout()


        self.notice = QLabel()
        self.notice.setWordWrap(True)
        self.notice.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notice.setText(self.getNoticeMessage())
        self.notice.setMinimumWidth(150)
        self.notice.setStyleSheet('''font-size: 10px''')

        self.propertyGrid = PropertyGrid()
        self.propertyGrid.updateDataObject(self.cfg)
        self.layout.addWidget(self.propertyGrid, 0, 0)



        self.layout.addWidget(self.notice, 0, 1)

        self.container = QVBoxLayout()
        self.dlg.setMinimumSize(600,400)
        self.dlg.setBaseSize(800,800)
        self.dlg.btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        self.dlg.btns.accepted.connect(self.dlg.accept)
        self.dlg.btns.rejected.connect(self.dlg.reject)
        self.container.addLayout(self.layout)
        self.container.addWidget(self.dlg.btns)
        self.dlg.setLayout(self.container)     

    def show(self):
        if self.dlg.exec_():
            self.cfg.save()
            ConfigManager.instance().notifyUpdate()
            #msg = QMessageBox(self.qwin)
            #msg.setText("Changes Saved! You must reload the application to see them.")
            #msg.exec_()

