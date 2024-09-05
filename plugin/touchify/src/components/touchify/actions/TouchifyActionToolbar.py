from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TouchifyActionToolbar(QToolBar):
    def __init__(self, parent: QWidget | None = None, title: str | None = None):
        super().__init__(parent, title)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
    def setVisible(self, state: bool):
        if self.property("wasvisible") != None:
            self.setProperty("wasvisible", None)
        else:
            super().setVisible(state)