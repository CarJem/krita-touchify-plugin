from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
import os
import json
from functools import partial
import sys
import importlib.util
from ...config import *
from ...resources import *
from ..components.popups.PopupDialog import *
from ..components.popups.PopupDialog_Actions import *
from ..components.popups.PopupDialog_Docker import *


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...ext.PyKrita import *
else:
    from krita import *

popup_dialogs = {}
pending_actions = []

class PopupButtons:


    def createPopup(self, qwin: QMainWindow, data: Popup):
        if data.type == "actions":
            return PopupDialog_Actions(qwin, data)
        elif data.type == "docker":
            return PopupDialog_Docker(qwin, data)
        else:
            return PopupDialog(qwin, data)

    def showPopup(self, id, data: Popup, mode: str):
        if not id in popup_dialogs:
            qwin = Krita.instance().activeWindow().qwindow()
            popup_dialogs[id] = self.createPopup(qwin, data)
        popup_dialogs[id].triggerPopup(mode)


    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Popups", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)

    def createAction(self, window, popup: Popup, actionPath):
        actionName = 'VaporJem_Popup_{0}'.format(popup.btnName)
        displayName = popup.btnName + POPUP_BTN_IDENTIFIER
        iconName = popup.icon
        id = popup.id
        hotkeyNumber = popup.hotkeyNumber

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.iconLoader(iconName)        
        action.setIcon(icon)
        action.triggered.connect(partial(self.showPopup, id, popup, "button"))

        if not hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(hotkeyNumber).triggered.connect(partial(self.showPopup, id, popup, "mouse"))

        pending_actions.append(action)

    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Popups"

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for popup in cfg.popups:
            self.createAction(window, popup, subItemPath)


