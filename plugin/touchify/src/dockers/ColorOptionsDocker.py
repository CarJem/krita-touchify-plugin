
from krita import *
from PyQt5.QtCore import *

from ..resources import ResourceManager

DOCKER_TITLE = 'Color Options'


class ColorSourceToggle(QWidget):
    def __init__(self, parent: QWidget | None = None, cubeSize: int = 25):
        super(ColorSourceToggle, self).__init__(parent)
        self.canvas: Canvas = None
        self.setContentsMargins(2,2,2,2)

        self.cubeSize = cubeSize

        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.updateColors)
        self.timer_pulse.setInterval(100)
        self.timer_pulse.start()

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.gridLayout = QHBoxLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.setFgBtn = QPushButton(self)
        self.setFgBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFgBtn.clicked.connect(self.setForegroundColor)
        self.setFgBtn.setFixedHeight(self.cubeSize)
        self.gridLayout.addWidget(self.setFgBtn)

        self.toggleBtn = QPushButton(self)
        self.toggleBtn.setIcon(ResourceManager.materialIcon("swap-horizontal"))
        self.toggleBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.toggleBtn.clicked.connect(self.toggleColors)
        self.toggleBtn.setFixedSize(self.cubeSize, self.cubeSize)
        self.toggleBtn.setStyleSheet("border-radius: 0px;")
        self.gridLayout.addWidget(self.toggleBtn)

        self.setBgBtn = QPushButton(self)
        self.setBgBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setBgBtn.clicked.connect(self.setBackgroundColor)
        self.setBgBtn.setFixedHeight(self.cubeSize)
        self.gridLayout.addWidget(self.setBgBtn)

        self.resetBtn = QPushButton(self)
        self.resetBtn.setIcon(ResourceManager.kritaIcon("color-to-alpha"))
        self.resetBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resetBtn.clicked.connect(self.resetColors)
        self.resetBtn.setFixedSize(self.cubeSize, self.cubeSize)
        self.resetBtn.setStyleSheet("border-radius: 0px;")
        self.gridLayout.addWidget(self.resetBtn)

    def setForegroundColor(self):
        Krita.instance().action("chooseForegroundColor").trigger()

    def setBackgroundColor(self):
        Krita.instance().action("chooseBackgroundColor").trigger()

    def toggleColors(self):
        Krita.instance().action("toggle_fg_bg").trigger()
        self.updateColors()

    def resetColors(self):
        Krita.instance().action("reset_fg_bg").trigger()
        self.updateColors()

    def showEvent(self, event):
        self.timer_pulse.start()
        super().showEvent(event)

    def closeEvent(self, event):
        self.timer_pulse.stop()
        super().closeEvent(event)

    def krita_to_qcolor(self, source: ManagedColor):
        if self.canvas == None or source == None: return QColor()
        return source.colorForCanvas(self.canvas)

    def updateColors(self):
        activeWin = Krita.instance().activeWindow()
        if activeWin == None: return
        activeView = activeWin.activeView()
        if activeView == None: return
        
        fg_color = self.krita_to_qcolor(activeView.foregroundColor())
        bg_color = self.krita_to_qcolor(activeView.backgroundColor())

        self.setFgBtn.setStyleSheet("border: 1px solid transparent; background-color: {0}".format(fg_color.name()))
        self.setBgBtn.setStyleSheet("border: 1px solid transparent; background-color: {0}".format(bg_color.name()))

    def onCanvasChanged(self, canvas: Canvas):
        self.canvas = canvas
        self.updateColors()

class ColorOptionsDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.colorToggle = ColorSourceToggle(self, 25)
        self.setWidget(self.colorToggle)
        self.setFixedHeight(50)
        self.colorToggle.onCanvasChanged(self.canvas())

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        self.colorToggle.onCanvasChanged(canvas)