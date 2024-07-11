from json import tool
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util

from .PopupDialog_Titlebar import PopupDialog_Titlebar

from ...cfg.CfgPopup import CfgPopup
from ...settings.TouchifyConfig import *
from ....resources import *
from ... import stylesheet

from krita import *

POPUP_BTN_IDENTIFIER = " [Popup]"


class PopupDialog(QDialog):


    
    def __init__(self, parent: QMainWindow, args: CfgPopup):     
        super().__init__(parent)  
        self.grid: QLayout = None
        self.parent: QMainWindow = parent
        self.metadata = args
        self.allowOpacity = False
        self.titlebarEnabled = False
        self.isCollapsed = False
        self.oldSize = None
        self.autoConceal = False
        
        self.popupMode = self.metadata.popupType
        self.popupType = self.metadata.type

        qApp.installEventFilter(self)


        self.winMargin = 3
        self._cursor = QCursor()
        self.resizeTop = False
        self.resizeBottom = False
        self.resizeLeft = False
        self.resizeRight = False
        self.isResizing = False

    #region Helper Methods

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

    def getActionSource(self, parent: QWidget | None):
        if parent != None:
            return self.getGeometry(parent.mapToGlobal(QPoint(0,0)), parent.width(), parent.height())
        else:
            for qobj in self.parent.findChildren(QToolButton):
                actions = qobj.actions()
                if actions:
                    for action in actions:
                        if action.text() == self.metadata.btnName + POPUP_BTN_IDENTIFIER:
                            return self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())
            return 0, 0, 0, 0

    #endregion

    #region Interface Methods

    def initLayout(self):
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        if self.popupMode == "popup":
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            self.autoConceal = True
        elif self.popupMode == "window":
            self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            self.setMouseTracking(True)
            self.autoConceal = False

        if self.allowOpacity:
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            self.setWindowOpacity(self.metadata.opacity)

        self.rootLayout = QVBoxLayout(self)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)
        self.setLayout(self.rootLayout)

        if self.popupMode == "window":
            self.titlebarEnabled = True
            self._toolbar = PopupDialog_Titlebar(self)
            self.rootLayout.addWidget(self._toolbar)
    
        self.frameWidget = QFrame(self)
        self.frameWidget.setFrameShape(QFrame.Box)
        self.frameWidget.setFrameShadow(QFrame.Plain)
        self.frameWidget.setLineWidth(0 if self.titlebarEnabled else 1)
        self.frameWidget.setObjectName("popupFrame")
        self.frameWidget.setStyleSheet(stylesheet.touchify_popup_frame(self.allowOpacity, self.metadata.opacity))
        self.rootLayout.addWidget(self.frameWidget)


        self.frameLayout = QVBoxLayout(self)
        self.frameLayout.setSpacing(0)
        self.frameLayout.setContentsMargins(0,0,0,0)
        self.frameWidget.setLayout(self.frameLayout)

        self.containerWidget = QWidget(self)
        self.containerWidget.setLayout(self.grid)
        self.frameLayout.addWidget(self.containerWidget)

    def generateSize(self):
        return [0, 0]
    
    def triggerPopup(self, ourMode: str, parent: QWidget | None):
        if self.isVisible():
            self.close()
            if not self.popupMode == "popup":
                return
        
        actual_x = 0
        actual_y = 0
        dialog_width = 0
        dialog_height = 0
        
        if ourMode == "mouse":
            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QCursor.pos(), 0, 0, True)
        else:
            actual_x, actual_y, dialog_width, dialog_height = self.getActionSource(parent)
        
        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
        self.show()

        if self.popupMode == "popup":
            self.activateWindow()

    def shutdownWidget(self):
        qApp.removeEventFilter(self)

    #endregion

    #region Window Methods

    def toggleMinimized(self):
        if self._toolbar:
            if self.isCollapsed:
                self.setMinimumSize(0, 0)
                self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                self.resize(self.oldSize)
                self.containerWidget.setVisible(True)
                self.oldSize = None
                self.isCollapsed = False
            else:
                self.oldSize = self.size()
                self.setFixedSize(self._toolbar.width(), self._toolbar.height())
                self.containerWidget.setVisible(False)
                self.isCollapsed = True

    def resizeWindow(self, e: QMouseEvent):
        window = self.window().windowHandle()
        # reshape cursor for resize
        if self._cursor.shape() == Qt.CursorShape.SizeHorCursor:
            if self.resizeLeft:
                window.startSystemResize(Qt.Edge.LeftEdge)
            elif self.resizeRight:
                window.startSystemResize(Qt.Edge.RightEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeVerCursor:
            if self.resizeTop:
                window.startSystemResize(Qt.Edge.TopEdge)
            elif self.resizeBottom:
                window.startSystemResize(Qt.Edge.BottomEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeBDiagCursor:
            if self.resizeTop and self.resizeRight:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.RightEdge)
            elif self.resizeBottom and self.resizeLeft:
                window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.LeftEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeFDiagCursor:
            if self.resizeTop and self.resizeLeft:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.LeftEdge)
            elif self.resizeBottom and self.resizeRight:
                window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.RightEdge)

    def updateCursor(self, p: QPoint):
        # give the margin to reshape cursor shape
        rect = self.rect()
        rect.setX(self.rect().x() + self.winMargin)
        rect.setY(self.rect().y() + self.winMargin)
        rect.setWidth(self.rect().width() - self.winMargin * 2)
        rect.setHeight(self.rect().height() - self.winMargin * 2)

        self.isResizing = rect.contains(p)
        if self.isResizing:
            # resize end
            self.unsetCursor()
            self._cursor = self.cursor()
            self.resizeTop = False
            self.resizeBottom = False
            self.resizeLeft = False
            self.resizeRight = False
        else:
            # resize start
            x = p.x()
            y = p.y()

            x1 = self.rect().x()
            y1 = self.rect().y()
            x2 = self.rect().width()
            y2 = self.rect().height()

            self.resizeLeft = abs(x - x1) <= self.winMargin # if mouse cursor is at the almost far left
            self.resizeTop = abs(y - y1) <= self.winMargin # far top
            self.resizeRight = abs(x - (x2 + x1)) <= self.winMargin # far right
            self.resizeBottom = abs(y - (y2 + y1)) <= self.winMargin # far bottom

            # set the cursor shape based on flag above
            if self.resizeTop and self.resizeLeft:
                self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
            elif self.resizeTop and self.resizeRight:
                self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
            elif self.resizeBottom and self.resizeLeft:
                self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
            elif self.resizeBottom and self.resizeRight:
                self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
            elif self.resizeLeft:
                self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
            elif self.resizeTop:
                self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
            elif self.resizeRight:
                self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
            elif self.resizeBottom:
                self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
            self.setCursor(self._cursor)

        self.isResizing = not self.isResizing

    #endregion
    
    #region Events 
    
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseMove:
            if self.titlebarEnabled:
                self.updateCursor(event.pos())
        return super().eventFilter(source, event)

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.autoConceal:
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

    def mousePressEvent(self, e: QMouseEvent):
        if self.titlebarEnabled:
            if e.button() == Qt.MouseButton.LeftButton and self.isResizing:
                self.resizeWindow(e)
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        if self.titlebarEnabled:
            self.updateCursor(e.pos())
        return super().enterEvent(e)
    
    #endregion
