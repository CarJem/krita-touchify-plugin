from typing import List
from dataclasses import InitVar, dataclass

from PyQt5.QtCore import (pyqtBoundSignal, Qt)
from PyQt5.QtWidgets import (QWidgetAction, QMainWindow, QMdiArea, QWidget, QDockWidget)

from krita import (
    Window as KritaWindow
)
from jemlib.api_krita.wrappers.document import DocumentAPI
from jemlib.api_krita.wrappers.view import ViewAPI
from jemlib.api_krita.extensions.window_manager import WindowNotifier

@dataclass
class WindowAPI:
    __internal__: KritaWindow
    __notifier__: InitVar[WindowNotifier] = None
        
    @property
    def internal(self): return self.__internal__

    @property
    def windowClosed(self) -> pyqtBoundSignal: return self.__internal__.windowClosed
    @property
    def themeChanged(self) -> pyqtBoundSignal: return self.__internal__.themeChanged
    @property
    def activeViewChanged(self) -> pyqtBoundSignal: return self.__internal__.activeViewChanged


    @property
    def mdi_area(self): return self.__internal__.qwindow().findChild(QMdiArea)
    @property
    def active_view(self): return ViewAPI(self.__internal__.activeView())
    @property
    def active_qview(self):
        current_view = self.active_view
        if not current_view: return None

        window_views = self.views
        if current_view not in window_views: return None

        mdi_area = self.mdi_area
        if not mdi_area: return None

        mdi_subwindow = mdi_area.activeSubWindow()
        if not mdi_subwindow: return None

        view_container = next((w for w in mdi_subwindow.findChildren(QWidget) if w.metaObject().className() == 'KisView'), None)
        if not view_container: return None

        return view_container
    @property
    def views(self) -> List[ViewAPI]: return list(map(ViewAPI, self.__internal__.views()))
    @property
    def hwnd(self): return int(self.__internal__.qwindow().winId())
    @property
    def qwindow(self) -> QMainWindow: return self.__internal__.qwindow()
    @property
    def dockers(self) -> List[QDockWidget]: return self.__internal__.dockers()
    @property
    def notifier(self) -> (WindowNotifier | None):
        if self.__notifier__ == None:
            source_window = self.__internal__.qwindow()
            results = source_window.findChildren(WindowNotifier, options=Qt.FindChildOption.FindChildrenRecursively)
            if len(results) > 0: self.__notifier__ = results[0]
        return self.__notifier__

    def add_view(self, document: DocumentAPI) -> ViewAPI:
        return ViewAPI(self.__internal__.addView(document.internal))
        
    def create_action(self, name: str, description: str = None, menu: str = None) -> QWidgetAction:
        if description == None: description = name
        if menu == None: menu = ""
        return self.__internal__.createAction(name, description, menu)