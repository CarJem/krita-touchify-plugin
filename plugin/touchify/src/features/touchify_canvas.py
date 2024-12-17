from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from touchify.src.components.touchify.canvas.NtCanvas import NtCanvas

from touchify.src.variables import *
from touchify.src.settings import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.extension import Touchify


from krita import *
    
class TouchifyCanvas(QObject):

    def __init__(self, instance: "Touchify"):
        super().__init__(instance)
        self.appEngine = instance
        self.ntCanvas: NtCanvas | None = None

    def windowCreated(self):
        self.qWin = self.appEngine.windowSource.qwindow()
        self.ntCanvas.windowCreated(self.appEngine)

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

        config = TouchifySettings.instance().preferences()

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
        TouchifySettings.instance().preferences().CanvasWidgets_EnableToolbox = toggled
        TouchifySettings.instance().preferences().save()

    def nuToolOptionsToggled(self, toggled):
        TouchifySettings.instance().preferences().CanvasWidgets_EnableToolshelf = toggled
        TouchifySettings.instance().preferences().save()
    
    def nuToolOptionsAltToggled(self, toggled):
        TouchifySettings.instance().preferences().CanvasWidgets_EnableAltToolshelf = toggled
        TouchifySettings.instance().preferences().save()
