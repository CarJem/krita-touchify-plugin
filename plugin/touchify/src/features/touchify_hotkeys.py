from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..docker_manager import DockerManager

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class TouchifyHotkeys:


    def showPopupPalette(self):
        qwin = Krita.instance().activeWindow().qwindow()
        viewIndex = Krita.instance().activeWindow().views().index(Krita.instance().activeWindow().activeView())
        pobj = qwin.findChild(QWidget,'view_' + str(viewIndex))
        mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if not mobj.isVisible():
            parentWidget = mobj.parentWidget()
            center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
            center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
            mobj.show()
            mobj.move(center_x, center_y)
        else:
            mobj.hide()

    def toggleDirectionalDockers(self, area: int):
        self.docker_manager.toggleDockersPerArea(area)

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.hotkey_menu)
        menu.addMenu(self.other_menu)
        menu.addMenu(self.docker_utils_menu)

    def windowCreated(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager

    def createActions(self, window: Window, subItemPath: str):

        self.hotkey_menu = QtWidgets.QMenu("Actions...")
        hotkey_subpath = "actions"

        # Global Hotkey Assignments
        for i in range(1, 10):
            hotkeyName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_HOTKEY, str(i))
            hotkeyAction = window.createAction(hotkeyName, "Touchify - Action " + str(i), subItemPath + "/" + hotkey_subpath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)
            self.hotkey_menu.addAction(hotkeyAction)

        self.other_menu = QtWidgets.QMenu("Other...")
        other_subpath = "other"

        # Show Popup Palette
        popupPaletteToggle = window.createAction(TOUCHIFY_ID_ACTION_OTHER_SHOWPOPUPPALETTE, "Show Popup Palette", subItemPath + "/" + other_subpath)
        popupPaletteToggle.setCheckable(False)
        popupPaletteToggle.triggered.connect(self.showPopupPalette)
        self.other_menu.addAction(popupPaletteToggle)


        self.docker_utils_menu = QtWidgets.QMenu("Docker Utils...")
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

        

        
