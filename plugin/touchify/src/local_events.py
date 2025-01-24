from PyQt5.QtCore import *

class LocalEvents(QObject):
    SIGNAL_TIMER_TICKED = pyqtSignal()
    SIGNAL_KRITA_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_TOUCHIFY_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_CANVAS_LAYOUT_CHANGED = pyqtSignal()
    SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED = pyqtSignal()
    SIGNAL_TOOLSHELF_PRESET_CHANGED = pyqtSignal(int)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        
        