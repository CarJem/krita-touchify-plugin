from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ToolshelfSplitter(QWidget):
    def __init__(self, orientation: Qt.Orientation, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.orientation = orientation

        if orientation == Qt.Orientation.Horizontal:
            self.ourLayout = QHBoxLayout(self)
        elif orientation == Qt.Orientation.Vertical:
            self.ourLayout = QVBoxLayout(self)
        else:
            error = TypeError().add_note("invalid orientation: {0}".format(str(orientation)))
            raise error
        
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.ourLayout.setSpacing(0)
        self.setLayout(self.ourLayout)


    def addWidget(self, widget: QWidget):
        self.layout().addWidget(widget)