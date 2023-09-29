from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import json
from functools import partial
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *

POPUP_BTN_IDENTIFIER = "⠀"


class PopupDialog(QDialog):

    parent: QMainWindow

    dockerWidget: QDockWidget = None
    dockerWindow: QMainWindow = None
    dockerLocation: Qt.DockWidgetArea = None
    dockerVisibility: bool = False

    def __init__(self, parent: QMainWindow, args: Popup):     
        super().__init__(parent)    

        self.parent = parent
        self.metadata = args
        self.allowOpacity = False

        self.popupType = self.metadata.type
        if self.popupType == "actions":
            self.allowOpacity = True
            self.grid = self.generateActionsLayout()
        elif self.popupType == "docker":
            self.grid = self.generateDockerLayout()
            self.getDockerDetails(True)
        else:
            raise Exception("Invalid popup type: " + self.popupType)
        
        self.initLayout()
    
    def closeEvent(self, event):
        self.updateDocker(True)
        super().closeEvent(event)

    def paintEvent(self, event=None):
        if self.allowOpacity:
            painter = QPainter(self)
            baseColor = self.palette().brush(QPalette.ColorRole.Window)
            painter.setOpacity(self.metadata.opacity)
            painter.setBrush(baseColor)
            painter.setPen(baseColor.color())   
            painter.drawRect(self.rect())

    def initLayout(self):
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("popupFrame")
        self.frame.setLayout(self.grid)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.frame)
        self.setLayout(layout)
                
        self.setFocusPolicy(Qt.ClickFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.window().setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)

        stylesheet = "border: 1px solid white;"

        if self.allowOpacity:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setWindowOpacity(self.metadata.opacity)
            stylesheet = f"""border: 1px solid rgba(255,255,255, {self.metadata.opacity}); opacity: {self.metadata.opacity};"""
            
        self.frame.setStyleSheet("QFrame#popupFrame { " + stylesheet  + " }")
            

    def runAction(self, actionName):
        try:
            action = Krita.instance().action(actionName)
            if action:
                action.trigger()
        except:
            pass

    def getActionIcon(self, iconName, isCustomIcon):
        return ResourceManager.iconLoader(iconName, "actions", isCustomIcon)
            
    def createActionButton(self, layout, text, icon, isCustomIcon, action, x, y):

        opacityLevel = self.metadata.opacity
        btn_stylesheet = f"""
            QToolButton {{
                border-radius: 0px; 
                background-color: rgba(0,0,0,{opacityLevel}); 
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px
            }}
            
            QToolButton:hover {{
                background-color: rgba(155,155,155,{opacityLevel}); 
            }}
                          
            QToolButton:pressed {{
                background-color: rgba(128,128,128,{opacityLevel}); 
            }}
        """

        btn = QToolButton()
        btn.setStyleSheet(btn_stylesheet)
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        if icon:
            btn.setIcon(self.getActionIcon(icon, isCustomIcon))
            btn.setIconSize(QSize(self.metadata.icon_width, self.metadata.icon_height))

        btn.setWindowOpacity(opacityLevel)
        btn.setFixedSize(self.metadata.item_width, self.metadata.item_height)
        btn.clicked.connect(lambda: self.runAction(action))
        layout.addWidget(btn, x, y)
    
    def generateActionsLayout(self):
        layout = QGridLayout()

        current_x = 0
        current_y = 0
        current_index = 0

        padding = self.metadata.grid_padding
        maximum_x = self.metadata.grid_width
        item_count = len(self.metadata.items)

        while current_index < item_count:
            if not current_x < maximum_x:
                current_y += 1
                current_x = 0
            
            btn = self.metadata.items[current_index]
            self.createActionButton(layout, btn.text, btn.icon, btn.customIcon, btn.action, current_y, current_x)
            current_x += 1
            current_index += 1

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(padding)
        layout.setVerticalSpacing(padding)
        return layout
   
    def generateDockerLayout(self):
        grid = QHBoxLayout()
        return grid

    def updateDocker(self, closing = False):
        if closing:
            if self.dockerWindow:
                self.grid.removeWidget(self.dockerWidget)
                self.dockerWindow.addDockWidget(self.dockerLocation, self.dockerWidget)

                titlebarSetting = Krita.instance().readSetting("", "showDockerTitleBars", "false")
                showTitlebar = True if titlebarSetting == "true" else False
                self.dockerWidget.titleBarWidget().setVisible(showTitlebar)

                self.dockerWidget.setVisible(self.dockerVisibility)
        else:
            self.getDockerDetails()
            self.dockerWidget.titleBarWidget().setVisible(False)
            self.grid.addWidget(self.dockerWidget)
            self.dockerWidget.setVisible(True)

    def getDockerDetails(self, firstLoad = False):
        if firstLoad:
            dockersList = Krita.instance().dockers()
            for docker in dockersList:
                if (docker.objectName() == self.metadata.docker_id):
                    self.dockerWidget = docker
                    self.dockerWindow = Krita.instance().activeWindow().qwindow()
                    return
            
        self.dockerVisibility = self.dockerWidget.isVisible()
        self.dockerLocation = self.dockerWindow.dockWidgetArea(self.dockerWidget)

    def getGeometry(self, position, width, height, isMouse = False):
        dialog_width, dialog_height = self.generateSize()

        screen = QtGui.QGuiApplication.screenAt(position)
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
        if self.popupType == "actions":
            padding = self.metadata.grid_padding
            grid_width = self.metadata.grid_width
        
            item_width = self.metadata.item_width + padding * 2
            item_height = self.metadata.item_height + padding * 2

            item_count = len(self.metadata.items)


            item_count_x = grid_width
            item_count_y = item_count / grid_width


            dialog_width = (item_count_x * item_width)
            dialog_height = (item_count_y * item_height)

            return [int(dialog_width), int(dialog_height)]
        elif self.popupType == "docker":
            dialog_width = self.metadata.item_width
            dialog_height = self.metadata.item_height
            return [int(dialog_width), int(dialog_height)]
        else:
            return [0, 0]
    
    def triggerPopup(self, mode):

        if self.isVisible():
            self.close()

        actual_x = 0
        actual_y = 0
        dialog_width = 0
        dialog_height = 0

        if mode == "mouse":
            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QtGui.QCursor.pos(), 0, 0, True)
        else:
            for qobj in self.parent.findChildren(QToolButton):
                actions = qobj.actions()
                if actions:
                    for action in actions:
                        if action.text() == self.metadata.btnName + POPUP_BTN_IDENTIFIER:
                            actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())

        if self.popupType == "docker":
            self.updateDocker()


        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
        self.show()


