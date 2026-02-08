
from jemlib.alib_pyqtgraph.dockarea.DockDrop import DockDrop, DropAreaOverlay
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#from touchify.src.extensions import pyqt_extensions as PyQtExt

class ShelfDropDock(DockDrop):
    def __init__(self, dndWidget):
        super().__init__(dndWidget)
        self._parentAreaId: str = ""
        self.overlay = ShelfDropAreaOverlay(dndWidget)
        self.overlay.raise_()
    
    def setParentAreaId(self, val: str):
        self._parentAreaId = val

    def dragEnterEvent(self, ev: QDragEnterEvent):
        src = ev.source()
        if hasattr(src, 'implements') and src.implements('dock'):
            if hasattr(src, 'accessible') and src.accessible(self._parentAreaId):
                ev.accept()
            else:
                ev.ignore()
        else:
            #print "drag enter ignore"
            ev.ignore()

class ShelfDropAreaOverlay(DropAreaOverlay):

    def __init__(self, parent):
        super().__init__(parent)

    """Overlay widget that draws drop areas during a drag-drop operation"""
    def paintEvent(self, ev):
        if self.dropArea is None:
            return
        p = QPainter(self)
        rgn = self.rect()

        fill_color = self.window().palette().highlight().color()
        fill_color.setAlpha(50)

        border_color = self.window().palette().highlight().color()

        #fill_color = QColor(100, 100, 255, 50)
        #border_color = QColor(50, 50, 150)

        p.setBrush(QBrush(fill_color))
        p.setPen(QPen(border_color, 3))
        p.drawRect(rgn)
        p.end()