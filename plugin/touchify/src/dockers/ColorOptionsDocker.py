
from krita import *
from PyQt5.QtCore import *

DOCKER_TITLE = 'Color Options'


class ColorSourceToggle(QWidget):
    def __init__(self, parent: QWidget | None = None, cubeSize: int = 25):
        super(ColorSourceToggle, self).__init__(parent)
        self.canvas: Canvas = None

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

        self.setBgBtn = QPushButton(self)
        self.setBgBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setBgBtn.clicked.connect(self.setBackgroundColor)
        self.setBgBtn.setFixedHeight(self.cubeSize)
        self.gridLayout.addWidget(self.setBgBtn)

        self.toggleBtn = QPushButton(self)
        self.toggleBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.toggleBtn.clicked.connect(self.toggleColors)
        self.toggleBtn.setFixedSize(self.cubeSize, self.cubeSize)
        self.toggleBtn.setStyleSheet("border-radius: 0px;")
        self.gridLayout.addWidget(self.toggleBtn)

        self.resetBtn = QPushButton(self)
        self.resetBtn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.resetBtn.clicked.connect(self.resetColors)
        self.resetBtn.setFixedSize(self.cubeSize, self.cubeSize)
        self.resetBtn.setStyleSheet("border-radius: 0px;")
        self.gridLayout.addWidget(self.resetBtn)

        self.initBitmaps()

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

    def initBitmaps(self):

        bitmap_size = 12

        arrowBitmap = QPixmap(bitmap_size,bitmap_size)
        arrowBitmap.fill(Qt.GlobalColor.transparent)
        
        p = QPainter(arrowBitmap)
        p.setPen(qApp.palette().windowText().color())

        #arrow pointing left
        p.drawLine(0, 3, 7, 3)
        p.drawLine(1, 2, 1, 4)
        p.drawLine(2, 1, 2, 5)
        p.drawLine(3, 0, 3, 6)

        #arrow pointing down
        p.drawLine(8, 4, 8, 11)
        p.drawLine(5, 8, 11, 8)
        p.drawLine(6, 9, 10, 9)
        p.drawLine(7, 10, 9, 10)
        p.end()
        
        resetBitmap = QPixmap(["12 12 4 1",
                 " 	c None",
                 ".	c #808080",
                 "+	c #000000",
                 "@	c #FFFFFF",
                 "........    ", 
                 ".++++++.    ", 
                 ".++++++.    ", 
                 ".++++++.    ", 
                 ".++++++.....", 
                 ".++++++.@@@.", 
                 ".++++++.@@@.", 
                 "........@@@.", 
                 "    .@@@@@@.", 
                 "    .@@@@@@.", 
                 "    .@@@@@@.", 
                 "    ........"
                ])
        
        self.resetBtn.setIcon(QIcon(resetBitmap))
        self.toggleBtn.setIcon(QIcon(arrowBitmap))

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

        self.setFgBtn.setStyleSheet("border-radius: 0px; background-color: {0}".format(fg_color.name()))
        self.setBgBtn.setStyleSheet("border-radius: 0px; background-color: {0}".format(bg_color.name()))

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