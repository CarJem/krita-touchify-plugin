from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
import os
import json
from functools import partial
import sys
import importlib.util

from ..variables import TOUCHIFY_AID_ACTIONS_POPUP, TOUCHIFY_ID_ACTIONS_POPUP

from ..cfg.CfgPopup import CfgPopup
from ..config import *
from ..resources import *
from ..components.popups.PopupDialog import *
from ..components.popups.PopupDialog_Actions import *
from ..components.popups.PopupDialog_Docker import *



from krita import *

popup_dialogs = {}
pending_actions = []
popup_data = {}

class PopupButtons:


    def createPopup(self, qwin: QMainWindow, data: CfgPopup):
        if data.type == "actions":
            return PopupDialog_Actions(qwin, data)
        elif data.type == "docker":
            return PopupDialog_Docker(qwin, data)
        else:
            return PopupDialog(qwin, data)


    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Popups", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)

    def createAction(self, window, popup: CfgPopup, actionPath):
        actionName = '{0}_{1}'.format(TOUCHIFY_AID_ACTIONS_POPUP, popup.id)
        displayName = popup.btnName + POPUP_BTN_IDENTIFIER
        iconName = popup.icon
        id = popup.id
        hotkeyNumber = popup.hotkeyNumber

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.iconLoader(iconName)        
        action.setIcon(icon)
        action.triggered.connect(partial(self.showPopup, id, "button"))

        if not hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(hotkeyNumber).triggered.connect(partial(self.showPopup, id, popup, "mouse"))

        pending_actions.append(action)

    def createActions(self, window, actionPath):
        sectionName = TOUCHIFY_ID_ACTIONS_POPUP

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for popup in cfg.popups:
            popup_data[popup.id] = popup
            self.createAction(window, popup, subItemPath)

    def showPopup(self, id, mode: str):
        needToBuild = True
        if not id in popup_dialogs:
            needToBuild = True
        elif popup_dialogs[id] == None:
            needToBuild =  True

        if needToBuild:
            qwin = Krita.instance().activeWindow().qwindow()
            popup_dialogs[id] = self.createPopup(qwin, popup_data[id])

        popup_dialogs[id].triggerPopup(mode)

    def onConfigUpdated(self):
        cfg: ConfigFile = ConfigManager.instance().getJSON()
        for item in cfg.popups:
            newPopupData: CfgPopup = item
            id = newPopupData.id
            if id in popup_data:
                popup_data[id] = newPopupData
                popup_dialogs = None

