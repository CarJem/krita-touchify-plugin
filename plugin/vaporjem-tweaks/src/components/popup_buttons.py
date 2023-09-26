from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
import os
import json
from functools import partial
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *

popup_dialogs = {}
pending_actions = []
BUTTON_INDICATOR = "⠀"


class PopupDialog(QDialog):

    parent: QMainWindow

    def __init__(self, parent: QMainWindow, args: Config_Popup):     
        super().__init__(parent)    

        self.parent = parent
        self.metadata = args

        self.popupType = self.metadata.type
        if self.popupType == "actions":
            self.initActionsPopup()
        elif self.popupType == "docker":
            self.initDockerPopup()
            pass
        else:
            raise Exception("Invalid popup type: " + self.popupType)


    #region Actions Popup

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

        btn_stylesheet = """
            QToolButton {
                border-radius: 0px; 
                background-color: rgba(0,0,0,0.5); 
                padding: 5px 5px;
                border: 0px solid transparent; 
                font-size: 12px
            }
            
            QToolButton:hover {
                background-color: rgba(155,155,155,0.5); 
            }
                          
            QToolButton:pressed {
                background-color: rgba(128,128,128,0.5); 
            }
        """

        btn = QToolButton()
        btn.setStyleSheet(btn_stylesheet)
        btn.setText(text)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        if icon:
            btn.setIcon(self.getActionIcon(icon, isCustomIcon))
            btn.setIconSize(QSize(self.metadata.icon_width, self.metadata.icon_height))

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
    
    def initActionsPopup(self):
        self.grid = self.generateActionsLayout()

        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.Box)
        self.frame.setFrameShadow(QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setStyleSheet("border: 1px solid white")
        self.frame.setLayout(self.grid)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.frame)
        self.setLayout(layout)
                
        self.setFocusPolicy(Qt.ClickFocus)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)

    def showActionsPopup(self, actual_x, actual_y, dialog_width, dialog_height):
        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
        self.show()

    #endregion

    #region Docker Popup

    def popupDockerVisibilityChanged(self, s):
        if self.docker_instance.isVisible() == False:
            self.docker_instance.setWindowFlags(self.docker_oldWindowFlags)
            self.docker_instance.visibilityChanged.disconnect(self.popupDockerVisibilityChanged)

            self.docker_instance = None
            self.docker_oldWindowFlags = None
        
    def showDockerPopup(self, actual_x, actual_y, dialog_width, dialog_height):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == self.docker_id):
                self.docker_instance = docker
                self.docker_oldWindowFlags = self.docker_instance.windowFlags()

                self.docker_instance.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
                self.docker_instance.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
                self.docker_instance.visibilityChanged.connect(self.popupDockerVisibilityChanged)
                self.docker_instance.setVisible(True)

    def initDockerPopup(self):
        self.docker_id = self.metadata.docker_id

    #endregion

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
        


    def _openPopup(self, actual_x, actual_y, dialog_width, dialog_height):
        if self.popupType == "actions":
            self.showActionsPopup(actual_x, actual_y, dialog_width, dialog_height)
        elif self.popupType == "docker":
            self.showDockerPopup(actual_x, actual_y, dialog_width, dialog_height)
        
    def showButtonPopup(self):
        for qobj in self.parent.findChildren(QToolButton):
            actions = qobj.actions()
            if actions:
                for action in actions:
                    if action.text() == self.metadata.btnName + BUTTON_INDICATOR:
                        actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(qobj.mapToGlobal(QPoint(0,0)), qobj.width(), qobj.height())
                        self._openPopup(actual_x, actual_y, dialog_width, dialog_height)

    def showMousePopup(self):
        actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QtGui.QCursor.pos(), 0, 0, True)
        self._openPopup(actual_x, actual_y, dialog_width, dialog_height)

class PopupButtons:

    def showPopup(self, id, data: Config_Popup, mode: str):
        if not id in popup_dialogs:
            qwin = Krita.instance().activeWindow().qwindow()
            popup_dialogs[id] = PopupDialog(qwin, data)

        if mode == "mouse":
            popup_dialogs[id].showMousePopup()
        else:
            popup_dialogs[id].showButtonPopup()

    def addPopup(self, window, popup: Config_Popup, actionPath):

        actionName = 'VaporJem_Popup_{0}'.format(popup.btnName)
        displayName = popup.btnName + BUTTON_INDICATOR
        iconName = popup.icon
        isCustomIcon = popup.isIconCustom
        id = popup.id
        hotkeyNumber = popup.hotkeyNumber

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.iconLoader(iconName, "buttons", isCustomIcon)        
        action.setIcon(icon)
        action.triggered.connect(partial(self.showPopup, id, popup, "button"))

        if not hotkeyNumber == -1:
            ConfigManager.getHotkeyAction(hotkeyNumber).triggered.connect(partial(self.showPopup, id, popup, "mouse"))

        pending_actions.append(action)

    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Popups", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)

    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Popups"

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.getJSON()
        for popup in cfg.popups:
            self.addPopup(window, popup, subItemPath)


