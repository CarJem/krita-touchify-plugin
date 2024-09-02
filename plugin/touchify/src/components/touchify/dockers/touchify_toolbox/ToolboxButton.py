from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPalette, QColor

from krita import *

class ToolboxButton(QToolButton):

    def __init__(self, actionName: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.actionName = actionName

        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(74, 108, 134))
        self.setPalette(palette)


    def enterEvent(self, event):
        super().enterEvent(event)

        if len(Krita.instance().documents()) == 0: # disable buttons before document is visible
            self.setEnabled(False)
        else:
            self.setEnabled(True)