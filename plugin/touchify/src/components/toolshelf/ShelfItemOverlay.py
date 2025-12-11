from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class ShelfItemOverlay(QtWidgets.QWidget):

    sigClicked = QtCore.pyqtSignal()
    sigMouseOverChanged = QtCore.pyqtSignal(bool)
    sigRightClicked = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget = None):
        QtWidgets.QWidget.__init__(self, parent)

        self.dock = None
        self.isMouseOver = False

        self.personallayout = QtWidgets.QGridLayout()
        self.personallayout.setContentsMargins(0, 0, 0, 0)
        self.personallayout.setSpacing(0)

        self.sigMouseOverChanged.connect(self.onMouseOverChanged)
        
        self.setLayout(self.personallayout)

    def onMouseOverChanged(self, state: bool):
        self.isMouseOver = state
        self.repaint()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setOpacity(0.2 if self.isMouseOver else 0.0)
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(QPen(Qt.GlobalColor.white))   
        painter.drawRect(event.rect())
        painter.end()

    def enterEvent(self, a0):
        self.sigMouseOverChanged.emit(True)
        return super().enterEvent(a0)
    
    def leaveEvent(self, a0):
        self.sigMouseOverChanged.emit(False)
        return super().leaveEvent(a0)

    def mousePressEvent(self, ev):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        self.pressPos = lpos
        self.mouseMoved = False
        ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.mouseMoved:
            lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
            self.mouseMoved = (lpos - self.pressPos).manhattanLength() > QtWidgets.QApplication.startDragDistance()

        if self.mouseMoved and ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.dock.startDrag()
        ev.accept()


    def mouseReleaseEvent(self, ev):
        ev.accept()
        if not self.mouseMoved:
            if ev.button() == QtCore.Qt.MouseButton.RightButton:
                self.sigRightClicked.emit()
            else:
                self.sigClicked.emit()

    def mouseDoubleClickEvent(self, ev):
        super(ShelfItemOverlay,self).mouseDoubleClickEvent(ev)

    def resizeEvent (self, ev):
        super(ShelfItemOverlay,self).resizeEvent(ev)