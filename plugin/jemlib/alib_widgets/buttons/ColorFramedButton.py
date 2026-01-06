from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets  import *
from PyQt5.QtCore import pyqtProperty

class ColorFramedButton(QPushButton):
    
    def __init__(self, _parent: QWidget = None, color: QColor | None = None):
        super(ColorFramedButton, self).__init__(_parent)
        self.__color = color
        self.__padding = 6

    @pyqtProperty(int)
    def padding(self):
        return self.__padding
    
    @padding.setter
    def padding(self, val: int):
        self.__padding = val
        self.update()
        
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        
        r = self.rect()
        p = QPainter(self)
        
        frame_size = 1
        
        x = self.__padding
        y = self.__padding
        width = (r.width()) - (self.__padding * 2)
        height = (r.height()) - (self.__padding * 2)
        
        if self.__color:
            frame_color = self.palette().color(QPalette.ColorRole.AlternateBase)
            fill_color = QColor(self.__color)
        
        if not self.isEnabled():
            fill_color.setAlpha(128)
            frame_color.setAlpha(128)
        
        if self.__color:
            p.fillRect(int(x), int(y), int(width + frame_size), int(height + frame_size), frame_color)
            p.fillRect(int(x + frame_size), int(y + frame_size), int(width - frame_size), int(height - frame_size), fill_color)
      
    def setColor(self, color: QColor | None = None):
        self.__color = color
        self.update()
    