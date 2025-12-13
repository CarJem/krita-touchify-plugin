
from touchify.src.alib_pyqtgraph.dockarea.DockDrop import DockDrop
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#from touchify.src.extensions import pyqt_extensions as PyQtExt

class ShelfDropDock(DockDrop):
    def __init__(self, dndWidget):
        super().__init__(dndWidget)
        self._parentAreaId: str = ""
    
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