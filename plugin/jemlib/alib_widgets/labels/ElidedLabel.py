from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class ElidedLabel(QLabel):

    def __init__(self, parent: QWidget = None, flags: Qt.WindowFlags | Qt.WindowType = None, elideMode: Qt.TextElideMode = Qt.TextElideMode.ElideRight):
        QLabel.__init__(self, parent, flags)
        self.m_elideMode = elideMode

    def __init__(self, parent: QWidget = None, elideMode: Qt.TextElideMode = Qt.TextElideMode.ElideRight):
        QLabel.__init__(self, parent)
        self.m_elideMode = elideMode

    def setElideMode(self, mode: Qt.TextElideMode):
        self.m_elideMode = mode

    def elideMode(self):
        return self.m_elideMode

    def paintEvent(self, event: QPaintEvent):
        if self.m_elideMode != Qt.TextElideMode.ElideNone:
            painter = QPainter(self)
            metrics = QFontMetrics(self.font())
            elided = metrics.elidedText(self.text(), self.m_elideMode, self.width())
            painter.drawText(self.rect(), self.alignment(), elided)
        else:
            QLabel.paintEvent(self, event)

    def minimumSizeHint(self):
        if self.m_elideMode != Qt.TextElideMode.ElideNone:
            fm = QFontMetrics(self.font())
            return QSize(fm.width("..."), fm.height())
        else:
            QLabel.minimumSizeHint(self)