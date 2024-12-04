from PyQt5.QtCore import *
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.src.variables import TOUCHIFY_WIDGETPROPS_EDITING_SELECTED, TOUCHIFY_WIDGETPROPS_EDITING_ALLOWED

class ToolshelfEditableWidget(QObject):

    def setup(_target: QWidget): 
        _target.installEventFilter(ToolshelfEditableWidget(_target))

    def __init__(self, target: QWidget):
        super().__init__(target)
        self.target = target
        self.target.setProperty(TOUCHIFY_WIDGETPROPS_EDITING_ALLOWED, True)

        self.__paintEvent = self.target.paintEvent
        self.target.paintEvent = self.paintEvent

        self.__setProperty = self.target.setProperty
        self.target.setProperty = self.setProp

    def eventFilter(self, widget: QWidget, event: QEvent):
        #if self.target.underMouse() and self.target.property(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED):
            #return True
        return False


    def updateState(self):
        if self.target.property(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED):
            self.target.update()
        else:
            self.target.update()

    def setProp(self, name: str, val: any):
        self.__setProperty(name, val)
        self.updateState()

    def paintEvent(self, event: QPaintEvent):    
        self.__paintEvent(event)
        if self.target.property(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED):
            p = QPainter(self.target)
            p.setPen(QColor(0, 0, 155, 128))
            p.fillRect(event.rect(), QColor(0, 0, 155, 128))
            p.drawRect(event.rect())

