from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *



class PropertyGrid_Dialog(QDialog):

    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)
        self.setWindowTitle("EDITOR")
        self.canReject = False

    def actual_reject(self):
        self.canReject = True
        self.reject()

    def reject(self):
        if self.canReject:
            super().reject()