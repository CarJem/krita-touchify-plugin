from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QPalette, QColor

from .....stylesheet import Stylesheet

from krita import *

class ToolboxButton(QToolButton):

    def __init__(self, actionName: str, parent: QWidget | None = None):
        super().__init__(parent)

        self.actionName = actionName
        self.__hasMenu = False

        palette = QPalette()
        palette.setColor(QPalette.Button, QColor(74, 108, 134))
        self.setPalette(palette)

        self.setStyleSheet(Stylesheet.instance().touchify_nt_toolbox_button)


    def setMenu(self, menu: QMenu):
        self.__hasMenu = True if menu else False
        super().setMenu(menu)

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

        if self.__hasMenu:
            rect = event.rect()

            triangleScale = 4
            triangleOffset = 2
            triangleFill = qApp.palette().text().color()

            point1 = QPoint(rect.bottomRight().x() - triangleOffset, rect.bottomRight().y() - triangleOffset)
            point2 = QPoint(point1.x(), point1.y() - triangleScale)
            point3 = QPoint(point1.x() - triangleScale, point1.y())

            painter = QPainter(self)
            path = QPainterPath()
            painter.begin(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path.moveTo(point1)
            path.lineTo(point2)
            path.lineTo(point3)
            path.lineTo(point1)
            painter.fillPath(path, triangleFill)

    def enterEvent(self, event):
        super().enterEvent(event)

        if len(Krita.instance().documents()) == 0: # disable buttons before document is visible
            self.setEnabled(False)
        else:
            self.setEnabled(True)