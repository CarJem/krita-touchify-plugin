from dataclasses import dataclass
import dataclasses
from typing import Any, Optional
from enum import IntEnum


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from jemlib.alib_vaporjem import Logger
from krita import *
from touchify_sub_view.SubViewSettings import SubViewSettings


class SubViewViewport(QWidget):

    #region Enums

    class ScalingMode(IntEnum):
        Smooth=1
        Fast=2

    class FitSetting(IntEnum):
        FitToNavigator=1

    #endregion

    #region Sub Classes

    @dataclass
    class Viewstate:
        flip_h: Optional[bool] = False
        flip_v: Optional[bool] = False
        rotation: Optional[float] = 0
        zoom: Optional[float] = 100.0
        x: Optional[float] = 0
        y: Optional[float] = 0
        width: Optional[float] = 0
        height: Optional[float] = 0

        @classmethod
        def from_dict(cls, env):      
            return cls(**{
                k: v for k, v in env.items() 
                if k in inspect.signature(cls).parameters
            })
        
    class Container(QGraphicsView):
        ''' Custom class for a hacky way to make sure input events are sent to the right place'''
    
        def __init__(self, parent: "SubViewViewport" = None):
            super().__init__(parent)
            self._panMode = True
            self._canSave = False

            self.setContentsMargins(0,0,0,0)

            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.setInteractive(False) # Disabling interactive mode prevents it from taking the drop events

            self.horizontalScrollBar().valueChanged.connect(self.onViewportPositionChanged)
            self.verticalScrollBar().valueChanged.connect(self.onViewportPositionChanged)

            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
            self.grabGesture(Qt.GestureType.PinchGesture)

        #region Overrides

        def parent(self) -> "SubViewViewport":
            return super().parent()
            
        #endregion

        #region Events

        def event(self, event: QEvent):
            if event.type() == QEvent.Type.Gesture:
                return self.gestureEvent(event)
            return super().event(event)
 
        def gestureEvent(self, event: QGestureEvent):
            
            pinch = event.gesture(Qt.GestureType.PinchGesture)
            pan = event.gesture(Qt.GestureType.PanGesture)
            
            if isinstance(pan, QPinchGesture):
                pass
            elif isinstance(pinch, QPinchGesture):
                change_flags = pinch.changeFlags()

                if change_flags & QPinchGesture.ChangeFlag.ScaleFactorChanged:
                    scale_factor = pinch.scaleFactor()

                    if scale_factor > 1.0: zoom_factor = 1
                    elif scale_factor < 1.0: zoom_factor = -1
                    else: zoom_factor = 0

                    self.parent().zoomBy(factor=(zoom_factor * 0.5))
                    
                if change_flags & QPinchGesture.ChangeFlag.RotationAngleChanged:
                    rotation_angle = pinch.lastRotationAngle() - pinch.rotationAngle()

                    if rotation_angle < 0.0: rotation_factor = 1
                    elif rotation_angle > 0.0: rotation_factor = -1
                    else: rotation_factor = 0

                    self.parent().rotateBy(factor=(rotation_factor * 0.5))

                # Trigger a repaint
                self.update() 
                # Accept the gesture to stop propagation to other widgets
                event.setAccepted(True)
                return True
            return False

        def wheelEvent(self, event: QWheelEvent):
            delta_y = event.angleDelta().y()

            if delta_y > 0:
                self.parent().zoomIn(event.pos())
            elif delta_y < 0:
                self.parent().zoomOut(event.pos())
            else:
                pass

        def keyReleaseEvent(self, event):
            self.parent().keyReleaseEvent(event)
            super().keyReleaseEvent(event)
        
        def mouseMoveEvent(self, event):
            self.parent().mouseMoveEvent(event)
            super().mouseMoveEvent(event)

        def mousePressEvent(self, event):
            self.parent().mousePressEvent(event)
            super().mousePressEvent(event)
        
        def mouseReleaseEvent(self, event):
            self.parent().mouseReleaseEvent(event)
            super().mouseReleaseEvent(event)

        #endregion

        #region Adjustment Functions

        def fitToNavigator(self):
            self.moveTo(self.scene().itemsBoundingRect().center())

        def moveTo(self, pos: QPointF):
            width = self.viewport().width()
            height = self.viewport().height()
            viewPoint: QPointF = self.transform().map(pos)

            if self.isRightToLeft():
                horizontal = 0
                horizontal += self.horizontalScrollBar().minimum()
                horizontal += self.horizontalScrollBar().maximum()
                horizontal -= int(viewPoint.x() - width / 2.0)
                self.horizontalScrollBar().setValue(horizontal)
            else:
                self.horizontalScrollBar().setValue(int(viewPoint.x() - width / 2.0))
            
            self.verticalScrollBar().setValue(int(viewPoint.y() - height / 2.0))

        #endregion

        #region Get / Set Functions

        def getPanMode(self):
            return self._panMode

        def setPanMode(self, enable: bool):
            if self._panMode != enable:
                self._panMode = enable
                if enable: self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                else: self.setDragMode(QGraphicsView.DragMode.NoDrag)
            
        def getColorAt(self, pos):
            pixmap = self.grab(self.viewport().rect())
            image = pixmap.toImage()
            if image.valid(pos):
                pixel_value = image.pixel(pos)
                color = QColor(pixel_value)
                return color
            else:
                # Return a default color if the position is out of bounds
                return None

        def getPostion(self):
            #Get the center point of the viewport in view coordinates (integers)
            viewportCenter = QPoint(int(self.viewport().width() / 2), int(self.viewport().height() / 2))
            #Map this point to the scene coordinates (floating point)
            sceneCenter = self.mapToScene(viewportCenter)
            return sceneCenter

        def setPosition(self, target: QPointF):
            self.moveTo(target)

        #endregion

        #region Signal Recievers

        def onViewportPositionChanged(self, value: int):
            self.parent().refreshState()

        #endregion

    class Controller(QObject):

        class Mode(IntEnum):
            Pan=1
            Rotate=2
            Zoom=3
            ZoomIn=4
            ZoomOut=5
            ColorSampling=6
            ManualPan=7

        class Style(IntEnum):
            Original=1
            ClipStudio=2

        sigColorSamplerTargetPicked=pyqtSignal(QPoint)
        sigModeChanged=pyqtSignal(Mode, bool)

        def __init__(self, parent: QWidget):
            super().__init__(parent)

            self.__parent: SubViewViewport = parent

            self.__isZooming = False
            self.__isZoomingOut = False
            self.__isZoomingIn = False
            self.__isPanning = False
            self.__isManualPanning = False
            self.__isRotating = False
            self.__isColorSampling = False

            self.__canPassivelyPan = False
            self.__mousePressed = None
            self.__mouseLastPosition: QPoint | None = None


            self.setControlStyle(self.Style.ClipStudio)

        def enable(self, option: Mode):
            self.set(option, True)

        def disable(self, option: Mode):
            self.set(option, False)

        def get(self, option: Mode):
            match option:
                case self.Mode.Zoom:
                    return self.__isZooming
                case self.Mode.ZoomIn:
                    return self.__isZoomingIn
                case self.Mode.ZoomOut:
                    return self.__isZoomingOut
                case self.Mode.Pan:
                    return self.__isPanning
                case self.Mode.Rotate:
                    return self.__isRotating
                case self.Mode.ColorSampling:
                    return self.__isColorSampling
                case self.Mode.ManualPan:
                    return self.__isManualPanning
                case _:
                    return False

        def set(self, option: Mode, state: bool):
            update = False
            match option:
                case self.Mode.Zoom:
                    if state != self.__isZooming: 
                        self.__isZooming = state
                        #print(f"Zooming: {self.__isZooming}")
                        update = True
                case self.Mode.ZoomIn:
                    if state != self.__isZoomingIn: 
                        self.__isZoomingIn = state
                        #print(f"Zooming In: {self.__isZoomingIn}")
                        update = True
                case self.Mode.ZoomOut:
                    if state != self.__isZoomingOut: 
                        self.__isZoomingOut = state
                        #print(f"Zooming Out: {self.__isZoomingOut}")
                        update = True
                case self.Mode.Pan:
                    if state != self.__isPanning: 
                        self.__isPanning = state
                        #print(f"Panning: {self.__isPanning}")
                        update = True
                case self.Mode.Rotate:
                    if state != self.__isRotating: 
                        self.__isRotating = state
                        #print(f"Rotating: {self.__isRotating}")
                        update = True
                case self.Mode.ColorSampling:
                    if state != self.__isColorSampling: 
                        self.__isColorSampling = state
                        #print(f"Color Sampling: {self.__isColorSampling}")
                        update = True
                case self.Mode.ManualPan:
                    if state != self.__isManualPanning: 
                        self.__isManualPanning = state
                        #print(f"Manual Panning: {self.__isManualPanning}")
                        update = True

            if update:
                self.onStateChanged()
                self.sigModeChanged.emit(option, state)

        def setControlStyle(self, style: Style):
            self.__controlStyle = style

            match style:
                case self.Style.ClipStudio:
                    self.__canPassivelyPan = True
                case self.Style.Original:
                    self.__canPassivelyPan = False
                case _:
                    self.__canPassivelyPan = False

            self.onStateChanged()
                
        def onStateChanged(self):
            if self.__isManualPanning:
                self.__parent.unsetCursor()
                self.__parent.viewport.setPanMode(True)
            elif self.__isColorSampling:
                self.__parent.setCursor(QCursor(Krita.instance().icon('tool_color_picker_cursor').pixmap(32,32),0,0))
                self.__parent.viewport.setPanMode(False)
            elif self.__isRotating:
                self.__parent.setCursor(QCursor(Krita.instance().icon('cursor_rotate').pixmap(32,32),0,0))
                self.__parent.viewport.setPanMode(False)
            elif self.__isZooming:
                self.__parent.setCursor(QCursor(Krita.instance().icon('zoom_in_cursor').pixmap(32,32),0,0))
                self.__parent.viewport.setPanMode(False)
            elif self.__isZoomingOut:
                self.__parent.setCursor(QCursor(Krita.instance().icon('zoom_out_cursor').pixmap(32,32),0,0))
                self.__parent.viewport.setPanMode(False)
            elif self.__isZoomingIn:
                self.__parent.setCursor(QCursor(Krita.instance().icon('zoom_in_cursor').pixmap(32,32),0,0))
                self.__parent.viewport.setPanMode(False)
            elif self.__isPanning:
                self.__parent.unsetCursor()
                self.__parent.viewport.setPanMode(True)
            elif self.__canPassivelyPan:
                self.__parent.unsetCursor()
                self.__parent.viewport.setPanMode(True)
            else:
                self.__parent.unsetCursor()
                self.__parent.viewport.setPanMode(False)

        def onMouseChanged(self, event: QMouseEvent, isPressed: bool):
            match self.__controlStyle:
                case self.Style.ClipStudio:
                    if not isPressed:
                        if self.get(self.Mode.ZoomOut):
                            self.__parent.zoomOut()
                        elif self.get(self.Mode.ZoomIn):
                            self.__parent.zoomIn()    
                        self.__mouseLastPosition = None
                case self.Style.Original:
                    if not isPressed:
                        self.disable(self.Mode.ColorSampling)
                        self.__mouseLastPosition = None

            self.__mousePressed = isPressed
        
        def onMouseMoved(self, event: QMouseEvent):
            
            if self.__mouseLastPosition != None and self.__mousePressed:
                mouseDelta = event.pos() - self.__mouseLastPosition
            else:
                mouseDelta = QPoint(0,0)

            if self.get(self.Mode.ManualPan):
                pass
            elif self.get(self.Mode.Rotate):
                self.__parent.rotateBy(pos=mouseDelta)
            elif self.get(self.Mode.Zoom):
                if mouseDelta.y() < 0:
                    self.__parent.zoomOut(event.pos())
                elif mouseDelta.y() > 0:
                    self.__parent.zoomIn(event.pos())
            elif self.get(self.Mode.ColorSampling):
                self.sigColorSamplerTargetPicked.emit(event.pos())
            elif self.get(self.Mode.Pan):
                pass

                    
            self.__mouseLastPosition = event.pos()

        def onKeyChanged(self, event: QKeyEvent, isPressed: bool):
            if event.isAutoRepeat():
                return

            match self.__controlStyle:
                case self.Style.ClipStudio:
                    #region Rotate
                    if event.key() == Qt.Key.Key_Shift: 
                        self.set(self.Mode.Rotate, isPressed)               
                    #endregion
                    #region Zoom In / Zoom Out
                    elif event.key() == Qt.Key.Key_Control or event.key() == Qt.Key.Key_Alt: 
                        is_ctrl = event.key() == Qt.Key.Key_Control
                        is_alt = event.key() == Qt.Key.Key_Alt

                        if is_ctrl and isPressed:
                            self.set(self.Mode.ZoomIn, True)
                            self.set(self.Mode.ZoomOut, False)
                        elif is_ctrl and not isPressed:
                            self.set(self.Mode.ZoomIn, False)
                            self.set(self.Mode.ZoomOut, False)
                        elif is_alt and isPressed and self.get(self.Mode.ZoomIn):
                            self.set(self.Mode.ZoomOut, True)
                        elif is_alt and not isPressed:
                            self.set(self.Mode.ZoomOut, False)
                    #endregion
                    #region Pan
                    elif event.key() == Qt.Key.Key_Space: 
                        self.set(self.Mode.ManualPan, isPressed)
                    #endregion
                case self.Style.Original:
                    if event.key() == Qt.Key.Key_Space:
                        #region Pan
                        if event.modifiers() == Qt.KeyboardModifier.NoModifier: 
                            self.set(self.Mode.Pan, isPressed)
                        #endregion
                        #region Rotate
                        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier: 
                            self.set(self.Mode.Rotate, isPressed)
                        #endregion
                        #region Zoom
                        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier: 
                            self.set(self.Mode.Zoom, isPressed)
                        #endregion

    #endregion

    #region Signals

    sigViewerStateChanged = pyqtSignal()
    sigViewerRequestedSave = pyqtSignal()

    #endregion

    #region Constructors

    def __init__(self, parent=None, flags=None):
        super().__init__(parent)

        self.__zoomIncrements = [
            0.8,
            1.6,
            2.1,
            3.1,
            4.2,
            6.2,
            8.3,
            12.6,
            16.7,
            25.0,
            33.3,
            50.0,
            75.0,
            100.0,
            150.0,
            200.0,
            300.0,
            400.0,
            500.0,
            600.0,
            800.0,
            1000.0,
            1200.0,
            1600.0,
            2400.0,
            3200.0
        ]

        self._scalingMode = self.ScalingMode.Fast
        self._zoomValue: float = 1
        self._rotateValue: float = 0
        self._fitSetting = SubViewViewport.FitSetting.FitToNavigator
        self._flipVertical = False
        self._flipHorizontal = False
        self._imageLoaded = False
        self._blockUpdates = True

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.state_timer = QTimer(self)
        self.state_timer.setInterval(100)
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(self.syncState)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.viewport = self.Container(self)
        layout.addWidget(self.viewport)
        self.viewport.setVisible(True)

        self.scene = QGraphicsScene()
        self.viewport.setScene(self.scene)

        self.imageItem = QGraphicsPixmapItem()
        self.scene.addItem(self.imageItem)
        
        self.setBackgroundColor(qApp.palette().window().color())

        self.controller = self.Controller(self)
        self.controller.sigColorSamplerTargetPicked.connect(self.onColorSamplerTargetPicked)
        self.controller.sigModeChanged.connect(self.onControllerModeChanged)

    #endregion

    #region Properties

    @property
    def zoomIncrements(self):
        return [tuple([x, f"{str(x)}%"]) for x in self.__zoomIncrements]

    #endregion

    #region State Update Functions

    def blockUpdates(self, state: bool):
        self._blockUpdates = state

    def refreshState(self, allowUI=False):
        if not self._blockUpdates: 
            self.state_timer.start()
            self.sigViewerStateChanged.emit()
        elif allowUI:
            self.sigViewerStateChanged.emit()

    def syncState(self):
        self.sigViewerRequestedSave.emit()

    def restoreState(self, input: dict[str, Any]):
        try:
            state = self.Viewstate.from_dict(input)
            self.setFlipHorizontal(state.flip_h)
            self.reloadTransforms(True)
            self.setFlipVertical(state.flip_v)
            self.reloadTransforms(True)
            self.setRotation(state.rotation)
            self.reloadTransforms(True)
            self.setZoom(state.zoom)
            self.reloadTransforms(True)
            self.viewport.setPosition(QPointF(state.x, state.y))
            self.reloadTransforms(True)
        except:
            self.reloadTransforms(True)
            self.fitToNavigator()

    def saveState(self):
        if self._blockUpdates: return None
        
        pos = self.viewport.getPostion()
        return dataclasses.asdict(self.Viewstate(
            flip_h=self.getFlipHorizontal(),
            flip_v=self.getFlipVertical(),
            rotation=self.getRotation(),
            zoom=self.getZoom(),
            x=pos.x(),
            y=pos.y()
        ))

    #endregion

    #region Adjustment Functions

    def zoomIn(self, pos: QPoint = None):
        max_index = len(self.__zoomIncrements) - 1
        currentValue = self.getZoom()
        nearest_index, nearest_value = min(enumerate(self.__zoomIncrements), key=lambda x: abs(currentValue - x[1]))
        new_index = nearest_index + 1
        if new_index > max_index: new_index = max_index
        self.setZoom(self.__zoomIncrements[new_index])

    def zoomOut(self, pos: QPoint = None):
        currentValue = self.getZoom()
        nearest_index, nearest_value = min(enumerate(self.__zoomIncrements), key=lambda x: abs(currentValue - x[1]))
        new_index = nearest_index - 1
        if new_index < 0: new_index = 0
        self.setZoom(self.__zoomIncrements[new_index])

    def zoomBy(self, pos: QPoint | QPointF | None = None, factor: float | None = None):
        currentZoom = self.getZoom()
        if pos:
            zoomX = pos.x()
            zoomY = pos.y()
            # Inverted: Mouse up/left zooms in, down/right zooms out
            self.setZoom(currentZoom - int(zoomX + zoomY))
        elif factor:
            self.setZoom(currentZoom + factor)
        else:
            return
        

    def rotateBy(self, pos: QPoint | QPointF | None = None, factor: float | None = None):
        if pos:
            deltaX = pos.x()
            deltaY = pos.y()
        elif factor:
            deltaX = factor
            deltaY = 0
        else:
            return
        
        currentRotation = self.getRotation()
        # From 90 to 270, increasing = left instead of right
        if 90 <= currentRotation < 270:
            deltaX *= -1
        # From 180 to 360, increasing = up instead of down
        if 180 <= currentRotation < 360:
            deltaY *= -1
        self.setRotation(currentRotation + deltaX + deltaY)
    
    def fitToNavigator(self):
        self.viewport.fitToNavigator()

    #endregion
        
    #region Transform Functions

    def reloadSceneRect(self):
        # Canvas Space
        viewport_tl: QPointF = self.viewport.mapToScene(self.viewport.frameRect().topLeft())
        viewport_br: QPointF = self.viewport.mapToScene(self.viewport.frameRect().bottomRight())
        pre_viewport_rect: QRectF = QRectF(viewport_tl, viewport_br)

        if self.getFlipHorizontal():
            left = pre_viewport_rect.right()
            right = pre_viewport_rect.left()
        else:
            left = pre_viewport_rect.left()
            right = pre_viewport_rect.right()

        if self.getFlipVertical():
            top = pre_viewport_rect.bottom()
            bottom = pre_viewport_rect.top()
        else:
            top = pre_viewport_rect.top()
            bottom = pre_viewport_rect.bottom()
            
        viewport_rect = QRectF(QPointF(left, top), QPointF(right, bottom))
        image_rect = self.imageItem.boundingRect()
        Logger.debug("TouchifySubView", "SubViewViewport", f"ViewportRect: {str(viewport_rect)}")
        Logger.debug("TouchifySubView", "SubViewViewport", f"ImageRect: {str(image_rect)}")
        
        canvas_rect = image_rect.marginsAdded(QMarginsF(viewport_rect.width(), viewport_rect.height(), viewport_rect.width(), viewport_rect.height()))
        self.viewport.setSceneRect(canvas_rect)
            
    def reloadTransforms(self, force=False):
        if self._blockUpdates == True:
            if not force: return

        self.reloadSceneRect()

        scale = self.getZoom() / 100

        # Scaling Mode
        match self.getScalingMode():
            case self.ScalingMode.Fast:
                self.imageItem.setTransformationMode(Qt.TransformationMode.FastTransformation)
            case self.ScalingMode.Smooth:
                self.imageItem.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

        # Reset Transforms
        self.viewport.resetTransform()
        viewport_transform = self.viewport.transform()

        # Rotation
        self.imageItem.setTransformOriginPoint(self.imageItem.boundingRect().center())
        self.imageItem.setRotation(self.getRotation())

        # Flip Horizontal / Flip Vertical
        if self.getFlipHorizontal():
            viewport_transform = self.viewport.transform() * QTransform().scale(-1, 1)
        if self.getFlipVertical():
            viewport_transform = self.viewport.transform() * QTransform().scale(1, -1)

        # Zoom
        viewport_transform.scale(scale, scale)
        self.viewport.setTransform(viewport_transform)
    
    #endregion

    #region Events

    def resizeEvent(self, a0):
        self.reloadSceneRect()
        return super().resizeEvent(a0)
    
    def keyPressEvent(self, event: QKeyEvent):
        self.controller.onKeyChanged(event, True)

    def keyReleaseEvent(self, event: QKeyEvent):
        self.controller.onKeyChanged(event, False)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.controller.onMouseMoved(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.controller.onMouseChanged(event, True)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.controller.onMouseChanged(event, False)
    
    #endregion
    
    #region Get / Set

    def getZoom(self) -> float:
        return self._zoomValue
    
    def setZoom(self, value):
        if value < self.__zoomIncrements[0]: value = self.__zoomIncrements[0]
        if value > self.__zoomIncrements[-1]: value = self.__zoomIncrements[-1]

        self._zoomValue = value
        self.reloadTransforms()
        self.refreshState()

    def getFlipHorizontal(self):
        return self._flipHorizontal

    def setFlipHorizontal(self, value):
        self._flipHorizontal = value
        self.reloadTransforms()
        self.refreshState()
        self.reloadSceneRect()

    def getFlipVertical(self):
        return self._flipVertical
    
    def setFlipVertical(self, value):
        self._flipVertical = value
        self.reloadTransforms()
        self.refreshState()
        self.reloadSceneRect()

    def getScalingMode(self):
        return self._scalingMode
    
    def setScalingMode(self, mode: ScalingMode):
        self._scalingMode = mode
        self.reloadTransforms()
        self.refreshState()

    def getSamplingColors(self):
        return self.controller.get(self.Controller.Mode.ColorSampling)

    def setSamplingColors(self, value: bool):
        self.controller.set(self.Controller.Mode.ColorSampling, value)
        self.refreshState()

    def getImageLoaded(self):
        return self._imageLoaded

    def setImage(self, imageData: SubViewSettings.Tab = None):
        self.blockUpdates(True)
        if not imageData:
            self._imageLoaded = False
            img = QImage()
        else:
            stored_img = imageData.getImageData()
            if stored_img: img = stored_img
            else: img = QImage()
        
        self._imageLoaded = not img.isNull()
        self.imageItem.setPixmap(QPixmap.fromImage(img))
        if self._imageLoaded:
            self.restoreState(imageData.viewer_state)
            self.blockUpdates(False)
            self.refreshState(True)
        else:
            self.blockUpdates(True)
            self.refreshState(True)
        
    def getRotation(self) -> float:
        return self._rotateValue
    
    def setRotation(self, angle):
        self._rotateValue = angle
        self.reloadTransforms()
        self.refreshState()

    def getBackgroundColor(self):
        return self.viewport.palette().base().color()

    def setBackgroundColor(self, color):
        palette = self.viewport.palette()
        palette.setColor(QPalette.ColorRole.Base, color)
        self.viewport.setPalette(palette)
        self.refreshState()

    #endregion
    
    #region Signal Recievers
    
    def onColorSamplerTargetPicked(self, pos: QPoint):
        found_color = self.viewport.getColorAt(pos)
        if found_color:
            actual_color = ManagedColor.fromQColor(found_color)
            Krita.instance().activeWindow().activeView().setForeGroundColor(actual_color)

    def onControllerModeChanged(self, mode: "Controller.Mode", state: bool):
        
        self.refreshState()

    #endregion





