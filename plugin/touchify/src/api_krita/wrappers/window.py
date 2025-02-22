from typing import Protocol, List
from dataclasses import InitVar, dataclass

from PyQt5.QtCore import (pyqtBoundSignal, Qt)
from PyQt5.QtWidgets import (QWidgetAction, QMainWindow, QDockWidget,)

from krita import (
    Document as KritaDocument,
    View as KritaView
)
from touchify.src.api_krita.extensions.window_manager import WindowNotifier

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
    __internal__: WindowObj
    __notifier__: InitVar[WindowNotifier] = None

    @property
    def windowClosed(self): return self.__internal__.windowClosed
    @property
    def themeChanged(self): return self.__internal__.themeChanged
    @property
    def activeViewChanged(self): return self.__internal__.activeViewChanged
    
    def notifier(self) -> (WindowNotifier | None):
        if self.__notifier__ == None:
            source_window = self.__internal__.qwindow()
            results = source_window.findChildren(WindowNotifier, options=Qt.FindChildOption.FindChildrenRecursively)
            if len(results) > 0: self.__notifier__ = results[0]
        return self.__notifier__

    def hwnd(self):
        return int(self.__internal__.qwindow().winId())

    def native(self):
        return self.__internal__

    def qwindow(self):
        return self.__internal__.qwindow()

    def createAction(self, name: str, description: str = None, menu: str = None) -> QWidgetAction:
        if description == None: description = name
        if menu == None: menu = ""
        return self.__internal__.createAction(name, description, menu)