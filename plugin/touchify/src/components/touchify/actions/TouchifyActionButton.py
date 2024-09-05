import uuid
from ....resources import ResourceManager
from ....variables import *
from ....ext.extensions_krita import *
from krita import *
from ....settings.TouchifyConfig import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TouchifyActionButton(QToolButton):

    def __init__(self, parent = None):
        super(TouchifyActionButton, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.intervalTimer = QTimer(self)
        self.setFocusPolicy(Qt.NoFocus)
        self.toggled.connect(self.highlight)
        self._resizing = False
        
        self.meta_icon: QIcon = None
        self.meta_text: str = ""
        
    def setMetadata(self, text, icon):
        self.meta_text = text
        self.meta_icon = icon

    def setIcon(self, icon):
        if isinstance(icon, QIcon):
            super().setIcon(icon)
        elif isinstance(icon, QPixmap):
            super().setIcon(QIcon(icon))
        elif isinstance(icon, QImage):
            super().setIcon(QIcon(QPixmap.fromImage(icon)))
        else:
            raise TypeError(f"Unable to set icon of invalid type {type(icon)}")

    def setColor(self, color): # In case the Krita API opens up for a "color changed" signal, this could be useful...
        if isinstance(color, QColor):
            pxmap = QPixmap(self.iconSize())
            pxmap.fill(color)
            self.setIcon(pxmap)
        else:
            raise TypeError(f"Unable to set color of invalid type {type(color)}")

    def highlight(self, toggled):
        p = self.window().palette()
        if toggled:
            p.setColor(QPalette.Button, p.color(QPalette.Highlight))
        self.setPalette(p)