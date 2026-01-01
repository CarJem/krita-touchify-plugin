from PyQt5.QtCore import *
from PyQt5.QtWidgets import *




class GlobalEventsProxyInstance(QObject):
    SIGNAL_KRITA_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_TOOLBOX_LAYOUT_UPDATED = pyqtSignal()
    SIGNAL_TOOLSHELF_PRESET_UPDATED = pyqtSignal(int)
    SIGNAL_PIE_TRIGGER_SENT = pyqtSignal(object)

    SIGNAL_TIMER_TICKED = pyqtSignal()
    SIGNAL_MOUSE_RELEASED = pyqtSignal()
    SIGNAL_KEY_RELEASED = pyqtSignal()
    SIGNAL_WINDOW_RESIZED = pyqtSignal()
    SIGNAL_WINDOW_MOVED = pyqtSignal()
    
    def setup(self):
        self.intervalTimer = QTimer(self)
        self.intervalTimer.timeout.connect(self.onTimerTick)
        self.intervalTimer.start(250)

    def onTimerTick(self):
        self.SIGNAL_TIMER_TICKED.emit()

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
        qApp.installEventFilter(self)

def GlobalEvents(parent: QObject = None) -> GlobalEventsProxyInstance:
    global GlobalEventsProxy
    if 'GlobalEventsProxy' not in globals() or not isinstance(GlobalEventsProxy, QObject):
        GlobalEventsProxy = GlobalEventsProxyInstance(parent)
    return GlobalEventsProxy