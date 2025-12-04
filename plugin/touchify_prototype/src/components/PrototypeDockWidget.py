
from krita import *
from PyQt5.QtCore import *


from touchify_prototype.src.components.PrototypeDockWidgetContainer import PrototypeDockWidgetContainer


class PrototypeDockWidget(DockWidget):

    def __init__(self): 
        super().__init__()

        w = PrototypeDockWidgetContainer(self)

        self.setWidget(w)
    
    def onLoaded(self):              
        pass

    def onUnload(self):
        pass

    def sizeHint(self):
        return super().sizeHint()

    def minimumSizeHint(self):
        return super().minimumSizeHint()

    def minimumSize(self):
        return super().minimumSize()
        
    def maximumSize(self):
        return super().maximumSize()
        
    def showEvent(self, event):
        return super().showEvent(event)

    def closeEvent(self, event):
        return super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        pass