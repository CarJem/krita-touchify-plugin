from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.settings import TouchifySettings
from touchify.src.variables import *
from touchify.src.components.touchify.canvas.NtCanvas import NtCanvas

from touchify.src.components.krita.extensions import *

if TYPE_CHECKING:
    from ..window import TouchifyWindow

class CanvasManager(QObject):

    mouseLeftPress=pyqtSignal()
    mouseRightPress=pyqtSignal()
    mouseMiddlePress=pyqtSignal()

    mouseLeftRelease=pyqtSignal()
    mouseRightRelease=pyqtSignal()
    mouseMiddleRelease=pyqtSignal()

    normalFocus=pyqtSignal()
    delayedFocus=pyqtSignal()


    def __init__(self, instance: "TouchifyWindow"):
        super().__init__(instance)
        self.app_engine = instance
        self.last_canvas_focus = None
        self.nt_canvas: NtCanvas | None = None
        self.active_canvas: QOpenGLWidget | None = None

    def Window_Load(self):
        self.nt_canvas.Window_Load(self.app_engine)
        self.nt_canvas.Window().activeViewChanged.connect(self.OnEvent_ActiveViewChanged)
        self.OnEvent_ActiveViewChanged()

    def Actions_Post(self):
        self.nt_canvas.Actions_Post()

    def Actions_Init(self, window: Window, path: str):
        self.nt_canvas = NtCanvas(window.qwindow().window(), window)
        self.nt_canvas.Actions_Init(window, path)

    def OnEvent_ActiveViewChanged(self):
        if self.active_canvas != None:
            try: self.active_canvas.removeEventFilter(self)
            except: pass
            
            self.active_canvas = None
        
        current_view = self.nt_canvas.Window().activeView()
        if not current_view: return

        window_views = self.nt_canvas.Window().views()
        if current_view not in window_views: return

        mdi_area = self.nt_canvas.MdiArea()
        if not mdi_area: return

        mdi_subwindow = mdi_area.activeSubWindow()
        if not mdi_subwindow: return

        view_container = next((w for w in mdi_subwindow.findChildren(QWidget) if w.metaObject().className() == 'KisView'), None)
        if not view_container: return
        
        active_canvas = next((w for w in view_container.findChildren(QOpenGLWidget) if w.metaObject().className() == 'KisOpenGLCanvas2'), None)
        if not active_canvas: return

        self.active_canvas = active_canvas
        self.active_canvas.installEventFilter(self)


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
            action = Krita.instance().action(actionName)
            if action: action.trigger()

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