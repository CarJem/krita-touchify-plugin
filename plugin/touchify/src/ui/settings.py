from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
import sys
import importlib.util
from ..config import *
from ...resources import *
from ..ext.extensions import *
import xml.etree.ElementTree as ET
import re
import functools
import copy
import json
from ..components.PropertyGrid import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *

class SettingsDialog:

    def __init__(self):
        self.qwin = Krita.instance().activeWindow().qwindow()
        self.cfg = copy.deepcopy(ConfigManager.instance().cfg)

        self.dlg = QDialog(self.qwin)

        self.layout = QVBoxLayout()

        self.propertyGrid = PropertyGrid()
        self.propertyGrid.updateDataObject(self.cfg)
        self.layout.addWidget(self.propertyGrid)

        self.container = QVBoxLayout()
        self.dlg.setMinimumSize(400,400)
        self.dlg.setBaseSize(800,800)
        self.dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dlg.btns.accepted.connect(self.dlg.accept)
        self.dlg.btns.rejected.connect(self.dlg.reject)
        self.container.addLayout(self.layout)
        self.container.addWidget(self.dlg.btns)
        self.dlg.setLayout(self.container)     

    def show(self):
        if self.dlg.exec_():
            self.cfg.save()
            msg = QMessageBox(self.qwin)
            msg.setText("Changes Saved! You must reload the application to see them.")
            msg.exec_()

