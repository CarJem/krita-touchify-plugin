from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from touchify.src.helpers import TouchifyHelpers
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

        settings_menu = self.qWin.findChild(QMenu, 'settings')

        configureAction = TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_CONFIGURE, settings_menu, settings_menu, 'options_configure')
        configureAction.setIcon(Krita.instance().icon("configure"))

        popupPaletteAction = TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_OTHER_SHOWPOPUPPALETTE, settings_menu, settings_menu, 'toolbars_submenu_action')
        popupMenuAction = TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_OTHER_SHOWMENUBARPOPUP, settings_menu, settings_menu, 'toolbars_submenu_action')
        settings_menu.insertSeparator(popupMenuAction)

        TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_DOCKERUTILS_MENU, settings_menu, settings_menu, 'view_toggledockers')

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


    def createActions(self, window: Window, subItemPath: str):

        docker_utils_path = "{0}/{1}".format(TOUCHIFY_ID_MENU_ROOT, "Toggle Dockers...")

        # Show Popup Palette
        popupPaletteToggle = window.createAction(TOUCHIFY_ID_ACTION_OTHER_SHOWPOPUPPALETTE, "Show Popup Palette", "settings")
        popupPaletteToggle.setCheckable(False)
        popupPaletteToggle.triggered.connect(self.showPopupPalette)

        # Show Popup Menu
        popupMenuToggle = window.createAction(TOUCHIFY_ID_ACTION_OTHER_SHOWMENUBARPOPUP, "Show Popup Menu", "settings")
        popupMenuToggle.setCheckable(False)
        popupMenuToggle.triggered.connect(self.showMenubarPopup)

        self.docker_utils_menu = QtWidgets.QMenu("Docker Utils", window.qwindow())
        self.docker_utils_action = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_MENU, "Toggle Dockers...", "settings")
        self.docker_utils_action.setMenu(self.docker_utils_menu)

        # Toggle Dockers
        toggleDockersLeft = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLELEFT, "Toggle Left Dockers", docker_utils_path)
        toggleDockersLeft.triggered.connect(lambda: self.toggleDirectionalDockers(1))
        self.docker_utils_menu.addAction(toggleDockersLeft)

        toggleDockersRight = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLERIGHT, "Toggle Right Dockers", docker_utils_path)
        toggleDockersRight.triggered.connect(lambda: self.toggleDirectionalDockers(2))
        self.docker_utils_menu.addAction(toggleDockersRight)

        toggleDockersTop = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLEUP, "Toggle Top Dockers", docker_utils_path)
        toggleDockersTop.triggered.connect(lambda: self.toggleDirectionalDockers(4))
        self.docker_utils_menu.addAction(toggleDockersTop)

        toggleDockersBottom = window.createAction(TOUCHIFY_ID_ACTION_DOCKERUTILS_TOGGLEDOWN, "Toggle Bottom Dockers", docker_utils_path)
        toggleDockersBottom.triggered.connect(lambda: self.toggleDirectionalDockers(8))
        self.docker_utils_menu.addAction(toggleDockersBottom)

        

        
