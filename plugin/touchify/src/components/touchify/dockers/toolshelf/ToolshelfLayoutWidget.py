from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ToolshelfLayoutWidget(QWidget):
    def __init__(self, orientation: Qt.Orientation, columns: int = 0, rows: int = 0, name: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.orientation = orientation

        if orientation == Qt.Orientation.Horizontal:
            #self.ourLayout = QHBoxLayout(self)
            self.ourLayout = QGridLayout(self)
        elif orientation == Qt.Orientation.Vertical:
            #self.ourLayout = QVBoxLayout(self)
            self.ourLayout = QGridLayout(self)
        else:
            error = TypeError().add_note("invalid orientation: {0}".format(str(orientation)))
            raise error
        
        if name != "":
            self.setObjectName(name)
        
        #print(f"[{self.objectName()}]: Columns:{columns}, Rows:{rows}")
        
        
        self.ourLayout.setContentsMargins(0,0,0,0)
        self.ourLayout.setSpacing(0)
        self.setLayout(self.ourLayout)


    def addWidget(self, widget: QWidget, x: int, y: int):
        #print(f"[{self.objectName()}]: Adding to: {x},{y}")
        self.ourLayout.addWidget(widget, y, x)