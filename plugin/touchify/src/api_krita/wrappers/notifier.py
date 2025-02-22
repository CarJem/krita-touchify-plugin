from typing import Protocol, Union, Callable
from dataclasses import dataclass
from PyQt5.QtCore import pyqtBoundSignal


PYQT_SLOT = Union[Callable[..., None], pyqtBoundSignal]



@dataclass
class NotifierAPI:
    notifier: 'GlobalNotifierClass'

    def add_configuration_changed_callback(self, slot: PYQT_SLOT):
        return self.notifier.configurationChanged.connect(slot)
    
    def add_window_created_callback(self, slot: PYQT_SLOT):
        return self.notifier.windowCreated.connect(slot)
    
class GlobalNotifierClass(Protocol):
    configurationChanged: pyqtBoundSignal

    applicationClosing: pyqtBoundSignal
    windowCreated: pyqtBoundSignal
    windowIsBeingCreated: pyqtBoundSignal

    viewClosed: pyqtBoundSignal
    viewCreated: pyqtBoundSignal

    imageClosed: pyqtBoundSignal
    imageSaved: pyqtBoundSignal
    imageCreated: pyqtBoundSignal

    def setActive(self, value: bool) -> None: ...
    def active(self) -> bool: ...