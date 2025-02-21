from typing import Protocol
from dataclasses import dataclass
from PyQt5.QtCore import pyqtBoundSignal


class NotifierObj(Protocol):
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

@dataclass
class NotifierAPI:
    notifier: NotifierObj

    def configurationChanged(self):
        return self.notifier.configurationChanged
    
    def windowCreated(self):
        return self.notifier.windowCreated