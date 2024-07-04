from krita import *

DOCKER_TITLE = 'Brush HUD'


class CustomBrushHUD(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super(CustomBrushHUD, self).__init__(parent)
        #self.widgetLayout = QVBoxLayout(self)
        #self.setLayout(self.widgetLayout)

        self.lastView = None
        self.lastWidget = None
        self.lastLayout = None
        

    def canvasChanged(self):
        self.borrow()


    def findSource(self, activeWindow: Window, view: View):
        viewIndex = activeWindow.views().index(view)
        actualView = activeWindow.qwindow().findChild(QWidget,'view_' + str(viewIndex))
    
        popupPalette = next((w for w in actualView.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if popupPalette == None:
            return None
        
        brushHUD = next((w for w in popupPalette.findChildren(QWidget) if w.metaObject().className() == 'KisBrushHud'), None)
        if brushHUD == None:
            return None
        
        return brushHUD


    def borrow(self):
        if self.lastLayout != None:
            self.lastWidget.setLayout(self.lastLayout)
            
            self.lastLayout = None
            self.lastWidget = None
            self.lastView = None
        
        activeWindow = Krita.instance().activeWindow()
        if activeWindow == None:
            return
        
        activeView = activeWindow.activeView()
        if activeView == None:
            return
        
        self.lastView = activeView
        self.lastWidget = self.findSource(activeWindow, self.lastView)
        if self.lastWidget:
            self.lastLayout = self.lastWidget.layout()
            self.setLayout(self.lastLayout)

class DockerBrushHUD(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.sourceWidget = CustomBrushHUD(self)
        self.setWidget(self.sourceWidget)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        self.sourceWidget.canvasChanged()

