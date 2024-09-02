# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *
from .....cfg.CfgToolboxSubItem import CfgToolboxSubItem
from .....cfg.CfgToolboxItem import CfgToolboxItem

class ToolboxMenu(QMenu): # this is the subtools menu

    def __init__(self, parentBtn: QWidget, tool: CfgToolboxItem):
        super().__init__()
        self.parentBtn = parentBtn
        self.tool = tool
        self.items = self.tool.items

        self.setMouseTracking(True)

    def showEvent(self, event): # if the menu is shown
        super().showEvent(event)

        self.move(self.parentBtn.mapToGlobal(QPoint(0,0)) + QPoint(self.parentBtn.width(), 0)) # move menu to top-right button corner

    def mouseMoveEvent(self, event): # this causes the subtool menu to close if exited
        super().mouseMoveEvent(event)

        buttonTLC = self.parentBtn.geometry().topLeft() # gets the clicked button's top left corner point
        menuSize = QSize(self.geometry().size()) # size of subtool menu
        buttonColumn = QRect(buttonTLC, menuSize) # column bounded by button and menu

        bounds = self.geometry().united(buttonColumn) # add safe area so the cursor doesn't accidentally exit

        if bounds.contains(QCursor.pos()) == False:
            self.close()