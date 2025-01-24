from PyQt5.QtCore import *

class TouchifyEvents(QObject):
    @staticmethod
    def instance():
        try:
            return TouchifyEvents.__instance
        except AttributeError:
            return None
        

    SIGNAL_TIMER_TICKED = pyqtSignal()
    SIGNAL_KRITA_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_TOUCHIFY_CONFIG_UPDATED = pyqtSignal()
    SIGNAL_CANVAS_LAYOUT_CHANGED = pyqtSignal()
    SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED = pyqtSignal()
    SIGNAL_TOOLSHELF_PRESET_CHANGED = pyqtSignal(int)
        
    @staticmethod
    def EMIT_SIGNAL_TIMER_TICKED():
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_TIMER_TICKED.emit()
    @staticmethod
    def EMIT_SIGNAL_KRITA_CONFIG_UPDATED():
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_KRITA_CONFIG_UPDATED.emit()
    @staticmethod
    def EMIT_SIGNAL_TOUCHIFY_CONFIG_UPDATED():
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.emit()
    @staticmethod
    def EMIT_SIGNAL_TOOLSHELF_PRESET_CHANGED(index: int):
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_TOOLSHELF_PRESET_CHANGED.emit(index)
    @staticmethod
    def EMIT_SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED():
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_TOUCHIFY_TOOLBOX_PRESET_CHANGED.emit()
    @staticmethod
    def EMIT_SIGNAL_CANVAS_LAYOUT_CHANGED():
        if TouchifyEvents.instance(): TouchifyEvents.instance().SIGNAL_CANVAS_LAYOUT_CHANGED.emit()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        TouchifyEvents.__instance = self
        
        