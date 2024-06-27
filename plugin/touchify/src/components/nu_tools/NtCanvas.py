from PyQt5.QtWidgets import QMdiArea, QDockWidget
from .NtToolbox import NtToolbox
from .NtToolOptions import NtToolOptions
from ...config import InternalConfig
from krita import *
from PyQt5.QtCore import QObject, QEvent, QPoint
from ...variables import *

class NtCanvas():
    def __init__(self, window: Window):
        #super(NtCanvas, self).__init__(window.qwindow())
        self.window = window

        self.toolboxAlignment = self.getToolboxAlignment()
        self.toolOptionsAlignment = self.getToolOptionsAlignment()
        self.alternativeToolboxPos = self.getToolboxAltPositionState()

        self.toolbox = None
        self.toolboxOptions = None
        self.toolOptions = None

        self.updateElements()
        self.updatePadAlignments()
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
        isToolboxOnRight = InternalConfig.instance().nuOptions_ToolboxOnRight
        return 'left' if isToolboxOnRight else 'right'

    def getToolboxAlignment(self):
        isToolboxOnRight = InternalConfig.instance().nuOptions_ToolboxOnRight
        return 'right' if isToolboxOnRight else 'left'
    
    def getToolboxAltPositionState(self):
        return InternalConfig.instance().nuOptions_AlternativeToolboxPosition
    #endregion

    #region Update Functions

    def updateElements(self):
        usesNuToolbox = InternalConfig.instance().usesNuToolbox
        usesNuToolboxOptions = InternalConfig.instance().usesNuToolbox
        usesNuToolOptions = InternalConfig.instance().usesNuToolOptions

        if self.toolbox == None and usesNuToolbox:
            self.toolbox = NtToolbox(self.window)
            self.toolbox.updateStyleSheet()
            self.installEventFilters(self.toolbox)
            self.toolbox.pad.show()
        elif self.toolbox and not usesNuToolbox:
            self.removeEventFilters(self.toolbox)
            self.toolbox.close()
            self.toolbox = None

        if self.toolboxOptions == None and usesNuToolboxOptions:
            self.toolboxOptions = NtToolOptions(self.window, self.toolboxAlignment)
            self.toolboxOptions.updateStyleSheet()
            self.installEventFilters(self.toolboxOptions)
            self.toolboxOptions.pad.show()
        elif self.toolboxOptions and not usesNuToolboxOptions:
            self.removeEventFilters(self.toolboxOptions)
            self.toolboxOptions.close()
            self.toolboxOptions = None

        if self.toolOptions == None and usesNuToolOptions:
            self.toolOptions = NtToolOptions(self.window, self.toolOptionsAlignment, True)
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

    def installEventFilters(self, widget: NtToolOptions | NtToolbox):
        widget.pad.btnHide.clicked.connect(self.updateCanvas)
        #widget.pad.installEventFilter(self)
        #self.qWin.installEventFilter(self)

    def removeEventFilters(self, widget: NtToolOptions | NtToolbox):
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


