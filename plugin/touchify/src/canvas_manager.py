from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from touchify.src.settings import TouchifySettings
from touchify.src.variables import *


from touchify.src.ext.KritaExtensions import *

if TYPE_CHECKING:
    from .window import TouchifyWindow

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
        super().__init__()
        self.appEngine = instance
        self.source_window = self.appEngine.windowSource.qwindow()
        self.lastCanvasFocus = None

        qApp.installEventFilter(self)


    def __runCanvasAction__(self, actionName: str):
        action = Krita.instance().action(actionName)
        if action: action.trigger()

    def __isMouseOverCanvas__(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
    
        if not isinstance(widget_under_cursor, QOpenGLWidget): return False
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return False

        return True
    
    def __IsCanvasWidget__(self, obj: QObject):
        if not isinstance(obj, QOpenGLWidget): return False
        if not obj.metaObject().className() == "KisOpenGLCanvas2": return False

        return True

    def eventFilter(self, obj: QObject, event: QEvent):
        if not self.__IsCanvasWidget__(obj): 
            return super().eventFilter(obj, event)
        
        if event.type() == QEvent.Type.MouseButtonPress:
                match event.button():
                    case Qt.MouseButton.LeftButton:
                        self.__runCanvasAction__(TouchifySettings.instance().preferences().Canvas_LeftClickAction)
                        self.mouseLeftPress.emit()
                    case Qt.MouseButton.RightButton:
                        self.__runCanvasAction__(TouchifySettings.instance().preferences().Canvas_RightClickAction)     
                        self.mouseRightPress.emit()
                    case Qt.MouseButton.MiddleButton:
                        self.__runCanvasAction__(TouchifySettings.instance().preferences().Canvas_MiddleClickAction)
                        self.mouseMiddlePress.emit()
        elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.lastCanvasFocus:
                    self.delayedFocus.emit()
                    self.lastCanvasFocus = None
                else:
                    match event.button():
                        case Qt.MouseButton.LeftButton:
                            self.mouseLeftRelease.emit()
                        case Qt.MouseButton.RightButton:
                            self.mouseRightRelease.emit()
                        case Qt.MouseButton.MiddleButton:
                            self.mouseMiddleRelease.emit()
        elif event.type() == QEvent.Type.FocusIn:
            if obj.hasFocus(): 
                self.lastCanvasFocus = obj
                self.normalFocus.emit()
        return super().eventFilter(obj, event)