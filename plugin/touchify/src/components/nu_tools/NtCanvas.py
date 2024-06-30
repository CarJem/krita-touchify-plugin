from PyQt5.QtWidgets import QMdiArea, QDockWidget
from .NtToolbox import NtToolbox
from .NtToolshelf import NtToolshelf
from ...config import InternalConfig
from krita import *
from PyQt5.QtCore import QObject, QEvent, QPoint
from ...variables import *

class NtCanvas():
    def __init__(self, window: Window):
        self.window = window

        self.toolboxAlignment = self.getToolboxAlignment()
        self.toolOptionsAlignment = self.getToolOptionsAlignment()
        self.alternativeToolboxPos = self.getToolboxAltPositionState()

        self.inShutdown = False

        self.toolbox = None
        self.toolboxOptions = None
        self.toolOptions = None

        self.updateElements()
        self.updatePadAlignments()
        self.updateCanvas()

    def dispose(self):
        self.inShutdown = True
        self.updateElements()

    def updateWindow(self, window: Window):
        self.window = window


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
        elif pad == "toolshelf" and self.toolbox: self.toolOptions.pad.toggleWidgetVisible()
        elif pad == "toolshelf_alt" and self.toolbox: self.toolboxOptions.pad.toggleWidgetVisible()
        self.updateCanvas()


    #region Event Functions
    def eventFilter(self, obj, e: QEvent):

        if (e.type() == QEvent.Type.Move or e.type() == QEvent.Type.Resize):
            self.updateCanvas()
        
        return False 
    
    def onConfigUpdate(self):
        self.updateStyleSheet()

        if self.toolboxOptions:
            self.toolboxOptions.toolshelf.onConfigUpdated()
        if self.toolOptions:
            self.toolOptions.toolshelf.onConfigUpdated()
    
    def onKritaConfigUpdate(self):        
        self.alternativeToolboxPos = self.getToolboxAltPositionState()
        self.toolboxAlignment = self.getToolboxAlignment()
        self.toolOptionsAlignment = self.getToolOptionsAlignment()

        self.updateElements()
        self.updatePadAlignments()
        self.updateCanvas()

        if self.toolboxOptions:
            self.toolboxOptions.toolshelf.onKritaConfigUpdate()
        if self.toolOptions:
            self.toolOptions.toolshelf.onKritaConfigUpdate()
            
    #endregion

    #region Get / Set Functions
    def getToolOptionsAlignment(self):
        isToolboxOnRight = InternalConfig.instance().CanvasWidgets_ToolboxOnRight
        return 'left' if isToolboxOnRight else 'right'

    def getToolboxAlignment(self):
        isToolboxOnRight = InternalConfig.instance().CanvasWidgets_ToolboxOnRight
        return 'right' if isToolboxOnRight else 'left'
    
    def getToolboxAltPositionState(self):
        return InternalConfig.instance().CanvasWidgets_AlternativeToolboxPosition
    #endregion

    #region Update Functions

    def updateElements(self):
        usesNuToolbox = InternalConfig.instance().CanvasWidgets_EnableToolbox
        usesNuToolOptionsAlt = InternalConfig.instance().CanvasWidgets_EnableAltToolshelf
        usesNuToolOptions = InternalConfig.instance().CanvasWidgets_EnableToolshelf

        if self.inShutdown:
            usesNuToolbox = False
            usesNuToolOptions = False
            usesNuToolOptionsAlt = False

        if self.toolbox == None and usesNuToolbox and not self.inShutdown:
            self.toolbox = NtToolbox(self.window)
            self.toolbox.updateStyleSheet()
            self.installEventFilters(self.toolbox)
            self.toolbox.pad.show()
        elif self.toolbox and not usesNuToolbox:
            self.removeEventFilters(self.toolbox)
            self.toolbox.close()
            self.toolbox = None

        if self.toolboxOptions == None and usesNuToolOptionsAlt:
            self.toolboxOptions = NtToolshelf(self.window, self.toolboxAlignment)
            self.toolboxOptions.updateStyleSheet()
            self.installEventFilters(self.toolboxOptions)
            self.toolboxOptions.pad.show()
        elif self.toolboxOptions and not usesNuToolOptionsAlt:
            self.removeEventFilters(self.toolboxOptions)
            self.toolboxOptions.close()
            self.toolboxOptions = None

        if self.toolOptions == None and usesNuToolOptions:
            self.toolOptions = NtToolshelf(self.window, self.toolOptionsAlignment, True)
            self.toolOptions.updateStyleSheet()
            self.installEventFilters(self.toolOptions)
            self.toolOptions.pad.show()
        elif self.toolOptions and not usesNuToolOptions:
            self.removeEventFilters(self.toolOptions)
            self.toolOptions.close()
            self.toolOptions = None

    def updatePadAlignments(self):
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
                self.toolbox.pad.adjustToView()
            return
        elif self.toolbox == None:
            if self.toolboxOptions:
                self.toolboxOptions.pad.offset_x_left = 0
                self.toolboxOptions.pad.offset_x_right = 0
                self.toolboxOptions.pad.adjustToView()
            return
        else:
            if self.alternativeToolboxPos:
                if self.toolboxAlignment == 'left':
                    self.toolbox.pad.offset_x_left = self.toolboxOptions.pad.width()
                    self.toolbox.pad.offset_x_right = 0
                elif self.toolboxAlignment == 'right':
                    self.toolbox.pad.offset_x_right = self.toolboxOptions.pad.width()
                    self.toolbox.pad.offset_x_left = 0

                self.toolboxOptions.pad.offset_x_right = 0
                self.toolboxOptions.pad.offset_x_left = 0
            else:
                if self.toolboxAlignment == 'left':
                    self.toolboxOptions.pad.offset_x_left = self.toolbox.pad.width()
                    self.toolboxOptions.pad.offset_x_right = 0
                elif self.toolboxAlignment == 'right':
                    self.toolboxOptions.pad.offset_x_right = self.toolbox.pad.width()
                    self.toolboxOptions.pad.offset_x_left = 0

                self.toolbox.pad.offset_x_right = 0
                self.toolbox.pad.offset_x_left = 0
            self.toolboxOptions.pad.adjustToView()

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

    def updateStyleSheet(self):
        if self.toolbox:
            self.toolbox.updateStyleSheet()
        if self.toolboxOptions:
            self.toolboxOptions.updateStyleSheet()
        if self.toolOptions:
            self.toolOptions.updateStyleSheet()


