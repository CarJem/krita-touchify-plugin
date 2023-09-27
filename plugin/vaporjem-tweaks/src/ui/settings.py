from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *
from ..ext.extensions import *
import xml.etree.ElementTree as ET
import re
import functools
import copy
import json
from ..components.propertygrid import *

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
        self.dlg.btns.accepted.connect(self.save)
        self.dlg.btns.rejected.connect(self.dlg.reject)
        self.container.addLayout(self.layout)
        self.container.addWidget(self.dlg.btns)
        self.dlg.setLayout(self.container)

    def save(self):
        msg = QMessageBox()
        data = json.dumps(self.cfg.auto_dockers, default=lambda o: o.__dict__, indent=4)
        msg.setText(data)
        msg.exec_()

    def show(self):
        self.dlg.show()

