from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *



class PropertyGrid_Dialog(QDialog):

    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setWindowTitle("EDITOR")