
from krita import *
from PyQt5.QtCore import *
from touchify.__env__ import *

class IconButton(QPushButton):



    def __init__(self, parent: QWidget | None = None):
        super(IconButton, self).__init__(parent)
        self.icon_img: QIcon | None = None
        self._margin = 2
        self.setContentsMargins(0,0,0,0)

    def paintEvent(self, ev: QPaintEvent):
        super().paintEvent(ev)
        if self.icon_img == None:
            return
        
        icon_size = ev.rect().size().shrunkBy(QMargins(self._margin,self._margin,self._margin,self._margin))        
        painter = QPainter(self)
        painter.drawPixmap(QPoint(self._margin,self._margin), self.icon_img.pixmap(QSize(icon_size.width(), icon_size.height())))
        painter.end()

    def setIcon(self, icon: QIcon):
        self.icon_img = icon
    
    def updateIcon(self):
        pass
        
    def resizeEvent(self, a0: QResizeEvent):
        self.updateIcon()
        super().resizeEvent(a0)