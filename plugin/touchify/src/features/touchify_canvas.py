from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..settings.TouchifySettings import TouchifySettings
from ..components.nu_tools.NtCanvas import NtCanvas

from ..variables import *
from ..settings.TouchifyConfig import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance


from krita import *
    
class TouchifyCanvas(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance
        self.ntCanvas: NtCanvas | None = None

    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()
        self.ntCanvas.setDockerManager(self.appEngine.docker_management)
        self.ntCanvas.windowCreated(self.appEngine.instanceWindow)

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
        
        nu_options_menu.addSection("Widget Options")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_SWAPTOOLBOXORIENTATION, "Swap Toolbox Orientation", sublocation_path, False, False, self.nuOptionsOrientationSwapRequested))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_RIGHTHANDTOOLBOX, "Right Hand Toolbox", sublocation_path, True, config.CanvasWidgets_ToolboxOnRight, self.nuOptionsRightHandToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ALTTOOLBOXPOSITION, "Alternative Toolbox Position", sublocation_path, True, config.CanvasWidgets_AlternativeToolboxPosition, self.nuOptionsAltToolboxPosToggled))

        self.ntCanvas = NtCanvas(window)
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

    def nuOptionsOrientationSwapRequested(self):
        if self.ntCanvas:
            if self.ntCanvas.toolbox:
                self.ntCanvas.toolbox.swapOrientation()
