from re import L
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..variables import *
from ..settings.TouchifyConfig import *
from ..stylesheet import Stylesheet
from PyQt5.QtWidgets import QMessageBox

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import Touchify

from krita import *
    
class TouchifyHotkeys(object):


    def __init__(self, instance: "Touchify"):
        self.appEngine = instance
        self.hotkeys_storage = {}
        self.hotkey_options_storage = {}

    def onAppEngineStart(self, instance: "Touchify"):
        self.appEngine = instance

    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()

    def showPopupPalette(self):
        activeWindow = Krita.instance().activeWindow()
        viewIndex = activeWindow.views().index(activeWindow.activeView())
        pobj = self.qWin.findChild(QWidget,'view_' + str(viewIndex))
        mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if not mobj.isVisible():
            parentWidget = mobj.parentWidget()
            center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
            center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
            mobj.show()
            mobj.move(center_x, center_y)
        else:
            mobj.hide()

    def showMenubarPopup(self):
        def iterateActions(destination: QMenu, menu: QMenu | QMenuBar):
            for action in menu.actions():
                if action.menu():
                    sourceMenu = action.menu()
                    subMenu = QMenu(destination)
                    subMenu.setTitle(sourceMenu.title())
                    iterateActions(subMenu, sourceMenu)
                    destination.addMenu(subMenu)
                else:
                    destination.addAction(action)

        activeWindow = Krita.instance().activeWindow().qwindow()
        popupMenu = QMenu(activeWindow)
        menuBar = activeWindow.menuBar()
        iterateActions(popupMenu, menuBar)
        popupMenu.exec(QCursor.pos())

    def toggleDirectionalDockers(self, area: int):
        self.appEngine.docker_management.toggleDockersPerArea(area)

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.hotkey_menu)
        menu.addMenu(self.other_menu)
        menu.addMenu(self.docker_utils_menu)
        
    
    def triggerHotkey(self, index: int):
        actionRequest = "none"
        cfg = TouchifyConfig.instance().getConfig().hotkeys
        match index:
            case  1: 
                actionRequest = cfg.hotkey1
            case  2: 
                actionRequest = cfg.hotkey2
            case  3: 
                actionRequest = cfg.hotkey3
            case  4: 
                actionRequest = cfg.hotkey4
            case  5: 
                actionRequest = cfg.hotkey5
            case  6: 
                actionRequest = cfg.hotkey6
            case  7: 
                actionRequest = cfg.hotkey7
            case  8: 
                actionRequest = cfg.hotkey8
            case  9: 
                actionRequest = cfg.hotkey9
            case 10: 
                actionRequest = cfg.hotkey10
                
        TouchifyConfig.instance().runHotkeyOption(actionRequest)

    def createActions(self, window: Window, subItemPath: str):

        self.hotkey_menu = QtWidgets.QMenu("Hotkey Actions")
        hotkey_subpath = "actions"

        # Global Hotkey Assignments
        for i in range(1, 11):
            hotkeyName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_HOTKEY, str(i))
            hotkeyAction = window.createAction(hotkeyName, "Touchify - Action " + str(i), subItemPath + "/" + hotkey_subpath)
            hotkeyAction.triggered.connect(lambda z, x=i: self.triggerHotkey(x))
            self.hotkeys_storage[i] = hotkeyAction
            self.hotkey_menu.addAction(hotkeyAction)

        self.other_menu = QtWidgets.QMenu("Other Actions")
        other_subpath = "other"

        # Show Popup Palette
        popupPaletteToggle = window.createAction(TOUCHIFY_ID_ACTION_OTHER_SHOWPOPUPPALETTE, "Show Popup Palette", subItemPath + "/" + other_subpath)
        popupPaletteToggle.setCheckable(False)
        popupPaletteToggle.triggered.connect(self.showPopupPalette)
        self.other_menu.addAction(popupPaletteToggle)

        # Show Popup Menu
        popupMenuToggle = window.createAction(TOUCHIFY_ID_ACTION_OTHER_SHOWMENUBARPOPUP, "Show Popup Menu", subItemPath + "/" + other_subpath)
        popupMenuToggle.setCheckable(False)
        popupMenuToggle.triggered.connect(self.showMenubarPopup)
        self.other_menu.addAction(popupMenuToggle)

        self.docker_utils_menu = QtWidgets.QMenu("Docker Utils")
        docker_utils_subpath = "docker_utils"

        # Toggle Dockers
        toggleDockersLeft = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLELEFT, "Toggle Left Dockers", subItemPath + "/" + docker_utils_subpath)
        toggleDockersLeft.triggered.connect(lambda: self.toggleDirectionalDockers(1))
        self.docker_utils_menu.addAction(toggleDockersLeft)

        toggleDockersRight = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLERIGHT, "Toggle Right Dockers", subItemPath + "/" + docker_utils_subpath)
        toggleDockersRight.triggered.connect(lambda: self.toggleDirectionalDockers(2))
        self.docker_utils_menu.addAction(toggleDockersRight)

        toggleDockersTop = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLEUP, "Toggle Top Dockers", subItemPath + "/" + docker_utils_subpath)
        toggleDockersTop.triggered.connect(lambda: self.toggleDirectionalDockers(4))
        self.docker_utils_menu.addAction(toggleDockersTop)

        toggleDockersBottom = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLEDOWN, "Toggle Bottom Dockers", subItemPath + "/" + docker_utils_subpath)
        toggleDockersBottom.triggered.connect(lambda: self.toggleDirectionalDockers(8))
        self.docker_utils_menu.addAction(toggleDockersBottom)

        

        
