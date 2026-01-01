from typing import Union, Callable
from PyQt5.QtCore import pyqtBoundSignal, QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QButtonGroup, QAbstractButton
from jemlib.alib_vaporjem import Logger
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
    
    brushSizeChanged=pyqtSignal(float)
    brushOpacityChanged=pyqtSignal(float)
    brushRotationChanged=pyqtSignal(float)
    brushFlowChanged=pyqtSignal(float)

    brushBlendingModeChanged=pyqtSignal(str)
    layerBlendingModeChanged=pyqtSignal(str)

    backgroundColorChanged=pyqtSignal(ManagedColor)
    foregroundColorChanged=pyqtSignal(ManagedColor)

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

        qwin = self.native_window.qwindow()
        mobj = next((w for w in qwin.findChildren(QWidget) if w.metaObject().className() == 'KoToolBox'), None)
        wobj = mobj.findChild(QButtonGroup)
        wobj.buttonToggled.connect(self.__onToolChanged__)

    def __onToolChanged__(self, obj: QAbstractButton):
        if obj:
            toolboxTool = obj.objectName()
            if toolboxTool != self.__lastToolboxTool:
                self.__lastToolboxTool = toolboxTool
                Logger.debug("JemLib", "WindowManager", "Tool Changed")
                self.toolChanged.emit(toolboxTool)

    def __onTimerTicked__(self):
        currentBrush: Resource = None
        currentGradient: Resource = None
        currentPattern: Resource = None
        currentView: View = None
        currentCanvas: Canvas = None

        currentBrushBlendingMode: str = ""
        currentLayerBlendingMode: str = ""

        currentSize: float = 0
        currentOpacity: float = 0
        currentFlow: float = 0
        currentRotation: float = 0

        currentForegroundColor: ManagedColor = None
        currentBackgroundColor: ManagedColor = None

        selectedNodes: list[Node] = []
        selectedNodeColors: list[int] = []

        try:
            win = self.native_window
            if win: 
                currentView = win.activeView()
                if currentView: 
                    currentDocument = currentView.document()
                    if currentDocument:
                        currentNode = currentDocument.activeNode()
                        if currentNode:
                            currentLayerBlendingMode = currentNode.blendingMode()

                    selectedNodes = currentView.selectedNodes()
                    selectedNodeColors = [node.colorLabel() for node in currentView.selectedNodes() ]

                    currentGradient = currentView.currentGradient()
                    currentPattern = currentView.currentPattern()
                    currentBrush = currentView.currentBrushPreset()
                    currentSize = currentView.brushSize()
                    currentOpacity = currentView.paintingOpacity()
                    currentFlow = currentView.paintingFlow()
                    currentRotation = currentView.brushRotation()
                    currentBrushBlendingMode = currentView.currentBlendingMode()
                    
                    currentCanvas = currentView.canvas()

                    currentForegroundColor = currentView.foregroundColor()
                    currentBackgroundColor = currentView.backgroundColor()
        except Exception as e:
            Logger.debug("JemLib", "WindowManager", "Failed to Run Checks: " + str(e))

        if currentGradient != self.__lastGradient:
            Logger.debug("JemLib", "WindowManager", "Selected Gradient Changed")
            self.gradientChanged.emit(currentGradient)
            self.__lastGradient = currentGradient

        if currentPattern != self.__lastPattern:
            Logger.debug("JemLib", "WindowManager", "Selected Pattern Changed")
            self.patternChanged.emit(currentPattern)
            self.__lastPattern = currentPattern

        if currentCanvas != self.__lastCanvas:
            Logger.debug("JemLib", "WindowManager", "Canvas Changed")
            self.canvasChanged.emit(currentCanvas)
            self.__lastCanvas = currentCanvas

        if currentView != self.__lastView:
            Logger.debug("JemLib", "WindowManager", "View Changed")
            self.viewChanged.emit(currentView)
            self.__lastView = currentView

        if selectedNodes != self.__lastSelectedNodes:
            Logger.debug("JemLib", "WindowManager", "Selected Nodes Changed")
            self.selectedNodesChanged.emit()
            self.__lastSelectedNodes = selectedNodes

        if selectedNodeColors != self.__lastNodeColors:
            Logger.debug("JemLib", "WindowManager", "Selected Node Colors Changed")
            self.selectedNodeColorsChanged.emit()
            self.__lastNodeColors = selectedNodeColors

        if currentLayerBlendingMode != self.__lastLayerBlendingMode:
            Logger.debug("JemLib", "WindowManager", "Layer Blending Mode Changed")
            self.layerBlendingModeChanged.emit(currentLayerBlendingMode)
            self.__lastLayerBlendingMode = currentLayerBlendingMode

        if currentBrushBlendingMode != self.__lastBrushBlendingMode:
            Logger.debug("JemLib", "WindowManager", "Brush Blending Mode Changed")
            self.brushBlendingModeChanged.emit(currentBrushBlendingMode)
            self.__lastBrushBlendingMode = currentBrushBlendingMode

        if currentForegroundColor != self.__lastForegroundColor:
            Logger.debug("JemLib", "WindowManager", "Foreground Color Changed")
            self.foregroundColorChanged.emit(currentForegroundColor)
            self.__lastForegroundColor = currentForegroundColor

        if currentBackgroundColor != self.__lastBackgroundColor:
            Logger.debug("JemLib", "WindowManager", "Background Color Changed")
            self.backgroundColorChanged.emit(currentBackgroundColor)
            self.__lastBackgroundColor = currentBackgroundColor
        
        if currentSize != self.__lastBrushSize:
            Logger.debug("JemLib", "WindowManager", "Brush Size Changed")
            self.brushSizeChanged.emit(currentSize)
            self.__lastBrushSize = currentSize

        if currentFlow != self.__lastBrushFlow:
            Logger.debug("JemLib", "WindowManager", "Brush Flow Changed")
            self.brushFlowChanged.emit(currentFlow)
            self.__lastBrushFlow = currentFlow

        if currentOpacity != self.__lastBrushOpacity:
            Logger.debug("JemLib", "WindowManager", "Brush Opacity Changed")
            self.brushOpacityChanged.emit(currentOpacity)
            self.__lastBrushOpacity = currentOpacity

        if currentRotation != self.__lastBrushRotation:
            Logger.debug("JemLib", "WindowManager", "Brush Rotation Changed")
            self.brushRotationChanged.emit(currentRotation)
            self.__lastBrushRotation = currentRotation

        if currentBrush != self.__lastBrushPreset:
            Logger.debug("JemLib", "WindowManager", "Brush Changed")
            self.brushChanged.emit(currentBrush)
            self.__lastBrushPreset = currentBrush


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

        self.notify_timer = QTimer(self)
        self.notify_timer.start(250)

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
                self.notify_timer.timeout.connect(new_notifier.__onTimerTicked__)
                qt_window.setProperty("KRITA_NOTIFIER_EXT_LOADED", True)
