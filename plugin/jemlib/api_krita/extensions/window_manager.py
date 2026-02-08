from typing import Union, Callable
from PyQt5.QtCore import pyqtBoundSignal, QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QButtonGroup, QAbstractButton
from jemlib.alib_vaporjem import Logger
from jemlib.api_touchify.types.ContextRequirements import ContextRequirements
from krita import ManagedColor, Resource, View, Canvas, Node, Window, Krita as KritaAPI


PYQT_SLOT = Union[Callable[..., None], pyqtBoundSignal]

class WindowNotifier(QObject):
    brushChanged=pyqtSignal(Resource)
    gradientChanged=pyqtSignal(Resource)
    patternChanged=pyqtSignal(Resource)
    toolChanged=pyqtSignal(str)
    viewChanged=pyqtSignal(View)
    canvasChanged=pyqtSignal(Canvas)
    
    selectedNodesChanged=pyqtSignal()
    selectedNodeColorsChanged=pyqtSignal()
    selectionChanged=pyqtSignal(bool)
    
    brushSizeChanged=pyqtSignal(float)
    brushOpacityChanged=pyqtSignal(float)
    brushRotationChanged=pyqtSignal(float)
    brushFlowChanged=pyqtSignal(float)

    brushBlendingModeChanged=pyqtSignal(str)
    layerBlendingModeChanged=pyqtSignal(str)

    backgroundColorChanged=pyqtSignal(ManagedColor)
    foregroundColorChanged=pyqtSignal(ManagedColor)

    requirementsContextChanged=pyqtSignal(ContextRequirements.Context)

    def __init__(self, parent: Window):
        super().__init__(parent.qwindow())
        self.native_window = parent

        self.__lastView: View = None
        self.__lastBrushPreset: Resource = None
        self.__lastCanvas: Canvas = None
        self.__lastGradient: Resource = None
        self.__lastPattern: Resource = None

        self.__lastToolboxTool: str = ""

        self.__lastBrushSize: float = 0
        self.__lastBrushOpacity: float = 0
        self.__lastBrushFlow: float = 0
        self.__lastBrushRotation: float = 0

        self.__lastBrushBlendingMode: str = ""
        self.__lastLayerBlendingMode: str = ""

        self.__lastForegroundColor: ManagedColor = None
        self.__lastBackgroundColor: ManagedColor = None

        self.__lastSelectedNodes: list[Node] = []
        self.__lastNodeColors: list[int] = []
        self.__isSelectionActive: bool = False

        qwin = self.native_window.qwindow()
        mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
        wobj = mobj.findChild(QButtonGroup)
        wobj.buttonToggled.connect(self.__onToolChanged__)

    def __onToolChanged__(self, obj: QAbstractButton):
        if obj:
            toolboxTool = obj.objectName()
            if toolboxTool != self.__lastToolboxTool:
                self.__lastToolboxTool = toolboxTool
                Logger.logDebug("JemLib","WindowManager", "unknown", "Tool Changed")
                self.toolChanged.emit(toolboxTool)
                self.__onUpdateContextRequirements__()

    def __onSlowTimerTicked__(self):
        currentView: View = None
        currentLayerBlendingMode: str = ""
        selectedNodes: list[Node] = []
        selectedNodeColors: list[int] = []
        isSelectionActive: bool = False
        updateContextRequirements: bool = False

        try:
            win = self.native_window
            if win: 
                currentView = win.activeView()
                if currentView: 
                    currentDocument = currentView.document()
                    if currentDocument:
                        isSelectionActive = currentDocument.selection() != None
                        currentNode = currentDocument.activeNode()
                        if currentNode:
                            currentLayerBlendingMode = currentNode.blendingMode()

                    selectedNodes = currentView.selectedNodes()
                    selectedNodeColors = [node.colorLabel() for node in currentView.selectedNodes() ]
        except Exception as e:
            Logger.logDebug("JemLib", "WindowManager", "__onSlowTimerTicked__", "Failed to Run Checks: " + str(e))

        if currentView != self.__lastView:
            Logger.logDebug("JemLib","WindowManager", "__onSlowTimerTicked__", "View Changed")
            self.viewChanged.emit(currentView)
            self.__lastView = currentView

        if selectedNodes != self.__lastSelectedNodes:
            Logger.logDebug("JemLib","WindowManager", "__onSlowTimerTicked__", "Selected Nodes Changed")
            self.selectedNodesChanged.emit()
            self.__lastSelectedNodes = selectedNodes

        if selectedNodeColors != self.__lastNodeColors:
            Logger.logDebug("JemLib","WindowManager", "__onSlowTimerTicked__", "Selected Node Colors Changed")
            self.selectedNodeColorsChanged.emit()
            self.__lastNodeColors = selectedNodeColors

        if currentLayerBlendingMode != self.__lastLayerBlendingMode:
            Logger.logDebug("JemLib","WindowManager", "__onSlowTimerTicked__", "Layer Blending Mode Changed")
            self.layerBlendingModeChanged.emit(currentLayerBlendingMode)
            self.__lastLayerBlendingMode = currentLayerBlendingMode

        if isSelectionActive != self.__isSelectionActive:
            Logger.logDebug("JemLib","WindowManager", "__onSlowTimerTicked__", "Selection Changed")
            self.selectionChanged.emit(isSelectionActive)
            updateContextRequirements = True
            self.__isSelectionActive = isSelectionActive

        if updateContextRequirements:
            self.__onUpdateContextRequirements__()

    def __onQuickTimerTicked__(self):
        currentBrush: Resource = None
        currentGradient: Resource = None
        currentPattern: Resource = None
        currentCanvas: Canvas = None
        currentBrushBlendingMode: str = ""
        currentSize: float = 0
        currentOpacity: float = 0
        currentFlow: float = 0
        currentRotation: float = 0
        currentForegroundColor: ManagedColor = None
        currentBackgroundColor: ManagedColor = None
        updateContextRequirements: bool = False


        if self.__lastView:
            currentGradient = self.__lastView.currentGradient()
            currentPattern = self.__lastView.currentPattern()
            currentBrush = self.__lastView.currentBrushPreset()
            currentSize = self.__lastView.brushSize()
            currentOpacity = self.__lastView.paintingOpacity()
            currentFlow = self.__lastView.paintingFlow()
            currentRotation = self.__lastView.brushRotation()
            currentBrushBlendingMode = self.__lastView.currentBlendingMode()
            currentCanvas = self.__lastView.canvas()
            currentForegroundColor = self.__lastView.foregroundColor()
            currentBackgroundColor = self.__lastView.backgroundColor()

        if currentGradient != self.__lastGradient:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Selected Gradient Changed")
            self.gradientChanged.emit(currentGradient)
            self.__lastGradient = currentGradient

        if currentPattern != self.__lastPattern:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Selected Pattern Changed")
            self.patternChanged.emit(currentPattern)
            self.__lastPattern = currentPattern

        if currentCanvas != self.__lastCanvas:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Canvas Changed")
            self.canvasChanged.emit(currentCanvas)
            self.__lastCanvas = currentCanvas

        if currentBrushBlendingMode != self.__lastBrushBlendingMode:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Blending Mode Changed")
            self.brushBlendingModeChanged.emit(currentBrushBlendingMode)
            self.__lastBrushBlendingMode = currentBrushBlendingMode

        if currentForegroundColor != self.__lastForegroundColor:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Foreground Color Changed")
            self.foregroundColorChanged.emit(currentForegroundColor)
            self.__lastForegroundColor = currentForegroundColor

        if currentBackgroundColor != self.__lastBackgroundColor:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Background Color Changed")
            self.backgroundColorChanged.emit(currentBackgroundColor)
            self.__lastBackgroundColor = currentBackgroundColor
        
        if currentSize != self.__lastBrushSize:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Size Changed")
            self.brushSizeChanged.emit(currentSize)
            self.__lastBrushSize = currentSize

        if currentFlow != self.__lastBrushFlow:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Flow Changed")
            self.brushFlowChanged.emit(currentFlow)
            self.__lastBrushFlow = currentFlow

        if currentOpacity != self.__lastBrushOpacity:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Opacity Changed")
            self.brushOpacityChanged.emit(currentOpacity)
            self.__lastBrushOpacity = currentOpacity

        if currentRotation != self.__lastBrushRotation:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Rotation Changed")
            self.brushRotationChanged.emit(currentRotation)
            self.__lastBrushRotation = currentRotation

        if currentBrush != self.__lastBrushPreset:
            Logger.logDebug("JemLib","WindowManager", "__onTimerTicked__", "Brush Changed")
            self.brushChanged.emit(currentBrush)
            self.__lastBrushPreset = currentBrush

        if updateContextRequirements:
            self.__onUpdateContextRequirements__()

    def __onUpdateContextRequirements__(self):
        context = self.getRequirementsContext()
        self.requirementsContextChanged.emit(context)

    def getRequirementsContext(self):
        return ContextRequirements.Context(
            current_tool=self.__lastToolboxTool,
            selection_active=self.__isSelectionActive
        )

    def getCurrentGradient(self):
        return self.__lastGradient
    
    def getCurrentPattern(self):
        return self.__lastPattern

    def getCurrentView(self):
        return self.__lastView

    def getCurrentTool(self):
        return self.__lastToolboxTool

    def getBrushBlendingMode(self):
        return self.__lastBrushBlendingMode
    
    def getLayerBlendingMode(self):
        return self.__lastLayerBlendingMode

    def getCurrentCanvas(self):
        return self.__lastCanvas
    
    def getCurrentBrush(self):
        return self.__lastBrushPreset
    
    def getCurrentBrushName(self):
        result = self.getCurrentBrush()
        if not result: return None
        else: return result.name()

    def getBrushSize(self):
        return self.__lastBrushSize
    
    def getBrushOpacity(self):
        return self.__lastBrushOpacity
    
    def getBrushFlow(self):
        return self.__lastBrushFlow
    
    def getBrushRotation(self):
        return self.__lastBrushRotation

    def getCanvasColor(self, is_background: bool = False):
        if is_background: return self.__lastBackgroundColor
        else: return self.__lastForegroundColor


    def isAlive(self) -> bool:
        """Return False if the action was deleted by C++"""
        try:
            self.parent()
        except RuntimeError:
            return False
        return True

class WindowManager(QObject):
    def __init__(self) -> None:
        super().__init__(KritaAPI.instance())
        self.window_notifiers: list[WindowNotifier] = []

        self.instance = KritaAPI.instance()
        self.instance.notifier().windowCreated.connect(self.onWindowCreated)

        self.__quick_notify_timer = QTimer(self)
        self.__quick_notify_timer.start(50)

        self.__slow_notify_timer = QTimer(self)
        self.__slow_notify_timer.start(250)

    def onWindowCreated(self):
        self.reloadNotifiers()

    def reloadNotifiers(self):
        for notifier in reversed(self.window_notifiers):
            if not notifier.isAlive(): self.window_notifiers.remove(notifier)

        for __window in self.instance.windows(): 
            qt_window = __window.qwindow()
            if qt_window.property("KRITA_NOTIFIER_EXT_LOADED") != True:
                new_notifier = WindowNotifier(__window)
                self.window_notifiers.append(new_notifier)
                self.__quick_notify_timer.timeout.connect(new_notifier.__onQuickTimerTicked__)
                self.__slow_notify_timer.timeout.connect(new_notifier.__onSlowTimerTicked__)
                qt_window.setProperty("KRITA_NOTIFIER_EXT_LOADED", True)
