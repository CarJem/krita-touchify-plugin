from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.api_krita import KritaAPI
from touchify.src.managers.shared.settings import TouchifySettings
from touchify.__env__ import *
from touchify.src.components.canvas.NtCanvas import NtCanvas

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


    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers
        self.api_window: WindowAPI | None = None
        self.last_canvas_focus = None
        self.nt_canvas: NtCanvas | None = None
        self.active_canvas: QOpenGLWidget | None = None

    def Window_Load(self, api_window: WindowAPI):
        self.api_window = api_window
        #self.nt_canvas.Window_Load(self.api_window, self.managers)
        self.api_window.activeViewChanged.connect(self.OnEvent_ActiveViewChanged)
        self.OnEvent_ActiveViewChanged()

    def Actions_Post(self):
        #self.nt_canvas.Actions_Post()
        pass
        
    def Actions_Init(self, window: WindowAPI, path: str):
        #self.nt_canvas = NtCanvas(window.qwindow.window())
        #self.nt_canvas.Actions_Init(window, path)
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