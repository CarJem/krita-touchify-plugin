from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..settings.TouchifySettings import TouchifySettings
from ..components.touchify.canvas.NtCanvas import NtCanvas

from ..variables import *
from ..settings.TouchifyConfig import *
from ..stylesheet import Stylesheet
from PyQt5.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import Touchify


from krita import *
    
class TouchifyCanvas(QObject):

    def __init__(self, instance: "Touchify"):
        super().__init__(instance)
        self.appEngine = instance
        self.ntCanvas: NtCanvas | None = None

    def windowCreated(self):
        self.qWin = self.appEngine.windowSource.qwindow()
        self.ntCanvas.setManagers(self.appEngine.docker_management, self.appEngine.action_management)
        self.ntCanvas.windowCreated(self.appEngine.windowSource)

    def createAction(self, window: Window, id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
        result = window.createAction(id, text, menuLocation)
        result.setCheckable(setCheckable)
        result.setChecked(setChecked)
        if setCheckable:
            result.toggled.connect(onToggled)
        else:
            result.triggered.connect(onToggled)
        return result

    def createActions(self, window: Window, mainMenuBar: QMenuBar):

        config = TouchifySettings.instance()

        sublocation_name = "On-Canvas Widgets"
        sublocation_path = TOUCHIFY_ID_MENU_ROOT + "/" + sublocation_name

        nu_options_menu = QtWidgets.QMenu(sublocation_name, mainMenuBar)
        mainMenuBar.addMenu(nu_options_menu)

        nu_options_menu.addSection("Widgets")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLBOX, "Enable Toolbox", sublocation_path, True, config.CanvasWidgets_EnableToolbox, self.nuToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLSHELF, "Enable Toolshelf", sublocation_path, True, config.CanvasWidgets_EnableToolshelf, self.nuToolOptionsToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLSHELF_ALT, "Enable Toolshelf (Alt.)", sublocation_path, True, config.CanvasWidgets_EnableAltToolshelf, self.nuToolOptionsAltToggled))

        self.ntCanvas = NtCanvas(window.qwindow().window(), window)
        self.ntCanvas.createActions(window, nu_options_menu, sublocation_path)

    def onKritaConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onKritaConfigUpdate()

    def onConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onConfigUpdate()

    def nuToolboxToggled(self, toggled):
        TouchifySettings.instance().CanvasWidgets_EnableToolbox = toggled
        TouchifySettings.instance().saveSettings()

    def nuToolOptionsToggled(self, toggled):
        TouchifySettings.instance().CanvasWidgets_EnableToolshelf = toggled
        TouchifySettings.instance().saveSettings()
    
    def nuToolOptionsAltToggled(self, toggled):
        TouchifySettings.instance().CanvasWidgets_EnableAltToolshelf = toggled
        TouchifySettings.instance().saveSettings()

    def nuOptionsAltToolboxPosToggled(self, toggled):
        TouchifySettings.instance().CanvasWidgets_AlternativeToolboxPosition = toggled
        TouchifySettings.instance().saveSettings()

    def nuOptionsRightHandToolboxToggled(self, toggled):
        TouchifySettings.instance().CanvasWidgets_ToolboxOnRight = toggled
        TouchifySettings.instance().saveSettings()

    #TODO: Remove
    def nuOptionsOrientationSwapRequested(self):
        if self.ntCanvas:
            if self.ntCanvas.toolbox:
                pass
