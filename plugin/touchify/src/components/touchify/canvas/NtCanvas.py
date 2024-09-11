from PyQt5.QtWidgets import QMdiArea, QDockWidget

from ....docker_manager import DockerManager
from ....action_manager import ActionManager
from .NtToolbox import NtToolbox
from .NtToolshelf import NtToolshelf
from ....settings.TouchifySettings import TouchifySettings
from krita import *
from PyQt5.QtCore import QObject, QEvent, QPoint
from ....variables import *
from .NtWidgetPad import NtWidgetPad
from .NtWidgetPadAlignment import NtWidgetPadAlignment

from ..special.DockerContainer import DockerContainer

class NtCanvas(QObject):
    def __init__(self, parent: QObject, window: Window):
        super().__init__(parent)
        self.window = window
        self.windowLoaded = False
        self.dockerManager = None

        self.toolboxAlignment = self.getToolboxAlignment()
        self.toolOptionsAlignment = self.getToolOptionsAlignment()
        self.alternativeToolboxPos = self.getToolboxAltPositionState()

        self.toolbox = None
        self.toolboxOptions = None
        self.toolOptions = None

        self.updateElements()
        self.updateCanvas()

    def setManagers(self, manager: DockerManager, actionsManager: ActionManager):
        self.dockerManager = manager
        self.actions_manager = actionsManager

    def windowCreated(self, window: Window):
        self.window = window
        self.windowLoaded = True
        self.window.qwindow().themeChanged.connect(self.updatePalette)

        self.updateElements()
        self.updateCanvas()


    def createActions(self, window: Window, menu: QMenu, path: str):
        menu.addSection("Widget Visibility")

        tlb_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLBOX, "Show Toolbox", path)
        tlb_action.toggled.connect(lambda: self.togglePadVisibility("toolbox"))
        tlb_action.setCheckable(True)
        tlb_action.setChecked(True)
        menu.addAction(tlb_action)

        tlshlf_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLSHELF, "Show Toolshelf", path)
        tlshlf_action.toggled.connect(lambda: self.togglePadVisibility("toolshelf"))
        tlshlf_action.setCheckable(True)
        tlshlf_action.setChecked(True)
        menu.addAction(tlshlf_action)

        tlshlf_alt_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLSHELF_ALT, "Show Toolshelf (Alt.)", path)
        tlshlf_alt_action.toggled.connect(lambda: self.togglePadVisibility("toolshelf_alt"))
        tlshlf_alt_action.setCheckable(True)
        tlshlf_alt_action.setChecked(True)
        menu.addAction(tlshlf_alt_action)

    def togglePadVisibility(self, pad: str):
        if pad == "toolbox" and self.toolbox: self.toolbox.pad.toggleWidgetVisible()
        elif pad == "toolshelf" and self.toolOptions: self.toolOptions.pad.toggleWidgetVisible()
        elif pad == "toolshelf_alt" and self.toolboxOptions: self.toolboxOptions.pad.toggleWidgetVisible()
        self.updateCanvas()


    #region Event Functions
    def onConfigUpdate(self):
        if self.toolboxOptions:
            self.toolboxOptions.toolshelf.onConfigUpdated()
        if self.toolOptions:
            self.toolOptions.toolshelf.onConfigUpdated()
    
    def onKritaConfigUpdate(self):        
        self.alternativeToolboxPos = self.getToolboxAltPositionState()
        self.toolboxAlignment = self.getToolboxAlignment()
        self.toolOptionsAlignment = self.getToolOptionsAlignment()

        self.updateElements()
        self.updateCanvas()

        if self.toolboxOptions:
            self.toolboxOptions.toolshelf.onKritaConfigUpdate()
        if self.toolOptions:
            self.toolOptions.toolshelf.onKritaConfigUpdate()
            
    #endregion

    #region Get / Set Functions
    def getToolOptionsAlignment(self):
        isToolboxOnRight = TouchifySettings.instance().CanvasWidgets_ToolboxOnRight
        return NtWidgetPadAlignment.Left if isToolboxOnRight else NtWidgetPadAlignment.Right

    def getToolboxAlignment(self):
        isToolboxOnRight = TouchifySettings.instance().CanvasWidgets_ToolboxOnRight
        return NtWidgetPadAlignment.Right if isToolboxOnRight else NtWidgetPadAlignment.Left
    
    def getToolboxAltPositionState(self):
        return TouchifySettings.instance().CanvasWidgets_AlternativeToolboxPosition
    #endregion

    #region Update Functions

    def updateElements(self):
        if self.windowLoaded == False:
            return
        
        usesNuToolbox = TouchifySettings.instance().CanvasWidgets_EnableToolbox
        usesNuToolOptionsAlt = TouchifySettings.instance().CanvasWidgets_EnableAltToolshelf
        usesNuToolOptions = TouchifySettings.instance().CanvasWidgets_EnableToolshelf

        if self.toolbox == None and usesNuToolbox:
            self.toolbox = NtToolbox(self, self.toolboxAlignment, self.window)
            self.installEventFilters(self.toolbox)
            self.toolbox.pad.show()
        elif self.toolbox and not usesNuToolbox:
            self.removeEventFilters(self.toolbox)
            self.toolbox.close()
            self.toolbox = None

        if self.toolboxOptions == None and usesNuToolOptionsAlt:
            self.toolboxOptions = NtToolshelf(self, self.window, self.toolboxAlignment, False, self.dockerManager, self.actions_manager)
            self.installEventFilters(self.toolboxOptions)
            self.toolboxOptions.pad.show()
        elif self.toolboxOptions and not usesNuToolOptionsAlt:
            self.removeEventFilters(self.toolboxOptions)
            self.toolboxOptions.close()
            self.toolboxOptions = None

        if self.toolOptions == None and usesNuToolOptions:
            self.toolOptions = NtToolshelf(self, self.window, self.toolOptionsAlignment, True, self.dockerManager, self.actions_manager)
            self.installEventFilters(self.toolOptions)
            self.toolOptions.pad.show()
        elif self.toolOptions and not usesNuToolOptions:
            self.removeEventFilters(self.toolOptions)
            self.toolOptions.close()
            self.toolOptions = None

        if self.toolbox != None:
            self.toolbox.pad.setViewAlignment(self.toolboxAlignment)
        if self.toolboxOptions != None:
            self.toolboxOptions.pad.setViewAlignment(self.toolboxAlignment)
        if self.toolOptions != None:
            self.toolOptions.pad.setViewAlignment(self.toolOptionsAlignment)

    def updateCanvas(self):
        if self.toolboxOptions == None:
            if self.toolbox:
                self.toolbox.pad.offset_x_left = 0
                self.toolbox.pad.offset_x_right = 0
            return
        elif self.toolbox == None:
            if self.toolboxOptions:
                self.toolboxOptions.pad.offset_x_left = 0
                self.toolboxOptions.pad.offset_x_right = 0
            return
        else:
            if self.alternativeToolboxPos:
                if self.toolboxAlignment == NtWidgetPadAlignment.Left:
                    self.toolbox.pad.offset_x_left = self.toolboxOptions.pad.width()
                    self.toolbox.pad.offset_x_right = 0
                elif self.toolboxAlignment == NtWidgetPadAlignment.Right:
                    self.toolbox.pad.offset_x_right = self.toolboxOptions.pad.width()
                    self.toolbox.pad.offset_x_left = 0

                self.toolboxOptions.pad.offset_x_right = 0
                self.toolboxOptions.pad.offset_x_left = 0
            else:
                if self.toolboxAlignment == NtWidgetPadAlignment.Left:
                    self.toolboxOptions.pad.offset_x_left = self.toolbox.pad.width()
                    self.toolboxOptions.pad.offset_x_right = 0
                elif self.toolboxAlignment == NtWidgetPadAlignment.Right:
                    self.toolboxOptions.pad.offset_x_right = self.toolbox.pad.width()
                    self.toolboxOptions.pad.offset_x_left = 0

                self.toolbox.pad.offset_x_right = 0
                self.toolbox.pad.offset_x_left = 0

        if self.toolbox: self.toolbox.pad.adjustToView()
        if self.toolboxOptions: self.toolboxOptions.pad.adjustToView()
        if self.toolOptions: self.toolOptions.pad.adjustToView()

    def updatePalette(self):
        if self.toolboxOptions:
            self.toolboxOptions.toolshelf.onConfigUpdated()
        if self.toolOptions:
            self.toolOptions.toolshelf.onConfigUpdated()

    #endregion

    #region Connect/Disconnect Functions

    def installEventFilters(self, widget: NtToolshelf | NtToolbox):
        widget.pad.btnHide.clicked.connect(self.updateCanvas)
        #widget.pad.installEventFilter(self)
        #self.qWin.installEventFilter(self)

    def removeEventFilters(self, widget: NtToolshelf | NtToolbox):
        widget.pad.btnHide.clicked.disconnect(self.updateCanvas)
        #widget.pad.removeEventFilter(self)
        #self.qWin.removeEventFilter(self)

    #endregion


