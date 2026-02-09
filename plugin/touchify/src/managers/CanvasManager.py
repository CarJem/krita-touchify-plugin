from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from jemlib.api_krita import KritaAPI

from jemlib.managers.GlobalEvents import GlobalEvents
from touchify.src.settings.TouchifySettings import TouchifySettings
from jemlib.api_touchify.env import *

from jemlib.alib_vaporjem.extensions.krita_extensions import *

if TYPE_CHECKING:
    from ..PluginManagers import TouchifyManagers


class CanvasManager(QObject):
    mouseLeftPress=pyqtSignal()
    mouseRightPress=pyqtSignal()
    mouseMiddlePress=pyqtSignal()

    mouseLeftRelease=pyqtSignal()
    mouseRightRelease=pyqtSignal()
    mouseMiddleRelease=pyqtSignal()

    normalFocus=pyqtSignal()
    delayedFocus=pyqtSignal()

    canvasResized = pyqtSignal()
    canvasMoved = pyqtSignal()
    canvasChanged = pyqtSignal()



    def __init__(self, parent: QObject, managers: "TouchifyManagers"):
        super().__init__(parent)
        self.managers = managers
        self.api_window: WindowAPI | None = None
        self.last_canvas_focus = None
        self.mdi_area: QMdiArea | None = None
        self.mdi_subwindow: QMdiSubWindow | None = None
        self.view_container: QWidget | None = None
        self.active_canvas: QOpenGLWidget | None = None

    def Window_Load(self, api_window: WindowAPI):
        self.api_window = api_window
        self.api_window.activeViewChanged.connect(self.OnEvent_ActiveViewChanged)
        GlobalEvents().SIGNAL_TIMER_TICKED.connect(self.onTick)
        self.OnEvent_ActiveViewChanged()

    def Actions_Post(self):
        pass
        
    def Actions_Init(self, window: WindowAPI, path: str):
        pass

    def currentBrushPreset(self):
        current_view = self.api_window.active_view
        if not current_view: return None

        window_views = self.api_window.views
        if current_view not in window_views: return None

        return current_view.brush_preset
    
    def underMouse(self):
        if not self.active_canvas: return False
        return self.active_canvas.underMouse()

    def hasFocus(self):
        if not self.active_canvas: return False
        return self.active_canvas.hasFocus()

    def OnEvent_ActiveViewChanged(self):
        def main():
            if self.active_canvas != None:
                try: self.active_canvas.removeEventFilter(self)
                except: pass
                

                self.mdi_area = None
                self.mdi_subwindow = None
                self.view_container = None
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

            self.mdi_area = mdi_area
            self.mdi_subwindow = mdi_subwindow
            self.view_container = view_container
            self.active_canvas = active_canvas
            self.active_canvas.installEventFilter(self)
        main(); self.canvasChanged.emit()

    def onTick(self):
        pass

    def eventFilter(self, obj: QObject, event: QEvent):

        try:
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

            if event.type() == QEvent.Type.Resize and obj == self.active_canvas:
                self.canvasResized.emit()
            if event.type() == QEvent.Type.Move and obj == self.active_canvas:
                self.canvasMoved.emit()

            if not Check_Event(): return False

            if event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.TabletPress:
                    match event.button():
                        case Qt.MouseButton.LeftButton:
                            Trigger_Run(TouchifySettings.preferences().canvas.canvas_left_click_action)
                            self.mouseLeftPress.emit()
                        case Qt.MouseButton.RightButton:
                            Trigger_Run(TouchifySettings.preferences().canvas.canvas_right_click_action)     
                            self.mouseRightPress.emit()
                        case Qt.MouseButton.MiddleButton:
                            Trigger_Run(TouchifySettings.preferences().canvas.canvas_middle_click_action)
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
        except:
            # Catch-all for any unexpected errors to prevent crashes
            return False