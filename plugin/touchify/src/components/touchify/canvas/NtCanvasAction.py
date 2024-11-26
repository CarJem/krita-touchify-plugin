
from PyQt5.QtCore import QObject, QEvent

from krita import *
from PyQt5.QtWidgets import *

from touchify.src.settings import TouchifyConfig


class NtCanvasAction(QObject):
    mouseReleased = pyqtSignal()

    def __init__(self, window: QMainWindow):
        self.main_window = window
        super().__init__()

    def isFocused(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
    
        if not isinstance(widget_under_cursor, QOpenGLWidget): return False
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return False

        return True

    def runAction(self, actionName: str):
        if self.isFocused():             
            action = Krita.instance().action(actionName)
            if action: action.trigger()

    def isCanvasEvent(self, event: QEvent, btn: Qt.MouseButton):
        return (event.type() == QEvent.Type.MouseButtonPress and event.button() == btn)

    def eventFilter(self, obj, event):
        if self.isCanvasEvent(event, Qt.MouseButton.LeftButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_LeftClickAction)
        elif self.isCanvasEvent(event, Qt.MouseButton.RightButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_RightClickAction)
        elif self.isCanvasEvent(event, Qt.MouseButton.MiddleButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_MiddleClickAction)
        return super().eventFilter(obj, event)