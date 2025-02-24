
from krita import *
from PyQt5.QtCore import *

from touchify.__env__ import *


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class CanvasPatternPicker(QPushButton):

    def __init__(self, parent: QWidget | None = None):
        super(CanvasPatternPicker, self).__init__(parent)
        self.clicked.connect(self.openBrushPicker)
        self.cached_pixmap: QPixmap = None

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window
        self.notifier = window.api_window.notifier
        self.notifier.patternChanged.connect(self.onPatternChanged)
        self.onPatternChanged(self.notifier.getCurrentPattern())

    def openBrushPicker(self):
        self.appEngine.managers.mgr_actions.Create_Popup("pattern_chooser_popup", self)
    
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)

    def updateIcon(self):
        if not self.pattern: 
            return
        
        icon_width = self.width()
        icon_height = self.height()
    
        pixmap = QPixmap(icon_width * self.devicePixelRatio(), icon_height*self.devicePixelRatio())
        pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        pixmap_painter = QPainter(pixmap)

        clipRegion = QRegion(0, 0, icon_width, icon_height)
        clipRegion -= QRegion(0, 0, 1, 1)
        clipRegion -= QRegion(icon_width - 1, 0, 1, 1)
        clipRegion -= QRegion(icon_width - 1, icon_height - 1, 1, 1)
        clipRegion -= QRegion(0, icon_height - 1, 1, 1)

        pixmap_painter.setClipRegion(clipRegion)
        pixmap_painter.setClipping(True)

        resource_image = self.pattern.image()

        img = QImage(icon_width * self.devicePixelRatio(), icon_height*self.devicePixelRatio(), QImage.Format.Format_ARGB32)
        img.setDevicePixelRatio(self.devicePixelRatioF())
        #img.fill()
        if resource_image.width() < icon_width or resource_image.height() < icon_height:
            paint2 = QPainter()
            paint2.begin(img)
            
            x = 0
            while x < icon_width:
                y = 0 
                while y < icon_height:
                    paint2.drawImage(x, y, resource_image);
                    y += resource_image.height()
                x += resource_image.width()
            paint2.end()
        else:
            img = resource_image.scaled(icon_width*self.devicePixelRatio(), icon_height*self.devicePixelRatio(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pixmap_painter.drawImage(QRect(0,0, icon_width, icon_height), img)     

        self.cached_pixmap = pixmap
        self.setIcon(QIcon(self.cached_pixmap))
  

    def resizeEvent(self, a0: QResizeEvent):
        self.setIconSize(self.size().shrunkBy(QMargins(4,4,4,4)))
        self.updateIcon()
        return super().resizeEvent(a0)

    def onPatternChanged(self, current_pattern: Resource):
        self.pattern = current_pattern
        self.updateIcon()
