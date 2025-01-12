from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class DockerToolbar(QWidget):
    def __init__(self, parent = None, mode: Qt.Orientation = Qt.Orientation.Horizontal):
        super().__init__(parent)

        match mode:
            case Qt.Orientation.Vertical:
                self.widgetLayout = QVBoxLayout(self)
                self.widgetLayout.setContentsMargins(0,0,0,0)
                self.setLayout(self.widgetLayout)
            case Qt.Orientation.Horizontal:
                self.widgetLayout = QHBoxLayout(self)
                self.widgetLayout.setContentsMargins(0,0,0,0)
                self.setLayout(self.widgetLayout)
            case _:
                self.widgetLayout = QHBoxLayout(self)
                self.widgetLayout.setContentsMargins(0,0,0,0)
                self.setLayout(self.widgetLayout)    


    def addLayout(self, layout, stretch = 0):
        return self.widgetLayout.addLayout(layout, stretch)

    def addWidget(self, widget, stretch = 0, alignment = Qt.Alignment()):
        return self.widgetLayout.addWidget(widget, stretch, alignment)


