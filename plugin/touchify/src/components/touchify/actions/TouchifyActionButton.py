from touchify.src.variables import *
from touchify.src.ext.KritaExtensions import *
from krita import *
from touchify.src.settings import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class TouchifyActionButton(QToolButton):

    timer_interval_triggered = pyqtSignal()

    def __init__(self, parent = None):
        super(TouchifyActionButton, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.NoFocus)
        self.toggled.connect(self.highlight)
        self._resizing = False
        
        self.meta_icon: QIcon = None
        self.meta_text: str = ""

        self.use_action_icon = False


        self.brushSelected = False

    def useActionIcon(self):
        self.use_action_icon = True
        
    def updateIcon(self, action: QAction):
        #TODO: Reimplement with Action Manager Logic
        if self.use_action_icon: self.setIcon(action.icon())
        
    def setMetadata(self, text, icon):
        self.meta_text = text
        self.meta_icon = icon

    def setBrushSelected(self, state: bool):
        self.brushSelected = state
        self.repaint()

    def setIcon(self, icon):
        if isinstance(icon, QIcon):
            super().setIcon(icon)
        elif isinstance(icon, QPixmap):
            super().setIcon(QIcon(icon))
        elif isinstance(icon, QImage):
            super().setIcon(QIcon(QPixmap.fromImage(icon)))
        else:
            raise TypeError(f"Unable to set icon of invalid type {type(icon)}")
        
    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
        if self.brushSelected: self.paintBrushHighlight(e)

    def paintBrushHighlight(self, e: QPaintEvent):
        hc = self.window().palette().color(QPalette.ColorRole.Highlight)
        rect = e.rect()
        opacity = 75
        thickness = 4

        painter = QPainter(self)
        painter.setBrush(QColor(hc.red(), hc.green(), hc.blue(), opacity))
        painter.drawRect(rect)

        rectPath = QPainterPath()
        rectPath.addRect(rect.x(),rect.y(),rect.width(),rect.height())
        painter.setPen(QPen(hc, thickness))
        painter.drawPath(rectPath)


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