from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from touchify.src.variables import *
from touchify.src.settings import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..window import TouchifyWindow

from krita import *
    
class TouchifyShortcuts(object):


    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance

    def onAppEngineStart(self, instance: "TouchifyWindow"):
        self.appEngine = instance

    def windowCreated(self):
        self.qWin = self.appEngine.windowSource.qwindow()

    def showPopupPalette(self):
        activeWindow = self.appEngine.windowSource
        viewIndex = activeWindow.views().index(activeWindow.activeView())
        pobj = self.qWin.findChild(QWidget,'view_' + str(viewIndex))
        mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if not mobj.isVisible():
            
            parentWidget = mobj.parentWidget()
            center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
            center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
            mobj.move(center_x, center_y)
            mobj.show()
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

        activeWindow = self.appEngine.windowSource.qwindow()
        popupMenu = QMenu(activeWindow)
        menuBar = activeWindow.menuBar()
        iterateActions(popupMenu, menuBar)
        popupMenu.exec(QCursor.pos())

    def toggleDirectionalDockers(self, area: int):
        self.appEngine.docker_management.toggleDockersPerArea(area)

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.other_menu)
        menu.addMenu(self.docker_utils_menu)

    def createActions(self, window: Window, subItemPath: str):

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

        

        
