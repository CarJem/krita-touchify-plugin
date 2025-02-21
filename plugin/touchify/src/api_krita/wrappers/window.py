from typing import Protocol, List
from dataclasses import dataclass

from PyQt5.QtCore import (pyqtBoundSignal)
from PyQt5.QtWidgets import (QWidgetAction, QMainWindow, QDockWidget,)

from krita import (
    Document as KritaDocument,
    View as KritaView
)

class WindowObj(Protocol):
    activeViewChanged: pyqtBoundSignal
    themeChanged: pyqtBoundSignal
    windowClosed: pyqtBoundSignal

    def createAction(self, id: str, text: str = ..., menuLocation: str = ...) -> QWidgetAction: ...
    def close(self) -> None: ...
    def activate(self) -> None: ...
    def activeView(self) -> KritaView: ...
    def showView(self, view: KritaView) -> None: ...
    def addView(self, document: KritaDocument) -> KritaView: ...
    def views(self) -> List[KritaView]: ...
    def dockers(self) -> List[QDockWidget]: ...
    def qwindow(self) -> QMainWindow: ...

@dataclass
class WindowAPI:
    window: WindowObj

    @property
    def windowClosed(self): return self.window.windowClosed
    @property
    def themeChanged(self): return self.window.themeChanged
    @property
    def activeViewChanged(self): return self.window.activeViewChanged

    def native(self):
        return self.window

    def qwindow(self):
        return self.window.qwindow()

    def createAction(self, name: str, description: str = None, menu: str = None) -> QWidgetAction:
        if description == None: description = name
        if menu == None: menu = ""
        return self.window.createAction(name, description, menu)