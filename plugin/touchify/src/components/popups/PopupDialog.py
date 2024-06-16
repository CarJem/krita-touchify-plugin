from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from ...cfg.CfgPopup import CfgPopup
from ...config import *
from ....resources import *

from .PopupDialog_ToolboxTitlebar import PopupDialog_ToolboxTitlebar
from krita import *

POPUP_BTN_IDENTIFIER = "⠀"


class PopupDialog(QDialog):

    parent: QMainWindow
    
    def __init__(self, parent: QMainWindow, args: CfgPopup):     
        super().__init__(parent)    
        self.parent: QMainWindow = parent
        self.metadata = args
        self.allowOpacity = False
        self.popupMode = self.metadata.popupType
        self.popupType = self.metadata.type

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.popupMode == "popup":
                self.close()
        return super().event(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def paintEvent(self, event=None):
        if self.allowOpacity:
            painter = QPainter(self)
            baseColor = self.palette().brush(QPalette.ColorRole.Window)
            painter.setOpacity(self.metadata.opacity)
            painter.setBrush(baseColor)
            painter.setPen(baseColor.color())   
            painter.drawRect(self.rect())

    def applySpecialRules(self):
        if self.popupMode == "popup":
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        elif self.popupMode == "window":
            pass
        elif self.popupMode == "toolbox":
            self.setWindowFlags(Qt.WindowType.Tool)
            self.setWindowTitle(self.metadata.btnName)
            self._layout.insertWidget(0, PopupDialog_ToolboxTitlebar(self))
        else:
            pass


    def initLayout(self):
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("popupFrame")
        self.frame.setLayout(self.grid)
        
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self.frame)
        self.setLayout(self._layout)

        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.applySpecialRules()

        stylesheet = "border: 1px solid white; background: palette(window)"        
        if self.allowOpacity:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setWindowOpacity(self.metadata.opacity)
            stylesheet = f"""border: 1px solid rgba(255,255,255, {self.metadata.opacity}); opacity: {self.metadata.opacity};"""

        self.frame.setStyleSheet("QFrame#popupFrame { " + stylesheet  + " }")

    def getGeometry(self, position, width, height, isMouse = False):
        dialog_width, dialog_height = self.generateSize()

        screen = QGuiApplication.screenAt(position)
        screen_geometry = screen.geometry()
        screenSize = screen.size()

        screen_x = screen_geometry.x()
        screen_y = screen_geometry.y()
        screen_height = screenSize.height()
        screen_width = screenSize.width()

        
        offset_x = position.x() 
        offset_y = position.y()
        
        if not isMouse:
            offset_x += (width // 2) - (dialog_width // 2)
            offset_y += (height)

        actual_x = offset_x
        actual_y = offset_y

        if actual_x + dialog_width > screen_x + screen_width:
            actual_x = screen_x + screen_width - dialog_width
        elif actual_x < screen_x:
            actual_x = screen_x

        if actual_y + dialog_height > screen_y + screen_height:
            actual_y = screen_y + screen_height - dialog_height

        return [actual_x, actual_y, dialog_width, dialog_height]
        
    def generateSize(self):
        return [0, 0]
    

    def collapse(self):
        self.frame.hide()
        self.resize(self.minimumSize())

    def expand(self):
        self.frame.show()
    
    def triggerPopup(self, mode):
        if self.isVisible():
            self.close()
            if not self.popupMode == "popup":
                return
        
        actual_x = 0
        actual_y = 0
        dialog_width = 0
        dialog_height = 0
        
        if mode == "mouse":
            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QCursor.pos(), 0, 0, True)
        else:
            for qobj in self.parent.findChildren(QToolButton):
                actions = qobj.actions()
                if actions:
                    for action in actions:
                        if action.text() == self.metadata.btnName + POPUP_BTN_IDENTIFIER:
                            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())
        
        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
        self.show()

        if self.popupMode == "popup":
            self.activateWindow()


