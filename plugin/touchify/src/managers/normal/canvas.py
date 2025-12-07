from enum import Enum
from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.api_krita import KritaAPI
from touchify.src.managers.shared.events import GlobalEvents
from touchify.src.managers.shared.settings import TouchifySettings
from touchify.__env__ import *

from touchify.src.extensions.krita_extensions import *

if TYPE_CHECKING:
    from ...PluginManagers import TouchifyManagers




class CanvasManager(QObject):
    mouseLeftPress=pyqtSignal()
    mouseRightPress=pyqtSignal()
    mouseMiddlePress=pyqtSignal()

    mouseLeftRelease=pyqtSignal()
    mouseRightRelease=pyqtSignal()
    mouseMiddleRelease=pyqtSignal()

    normalFocus=pyqtSignal()
    delayedFocus=pyqtSignal()


    class WidgetAlignment(Enum):
        TopLeft = 1
        TopCenter = 2
        TopRight = 3
        MidLeft = 4
        MidRight = 5
        BottomLeft = 6
        BottomCenter = 7
        BottomRight = 8



    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers
        self.api_window: WindowAPI | None = None
        self.last_canvas_focus = None
        self.active_canvas: QOpenGLWidget | None = None

    def Window_Load(self, api_window: WindowAPI):
        self.api_window = api_window
        self.api_window.activeViewChanged.connect(self.OnEvent_ActiveViewChanged)
        GlobalEvents.instance().SIGNAL_TIMER_TICKED.connect(self.onTick)
        self.OnEvent_ActiveViewChanged()

    def Actions_Post(self):
        pass
        
    def Actions_Init(self, window: WindowAPI, path: str):
        pass

    def OnEvent_ActiveViewChanged(self):
        if self.active_canvas != None:
            try: self.active_canvas.removeEventFilter(self)
            except: pass
            
            self.active_canvas = None
        
        current_view = self.api_window.active_view
        if not current_view: return

        window_views = self.api_window.views
        if current_view not in window_views: return

        mdi_area = self.api_window.mdi_area
        if not mdi_area: return

        mdi_subwindow = mdi_area.activeSubWindow()
        if not mdi_subwindow: return

        view_container = next((w for w in mdi_subwindow.findChildren(QWidget) if w.metaObject().className() == 'KisView'), None)
        if not view_container: return
        
        active_canvas = next((w for w in view_container.findChildren(QOpenGLWidget) if w.metaObject().className() == 'KisOpenGLCanvas2'), None)
        if not active_canvas: return

        self.active_canvas = active_canvas
        self.active_canvas.installEventFilter(self)


    def updateFloatingDocker(self, docker_id: str, position: WidgetAlignment):
        if not self.active_canvas: 
            return
        
        floatableDocker = self.managers.mgr_dockers.findDocker(docker_id)
        if not floatableDocker.isVisible():
            return
        
        if floatableDocker.isFloating() == False:
            floatableDocker.setFloating(True)
        
        edge_padding: int = 5
        space_rect = self.active_canvas.rect()
        docker_width = floatableDocker.width()
        docker_height = floatableDocker.height()

        if docker_width != 0 and docker_height != 0:
            docker_halfwidth = int(docker_width / 2)
            docker_halfheight = int(docker_height / 2)
        else:
            docker_halfwidth = 0
            docker_halfheight = 0

        top_left = QPoint(space_rect.topLeft()) + QPoint(edge_padding, edge_padding)
        top_center = QPoint(space_rect.center().x(),space_rect.top()) - QPoint(docker_halfwidth, 0) + QPoint(0, edge_padding)
        top_right = QPoint(space_rect.topRight()) - QPoint(docker_width, 0) + QPoint(-edge_padding, edge_padding)

        mid_left = QPoint(space_rect.left(), space_rect.center().y()) - QPoint(0, docker_halfheight) + QPoint(edge_padding, 0)
        mid_right = QPoint(space_rect.right(), space_rect.center().y()) - QPoint(docker_width, docker_halfheight) + QPoint(-edge_padding, 0)

        bottom_left = QPoint(space_rect.bottomLeft()) - QPoint(0, docker_height) + QPoint(edge_padding, -edge_padding)
        bottom_center = QPoint(space_rect.center().x(), space_rect.bottom()) - QPoint(docker_halfwidth, docker_height) + QPoint(0, -edge_padding)
        bottom_right = QPoint(space_rect.bottomRight()) - QPoint(docker_width, docker_height) + QPoint(-edge_padding, -edge_padding)

        edgePoint: QPoint = QPoint(0,0)
        match position:
            case CanvasManager.WidgetAlignment.TopLeft:
                edgePoint = self.active_canvas.mapToGlobal(top_left)
            case CanvasManager.WidgetAlignment.TopRight:
                edgePoint = self.active_canvas.mapToGlobal(top_right)
            case CanvasManager.WidgetAlignment.BottomRight:
                edgePoint = self.active_canvas.mapToGlobal(bottom_right)
            case CanvasManager.WidgetAlignment.BottomLeft:
                edgePoint = self.active_canvas.mapToGlobal(bottom_left)
            case CanvasManager.WidgetAlignment.TopCenter:
                edgePoint = self.active_canvas.mapToGlobal(top_center)
            case CanvasManager.WidgetAlignment.BottomCenter:
                edgePoint = self.active_canvas.mapToGlobal(bottom_center)
            case CanvasManager.WidgetAlignment.MidLeft:
                edgePoint = self.active_canvas.mapToGlobal(mid_left)
            case CanvasManager.WidgetAlignment.MidRight:
                edgePoint = self.active_canvas.mapToGlobal(mid_right)
            
            case _:
                edgePoint = self.active_canvas.mapToGlobal(QPoint(0,0))

        floatableDocker.move(edgePoint)



    def onTick(self):
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_1", CanvasManager.WidgetAlignment.TopLeft)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_2", CanvasManager.WidgetAlignment.TopCenter)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_3", CanvasManager.WidgetAlignment.TopRight)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_4", CanvasManager.WidgetAlignment.MidLeft)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_5", CanvasManager.WidgetAlignment.MidRight)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_6", CanvasManager.WidgetAlignment.BottomLeft)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_7", CanvasManager.WidgetAlignment.BottomCenter)
        self.updateFloatingDocker(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT + "_8", CanvasManager.WidgetAlignment.BottomRight)

    def eventFilter(self, obj: QObject, event: QEvent):

        def Check_Event():
            event_type = event.type()
            if event_type == QEvent.Type.FocusIn or \
               event_type == QEvent.Type.MouseButtonPress or \
               event_type == QEvent.Type.TabletPress or \
               event_type == QEvent.Type.MouseButtonRelease or \
               event_type == QEvent.Type.TabletRelease: return True
            else: return False
            

        def Trigger_Run(actionName: str):
            KritaAPI.trigger_action(actionName)

        try:
            if not self.active_canvas == obj: return False
        except:
            return False

        if not Check_Event(): return False

        if event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.TabletPress:
                match event.button():
                    case Qt.MouseButton.LeftButton:
                        Trigger_Run(TouchifySettings.instance().preferences().Canvas_LeftClickAction)
                        self.mouseLeftPress.emit()
                    case Qt.MouseButton.RightButton:
                        Trigger_Run(TouchifySettings.instance().preferences().Canvas_RightClickAction)     
                        self.mouseRightPress.emit()
                    case Qt.MouseButton.MiddleButton:
                        Trigger_Run(TouchifySettings.instance().preferences().Canvas_MiddleClickAction)
                        self.mouseMiddlePress.emit()
        elif event.type() == QEvent.Type.MouseButtonRelease or event.type() == QEvent.Type.TabletRelease:
                if self.last_canvas_focus:
                    self.delayedFocus.emit()
                    self.last_canvas_focus = None

                match event.button():
                    case Qt.MouseButton.LeftButton:
                        self.mouseLeftRelease.emit()
                    case Qt.MouseButton.RightButton:
                        self.mouseRightRelease.emit()
                    case Qt.MouseButton.MiddleButton:
                        self.mouseMiddleRelease.emit()
        elif event.type() == QEvent.Type.FocusIn:
            if obj.hasFocus(): 
                self.last_canvas_focus = obj
                self.normalFocus.emit()
        return False