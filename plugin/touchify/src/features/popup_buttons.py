from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QToolButton, QGridLayout, QSizePolicy
from PyQt5.QtCore import QObject, Qt, QEvent, QPoint, QRect, QSize
import os
import json
from functools import partial
import sys
import importlib.util



from ..variables import *

from ..cfg.CfgPopup import CfgPopup
from ..settings.TouchifyConfig import *
from ..resources import *
from ..components.popups.PopupDialog import *
from ..components.popups.PopupDialog_Actions import *
from ..components.popups.PopupDialog_Docker import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance

from krita import *



class PopupButtons(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance
        self.popup_data = {}
        self.popup_dialogs: dict[str, PopupDialog] = {}
        self.actions: dict[str, QAction] = {}

    def createPopup(self, qwin: QMainWindow, data: CfgPopup):
        if data.type == "actions":
            return PopupDialog_Actions(qwin, data)
        elif data.type == "docker":
            return PopupDialog_Docker(qwin, data, self.appEngine.docker_management)
        else:
            return PopupDialog(qwin, data)

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def createAction(self, window: Window, popup: CfgPopup, actionPath):
        actionName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_POPUP, popup.id)
        displayName = popup.btnName + POPUP_BTN_IDENTIFIER
        iconName = popup.icon
        id = popup.id
        hotkeyNumber = popup.hotkeyNumber

        action = window.createAction(actionName, displayName, actionPath)
        icon = ResourceManager.iconLoader(iconName)        
        action.setIcon(icon)
        action.triggered.connect(lambda: self.showPopup(actionName, id, "button"))

        if not hotkeyNumber == 0:
            self.appEngine.touchify_hotkeys.getHotkeyAction(hotkeyNumber).triggered.connect(lambda: self.showPopup(action, id, "mouse"))

        self.actions[actionName] = action
        self.root_menu.addAction(action)

    def createActions(self, window, actionPath):
        sectionName = TOUCHIFY_ID_ACTIONS_POPUP
        subItemPath = actionPath + "/" + sectionName

        self.root_menu = QtWidgets.QMenu("Popups")

        cfg = TouchifyConfig.instance().getJSON()
        for popup in cfg.popups:
            self.popup_data[popup.id] = popup
            self.createAction(window, popup, subItemPath)

    def showPopup(self, actionName: str, id, mode: str):
        action = self.actions[actionName]
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
            qwin = self.appEngine.instanceWindow.qwindow()
            self.popup_dialogs[id] = self.createPopup(qwin, self.popup_data[id])

        self.popup_dialogs[id].triggerPopup(mode, _parent)

    def onConfigUpdated(self):
        for popupKeys in self.popup_dialogs:
            popup: PopupDialog = self.popup_dialogs[popupKeys]
            if popup != None:
                popup.shutdownWidget()
            self.popup_dialogs[popupKeys] = None


        cfg: TouchifyConfig.ConfigFile = TouchifyConfig.instance().getJSON()
        for item in cfg.popups:
            newPopupData: CfgPopup = item
            id = newPopupData.id
            if id in self.popup_data:
                self.popup_data[id] = newPopupData

