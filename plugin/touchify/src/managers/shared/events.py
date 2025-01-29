from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class GlobalEvents(QObject):
    @staticmethod
    def instance():
        try:
            return GlobalEvents.__instance
        except AttributeError:
            return None
        

    SIGNAL_TIMER_TICKED = pyqtSignal()
    SIGNAL_KRITA_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_TOUCHIFY_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_CANVAS_LAYOUT_CHANGED = pyqtSignal()
    SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED = pyqtSignal()
    SIGNAL_TOOLSHELF_PRESET_CHANGED = pyqtSignal(int)
    SIGNAL_MOUSE_RELEASED = pyqtSignal()
    SIGNAL_KEY_RELEASED = pyqtSignal()
    SIGNAL_WINDOW_RESIZED = pyqtSignal()
    SIGNAL_WINDOW_MOVED = pyqtSignal()
        
    @staticmethod
    def EMIT_SIGNAL_TIMER_TICKED():
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_TIMER_TICKED.emit()
    @staticmethod
    def EMIT_SIGNAL_KRITA_CONFIG_UPDATED():
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_KRITA_CONFIG_UPDATED.emit()
    @staticmethod
    def EMIT_SIGNAL_TOUCHIFY_CONFIG_UPDATED():
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.emit()
    @staticmethod
    def EMIT_SIGNAL_TOOLSHELF_PRESET_CHANGED(index: int):
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.emit(index)
    @staticmethod
    def EMIT_SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED():
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED.emit()
    @staticmethod
    def EMIT_SIGNAL_CANVAS_LAYOUT_CHANGED():
        if GlobalEvents.instance(): GlobalEvents.instance().SIGNAL_CANVAS_LAYOUT_CHANGED.emit()

    def eventFilter(self, obj: QObject, event: QEvent):
        if isinstance(obj, QMainWindow):
            if event.type() == QEvent.Type.Resize:
                self.SIGNAL_WINDOW_RESIZED.emit()
            elif event.type() == QEvent.Type.Move:
                self.SIGNAL_WINDOW_MOVED.emit()
            return False
        elif event.type() == QEvent.Type.MouseButtonRelease or \
           event.type() == QEvent.Type.TabletRelease:
            self.SIGNAL_MOUSE_RELEASED.emit()
        elif event.type() == QEvent.Type.KeyRelease:
            self.SIGNAL_KEY_RELEASED.emit()
        return False

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        GlobalEvents.__instance = self
        qApp.installEventFilter(self)
        
        