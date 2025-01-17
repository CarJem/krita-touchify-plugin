from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .ReferenceSection import ReferenceSection

class ReferenceMenu(QMenu):
    def __init__(self, section: ReferenceSection, parent: QWidget | None = None):
        super().__init__("Reference Settings", parent)
        self.reference = section

    def onTabActivated(self):
        pass
