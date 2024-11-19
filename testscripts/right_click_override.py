from krita import *


class MouseListenerTemp(QObject):
    mouseReleased = pyqtSignal()

    def __init__(self):
        super().__init__()

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.MouseButton.RightButton) or \
        (event.type() == QEvent.TabletRelease and event.button() == Qt.MouseButton.RightButton):
            self.mouseReleased.emit()
        return super().eventFilter(obj, event)
    
class TestObject(QObject):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.mouse_listener = MouseListenerTemp()
        QApplication.instance().installEventFilter(self.mouse_listener)
        self.mouse_listener.mouseReleased.connect(self.onMouseRelease)

    def shutdown(self):
        QApplication.instance().removeEventFilter(self.mouse_listener)
        self.mouse_listener.mouseReleased.disconnect(self.onMouseRelease)

    def onMouseRelease(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
        
        if not isinstance(widget_under_cursor, QOpenGLWidget): return
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return

        msgBox = QMessageBox()
        msgBox.setText("Hey!")
        msgBox.show()

qwin = Krita.instance().activeWindow().qwindow()

children = qwin.findChildren(TestObject)
for child in children:
    child.shutdown()
    child.deleteLater()

TestObject(qwin)