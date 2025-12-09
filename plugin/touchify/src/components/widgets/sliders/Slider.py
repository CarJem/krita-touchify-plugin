
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from touchify.src.components.krita.KisAngleSelector import KisAngleSelector
from touchify.src.components.krita.KisSliderSpinBox import KisSliderSpinBox

class RotatableContainer(QGraphicsView):

    def __init__(self, parent, widget: QWidget, angle: float):

        super().__init__(parent)

        scene = QGraphicsScene(self)
        self.setScene(scene)

        self.ignoreConentsResize = False

        self.proxy = QGraphicsProxyWidget()
        self.proxy.setContentsMargins(0,0,0,0)
        self.proxy.setWidget(widget)
        self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
        self.proxy.setRotation(angle)
        scene.addItem(self.proxy)

    def rotate(self, angle):
        self.proxy.setRotation(angle)


class Slider(RotatableContainer):


    sigOnSizeChanged = pyqtSignal(QSize)
    def __init__(self, slider: KisSliderSpinBox | KisAngleSelector, parent=None):
        self._slider = slider
        self._isVertical = False
        super().__init__(parent, self._slider, 0)
        self.setContentsMargins(0,0,0,0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.sigOnSizeChanged.connect(self.updateSliderSize)
        self.updateOrientation()

    def slider(self) -> KisSliderSpinBox | KisAngleSelector:
        return self._slider

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

    def paintEvent(self, event):
        self.updateSliderSize(self.height() if self._isVertical else self.width())
        return super().paintEvent(event)
            
    def setOrientation(self, orientation: Qt.Orientation | str):
        if isinstance(orientation, Qt.Orientation):
            self._isVertical = orientation == Qt.Orientation.Vertical
        elif orientation == "horizontal":
            self._isVertical = False
        elif orientation == "vertical":
            self._isVertical = True
        
        self.updateOrientation()

    def updateSliderSize(self, length: int):
        self._slider.setFixedWidth(length)

    def updateOrientation(self):
        self.setFixedSize(self.size())
        self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
        self.setMinimumSize(0,0)

        if self._isVertical:
            self.setFixedWidth(30)
            self.setMinimumHeight(100)
        else:
            self.setFixedHeight(30)
            self.setMinimumWidth(100)

        rotation = 90 if self._isVertical else 0
        self.rotate(rotation)
        self.updateSliderSize(self.height() if self._isVertical else self.width())

        

