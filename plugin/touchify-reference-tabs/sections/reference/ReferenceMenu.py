from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .ReferenceSection import ReferenceSection

class ReferenceMenu(QMenu):
    def __init__(self, section: ReferenceSection, parent: QWidget | None = None):
        super().__init__("Reference Settings", parent)
        self.reference = section

        self.addAction("New Reference...", self.reference.File_New)
        self.addAction("Open Reference...", self.reference.File_Open)
        self.addAction("Unload Reference...", self.reference.File_Unload)
        self.addAction("Save Reference", self.reference.File_Save)
        self.addAction("Save Reference As...", self.reference.File_Save_As)

    def onTabActivated(self):
        pass
