
from PyQt5 import *
from PyQt5.QtWidgets import *



from touchify_prototype.third_deps.pyqtgraph_docking.dockarea.Dock import Dock
from touchify_prototype.third_deps.pyqtgraph_docking.dockarea.DockArea import DockArea
from touchify_prototype.third_deps.pyqtgraph_docking.widgets.LayoutWidget import LayoutWidget


# Subclass QMainWindow to customize your application's main window
class PrototypeDockWidgetContainer(DockArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup()
    def floatDock(self, dock):
        return None
        #return super().floatDock(dock)

    def addDockWidget(self, name, widget):
        d1 = Dock(name, size=(1, 1),autoOrientation=False)
        d1.setMinimumWidth(50)
        w1 = LayoutWidget()
        w1.addWidget(widget, row=0, col=0)
        d1.addWidget(w1)
        self.addDock(d1)
        return d1
        

    def setup(self):
        w1 = QWidget()
        w1.setStyleSheet("background-color: red")
        d1 = self.addDockWidget("Dock1", w1)

        w2 = QWidget()
        w2.setStyleSheet("background-color: blue")
        d2 = self.addDockWidget("Dock2", w2)

        w3 = QWidget()
        w3.setStyleSheet("background-color: green")
        d3 = self.addDockWidget("Dock3", w3)

        w4 = QWidget()
        w4.setStyleSheet("background-color: yellow")
        d4 = self.addDockWidget("Dock4", w4)


