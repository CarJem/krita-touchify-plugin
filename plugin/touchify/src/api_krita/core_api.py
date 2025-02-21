# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from typing import Callable, Any

from krita import Krita as Api, Extension, DockWidgetFactory, Window as KritaWindow, qApp
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QWidgetAction,
    QAction,
    QDockWidget,
    QMdiArea)
from PyQt5.QtGui import QKeySequence, QColor, QIcon, QPalette
from PyQt5.QtCore import QTimer


from touchify.src.api_krita.enums.docker_position import DockerPosition
from touchify.src.api_krita.wrappers import (
    UnknownVersion,
    ToolDescriptor,
    DocumentAPI,
    Version,
    CanvasAPI,
    CursorAPI,
    WindowAPI,
    NotifierAPI,
    ViewAPI)


class KritaInstance:
    """Wraps krita API for typing, documentation and PEP8 compatibility."""

    active_tool = ToolDescriptor()
    """Settable property which lets to set and get active tool from toolbox."""

    def __init__(self) -> None:
        self.instance = Api.instance()
        self.screen_size = QDesktopWidget().screenGeometry(-1).width()
        self.main_window: Any = None

    def get_active_view(self) -> ViewAPI:
        """Return wrapper of krita `View`."""
        return ViewAPI(self.instance.activeWindow().activeView())
    
    def get_active_view_native(self):
        win = self.instance.activeWindow()
        if win == None: return None

        view = win.activeView()
        if view == None: return None

        return view

    def get_active_document(self) -> DocumentAPI | None:
        """Return wrapper of krita `Document`."""
        document = self.instance.activeDocument()
        if document is None:
            return None
        return DocumentAPI(document)

    def get_active_document_native(self):
        document = self.instance.activeDocument()
        if document is None:
            return None
        return document

    def get_active_canvas(self) -> CanvasAPI:
        """Return wrapper of krita `Canvas`."""
        return CanvasAPI(self.instance.activeWindow().activeView().canvas())
    
    def get_active_canvas_native(self):
        win = self.instance.activeWindow()
        if win == None: return None

        view = win.activeView()
        if view == None: return None

        canvas = view.canvas()
        if canvas == None: return None

        return canvas

    def get_cursor(self) -> CursorAPI:
        """Return wrapper of krita `Cursor`. Don't use on plugin init phase."""
        q_win = self.get_active_qwindow()
        return CursorAPI(q_win)

    def get_documents(self):
        return list(map(DocumentAPI, self.instance.documents()))

    def get_documents_native(self):
        return self.instance.documents()

    def trigger_action(self, action_name: str) -> None:
        """Trigger internal krita action called `action_name`."""
        act = self.instance.action(action_name)
        if act: act.trigger()
        return None

    def get_action_shortcut(self, action_name: str) -> QKeySequence:
        """Return shortcut of krita action called `action_name`."""
        return self.instance.action(action_name).shortcut()

    def get_presets(self) -> dict[str, Any]:
        """Return a list of unwrapped preset objects"""
        return self.instance.resources('preset')

    def get_active_qwindow(self) -> QMainWindow:
        """Return qt window of krita. Don't use on plugin init phase."""
        return self.instance.activeWindow().qwindow()

    def get_active_mdi_area(self) -> QMdiArea:
        return self.get_active_qwindow().findChild(QMdiArea)  # type: ignore

    def get_icon(self, icon_name: str) -> QIcon:
        return self.instance.icon(icon_name)
    
    def get_action(self, action_name: str) -> QAction:
        return self.instance.action(action_name)
    
    def get_actions(self) -> list[QAction]:
        return self.instance.actions()
    
    def get_dockers(self) -> list[QDockWidget]:
        return self.instance.dockers()
    
    def get_windows_native(self) -> list[KritaWindow]:
        return self.instance.windows()

    def get_app_data_location(self) -> str:
        return self.instance.getAppDataLocation()

    def notifier(self) -> NotifierAPI:
        return NotifierAPI(self.instance.notifier())

    def native(self) -> Api:
        return self.instance
    
    def read_setting(
        self,
        group: str,
        name: str,
        default: str = "Not stored"
    ) -> str | None:
        """
        Read a setting from kritarc file.

        - Return string red from file if present
        - Return default if it was given
        - Return None if default was not given
        """
        red_value = self.instance.readSetting(group, name, default)
        return None if red_value == "Not stored" else red_value

    def write_setting(self, group: str, name: str, value: Any) -> None:
        """Write setting to kritarc file. Value type will be lost."""
        self.instance.writeSetting(group, name, str(value))

    def create_action(
        self,
        window: 'WindowAPI',
        name: str,
        group: str = "",
        callback: Callable[[], None] = lambda: None
    ) -> QWidgetAction:
        """
        Create a new action in krita.

        Requires providing a krita window received in createActions()
        method of the main extension file.
        """
        krita_action = window.createAction(name, name, group)
        krita_action.setAutoRepeat(False)
        krita_action.triggered.connect(callback)
        return krita_action

    def add_extension(self, extension: Extension) -> None:
        """Add extension/plugin/add-on to krita."""
        self.instance.addExtension(extension(self.instance))

    def add_dock_widget_factory(self, docker_id: str, docker_position: DockerPosition, docker_class: any):
        self.instance.addDockWidgetFactory(DockWidgetFactory(docker_id, docker_position, docker_class))

    def get_extension_by_name(self, target: str):
        """Get extension/plugin/add-on by object name."""
        krita_extensions = self.instance.extensions()
        for extension in krita_extensions:
            if extension.objectName() == target:
                return extension
        return None

    def add_theme_change_callback(self, callback: Callable[[], None]) -> Any:
        """
        Add method which should be run after the theme is changed.

        Method is delayed with a timer to allow running it on plugin
        initialization phase.
        """
        def connect_callback() -> None:
            self.main_window = self.instance.activeWindow()
            if self.main_window is not None:
                self.main_window.themeChanged.connect(callback)
        QTimer.singleShot(1000, connect_callback)

    def get_main_color_from_theme(self) -> QColor:
        """Return main color of the current theme."""
        return qApp.palette().color(QPalette.Window)

    def get_active_color_from_theme(self) -> QColor:
        """Return active color of the current theme."""
        return qApp.palette().color(QPalette.Highlight)

    @property
    def is_light_theme_active(self) -> bool:
        """Return if currently set theme is light using it's main color."""
        main_color = self.get_main_color_from_theme()
        return main_color.value() > 128

    @property
    def version(self) -> Version:
        """Get version of krita."""
        raw: str = self.instance.version()

        num = r"(0|[1-9]\d*)"
        dot = r"\."
        delimiter = r"[ -]?"
        info = r"(.*)"

        regex = "^" + num + dot + num + dot + num + delimiter + info + "$"
        result = re.search(regex, raw)

        if result is None or len(result.groups()) != 4:
            return UnknownVersion()

        major, minor, fix, additional_info = result.groups()

        return Version(int(major), int(minor), int(fix), additional_info)



