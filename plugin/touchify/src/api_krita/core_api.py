# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from typing import Callable, Any, List


from krita import (
    Extension, 
    DockWidgetFactory, DockWidgetFactoryBase, 
    Krita as KritaAPI,
    qApp
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QWidgetAction,
    QAction,
    QDockWidget,
    QMdiArea)
from PyQt5.QtGui import QKeySequence, QColor, QIcon, QPalette


from touchify.src.api_krita.wrappers import (
    UnknownVersion,
    DocumentAPI,
    Version,
    CanvasAPI,
    CursorAPI,
    WindowAPI,
    NotifierAPI,
    ViewAPI
)

from touchify.src.api_krita.extensions import (
    ToolDescriptor,
    WindowManager
)





class KritaInstance:
    """Wraps krita API for typing and documentation"""

    active_tool = ToolDescriptor()
    """Settable property which lets to set and get active tool from toolbox."""

    window_manager = WindowManager()

    def __init__(self) -> None:
        self.instance = KritaAPI.instance()
        self.screen_size = QDesktopWidget().screenGeometry(-1).width()

    #region API Wrappers

    def get_active_view(self) -> ViewAPI:
        """Return wrapper of krita `View`."""
        win = self.instance.activeWindow()
        if win == None: return ViewAPI(None)

        view = win.activeView()
        if view == None: return ViewAPI(None)

        return ViewAPI(view)
    
    def get_active_document(self) -> DocumentAPI:
        """Return wrapper of krita `Document`."""
        return DocumentAPI(self.instance.activeDocument())

    def get_active_canvas(self) -> CanvasAPI:
        """Return wrapper of krita `Canvas`."""
        win = self.instance.activeWindow()
        if win == None: return CanvasAPI(None)

        view = win.activeView()
        if view == None: return CanvasAPI(None)

        canvas = view.canvas()
        if canvas == None: return CanvasAPI(None)

        return CanvasAPI(canvas)

    def get_active_window(self) -> WindowAPI:
        return WindowAPI(self.instance.activeWindow())
    
    def get_active_qwindow(self) -> QMainWindow:
        """Return qt window of krita. Don't use on plugin init phase."""
        return self.instance.activeWindow().qwindow()

    def get_active_mdi_area(self) -> QMdiArea:
        return self.get_active_qwindow().findChild(QMdiArea)  # type: ignore
   
    def get_windows(self) -> list[WindowAPI]:
        return list(map(WindowAPI, self.instance.windows()))
    
    def get_documents(self) -> list[DocumentAPI]:
        return list(map(DocumentAPI, self.instance.documents()))
    
    #endregion
    
    def open_document(self, filename: str):
        return DocumentAPI(self.instance.openDocument(filename))


    def get_cursor(self) -> CursorAPI:
        """Return wrapper of krita `Cursor`. Don't use on plugin init phase."""
        q_win = self.get_active_qwindow()
        return CursorAPI(q_win)

    def get_action_shortcut(self, action_name: str) -> QKeySequence:
        """Return shortcut of krita action called `action_name`."""
        return self.instance.action(action_name).shortcut()

    def get_presets(self) -> dict[str, Any]:
        """Return a list of unwrapped preset objects"""
        return self.instance.resources('preset')

    def get_icon(self, icon_name: str) -> QIcon:
        return self.instance.icon(icon_name)
    
    def get_action(self, action_name: str) -> QAction:
        return self.instance.action(action_name)
    
    def get_actions(self) -> List[QAction]:
        return self.instance.actions()
    
    def get_dockers(self) -> List[QDockWidget]:
        return self.instance.dockers()
    
    def get_docker(self, object_name: str) -> QDockWidget | None:
        try:
            docker_list = self.get_dockers()
            for docker_obj in docker_list:
                if docker_obj.objectName() == object_name:
                    return docker_obj
        except:
            return None

    def trigger_action(self, action_name: str) -> None:
        """Trigger internal krita action called `action_name`."""
        act = self.instance.action(action_name)
        if act: act.trigger()
        return None

    def get_app_data_location(self) -> str:
        return self.instance.getAppDataLocation()

    def notifier(self) -> NotifierAPI:
        return NotifierAPI(self.instance.notifier())
    
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
        krita_action = window.create_action(name, name, group)
        krita_action.setAutoRepeat(False)
        krita_action.triggered.connect(callback)
        return krita_action

    def add_extension(self, extension: Extension) -> None:
        """Add extension/plugin/add-on to krita."""
        self.instance.addExtension(extension(self.instance))

    def add_dock_widget_factory(self, docker_id: str, docker_position: int, docker_class: any):
        self.instance.addDockWidgetFactory(DockWidgetFactory(docker_id, DockWidgetFactoryBase.DockPosition(docker_position), docker_class))

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
        """
        main_window = self.instance.activeWindow()
        if main_window is not None:
            return main_window.themeChanged.connect(callback)
        else:
            return None

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




