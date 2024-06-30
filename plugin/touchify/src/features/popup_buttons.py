from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, QSize
import os
import json
from functools import partial
import sys
import importlib.util

from ..variables import *

from ..cfg.CfgPopup import CfgPopup
from ..config import *
from ..resources import *
from ..components.popups.PopupDialog import *
from ..components.popups.PopupDialog_Actions import *
from ..components.popups.PopupDialog_Docker import *



from krita import *



class PopupButtons:

    popup_dialogs: dict[str, PopupDialog] = {}
    pending_actions = []
    popup_data = {}

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

        for action in self.pending_actions:
            root_menu.addAction(action)

    def createAction(self, window: Window, popup: CfgPopup, actionPath):
        actionName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_POPUP, popup.id)
        displayName = popup.btnName + POPUP_BTN_IDENTIFIER
        iconName = popup.icon
        id = popup.id
        hotkeyNumber = popup.hotkeyNumber

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.iconLoader(iconName)        
        action.setIcon(icon)
        action.triggered.connect(lambda: self.showPopup(action, id, "button"))

        if not hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(hotkeyNumber).triggered.connect(lambda: self.showPopup(action, id, "mouse"))

        self.pending_actions.append(action)

    def createActions(self, window, actionPath):
        sectionName = TOUCHIFY_ID_ACTIONS_POPUP

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for popup in cfg.popups:
            self.popup_data[popup.id] = popup
            self.createAction(window, popup, subItemPath)

    def showPopup(self, action: QAction, id, mode: str):

        _sender = action.sender()
        _parent = None
        if isinstance(_sender, QWidget):
            _parent: QWidget = _sender

        needToBuild = False
        if not id in self.popup_dialogs:
            needToBuild = True
        elif self.popup_dialogs[id] == None:
            needToBuild =  True

        if needToBuild:
            qwin = Krita.instance().activeWindow().qwindow()
            self.popup_dialogs[id] = self.createPopup(qwin, self.popup_data[id])

        self.popup_dialogs[id].triggerPopup(mode, _parent)

    def onConfigUpdated(self):
        for popupKeys in self.popup_dialogs:
            popup: PopupDialog = self.popup_dialogs[popupKeys]
            popup.shutdownWidget()
            self.popup_dialogs[popupKeys] = None


        cfg: ConfigFile = ConfigManager.instance().getJSON()
        for item in cfg.popups:
            newPopupData: CfgPopup = item
            id = newPopupData.id
            if id in self.popup_data:
                self.popup_data[id] = newPopupData

