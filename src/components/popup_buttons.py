from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *

popup_dialogs = {}
BUTTON_INDICATOR = "⠀"

class PopupDialog(QDialog):
    def __init__(self, parent, args):     
        super().__init__(parent)    

        self.parent = parent
        self.metadata = args
        self.grid = self.generateLayout()

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

    def getIcon(self, iconName, isCustomIcon):
        RESOURCE_PATH = os.path.join('popups', self.metadata["id"])
        if isCustomIcon:
            return ResourceManager.customIcon(RESOURCE_PATH, iconName)
        else:
            return ResourceManager.kritaIcon(iconName)
            
    def runAction(self, actionName):
        try:
            action = Krita.instance().action(actionName)
            if action:
                action.trigger()
        except:
            pass

    def createButton(self, layout, text, icon, isCustomIcon, action, x, y):

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
            btn.setIcon(self.getIcon(icon, isCustomIcon))
            btn.setIconSize(QSize(self.metadata["icon_width"], self.metadata["icon_height"]))

        btn.setFixedSize(self.metadata["item_width"], self.metadata["item_height"])
        btn.clicked.connect(lambda: self.runAction(action))
        layout.addWidget(btn, x, y)
    
    def generateLayout(self):
        layout = QGridLayout()

        current_x = 0
        current_y = 0
        current_index = 0

        padding = self.metadata["grid_padding"]
        maximum_x = self.metadata["grid_width"]
        item_count = len(self.metadata["items"])

        while current_index < item_count:
            if not current_x < maximum_x:
                current_y += 1
                current_x = 0
            
            btn = self.metadata["items"][current_index]
            self.createButton(layout, btn["text"], btn["icon"], btn["customIcon"], btn["action"], current_y, current_x)
            current_x += 1
            current_index += 1

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(padding)
        layout.setVerticalSpacing(padding)
        return layout
    
    def generateSize(self):
        padding = self.metadata["grid_padding"]
        grid_width = self.metadata["grid_width"]
        
        item_width = self.metadata["item_width"] + padding * 2
        item_height = self.metadata["item_height"] + padding * 2

        item_count = len(self.metadata["items"])


        item_count_x = grid_width
        item_count_y = item_count / grid_width


        dialog_width = (item_count_x * item_width)
        dialog_height = (item_count_y * item_height)

        return [int(dialog_width), int(dialog_height)]

    def updatePosition(self):
        for qobj in self.parent.findChildren(QToolButton):
            actions = qobj.actions()
            if actions:
                for action in actions:
                    if action.text() == self.metadata["btnName"] + BUTTON_INDICATOR:
                        self.generateGeometry(qobj)
                        return

    def showPopup(self):
        self.updatePosition()
        self.show()

    def generateGeometry(self, button):
        dialog_width, dialog_height = self.generateSize()

        pos = button.mapToGlobal(QPoint(0,0))
        screenSize = QtWidgets.QApplication.primaryScreen().size()

        intScreenHeight = screenSize.height()
        intScreenWidth = screenSize.width()

        offset_x = pos.x() + (button.width() // 2) - (dialog_width // 2)
        offset_y = pos.y() + (button.height())

        actual_x = min(offset_x, intScreenWidth - dialog_width)
        actual_y = min(offset_y, intScreenHeight - dialog_height)

        self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
    
class PopupButtons:

    def showPopup(self, id, data):
        if not id in popup_dialogs:
            qwin = Krita.instance().activeWindow().qwindow()
            popup_dialogs[id] = PopupDialog(qwin, data)

        popup_dialogs[id].showPopup()

    def addPopup(self, window, menu, popup, actionPath):

        actionName = 'VaporJem_Popup_{0}'.format(popup["btnName"])
        displayName = popup["btnName"] + BUTTON_INDICATOR
        id = popup["id"]

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.customIcon(os.path.join('popups', id), 'toolbar_icon')
        action.setIcon(icon)

        menu.addAction(action)
        action.triggered.connect(lambda: self.showPopup(id, popup))


    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Popups"
        root = window.createAction(sectionName, "Popups", actionPath)
        root_menu = QtWidgets.QMenu(sectionName, window.qwindow())
        root.setMenu(root_menu)

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.getJSON()

        for popup in cfg.popups:
            self.addPopup(window, root_menu, popup, subItemPath)


