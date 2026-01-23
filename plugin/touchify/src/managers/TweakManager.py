from PyQt5.QtWidgets import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.api_touchify.env import *
from touchify.src.components.tweaks.BrushEditorTweak import BrushEditorTweak
from touchify.src.settings.TouchifySettings import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..PluginWindow import TouchifyWindow


from krita import *

SMALL_TAB_SIZE = 22
SMALL_TAB_ICON_SIZE = 12
SMALL_TAB_CLOSE_BUTTON_MARGIN = 2

class TweakManager(QObject):

    def __init__(self, instance: "TouchifyWindow"):
        super().__init__(instance)
        self.app_window = instance
        self.api_window: WindowAPI = None
        self.qt_window: QMainWindow = None
        self.brush_editor_tweak: BrushEditorTweak | None = None

    def Window_Load(self):
        KritaAPI.get_action("show_brush_editor").triggered.connect(self.onBrushEditorTrigged)
        self.api_window = self.app_window.api_window
        self.qt_window = self.api_window.qwindow
        self.qt_window.themeChanged.connect(self.rebuildStyleSheet)
        self.brush_editor_tweak = BrushEditorTweak(self.app_window.api_window, self.app_window.managers)
        self.rebuildStyleSheet()

    def Window_Reload(self):
        self.brush_editor_tweak.refresh()
        self.rebuildStyleSheet()

    def Actions_Init(self, window: WindowAPI, path: str):
        pass

    def Actions_Post(self):
        pass

    def onBrushEditorTrigged(self):
        self.brush_editor_tweak.refresh()

    def rebuildStyleSheet(self):
        if self.qt_window == None:
            return

        config = TouchifySettings.preferences().tweaks

        # region No Toolbar Borders
        full_style_sheet = ""
        if config.borderless_toolbar:
            full_style_sheet += f"\n QToolBar {{ border: none; }} \n"    
        self.qt_window.setStyleSheet(full_style_sheet)
        #endregion

        # region Small Tabs
        canvas_style_sheet = ""
        
        if config.thin_document_tabs:
            canvas_style_sheet += f"""\n 
            QTabBar {{ icon-size: {SMALL_TAB_ICON_SIZE}px {SMALL_TAB_ICON_SIZE}px; }}
            QTabBar::tab {{ height: {SMALL_TAB_SIZE}px;  }} 
            QTabBar::close-button {{ margin: {SMALL_TAB_CLOSE_BUTTON_MARGIN}px; }} 
            \n"""

        canvas = self.qt_window.centralWidget()
        if canvas:
            canvas.setStyleSheet(canvas_style_sheet)
            canvas.adjustSize()
        # endregion
        
        # region Privacy Mode
        recentDocumentsListView = self.qt_window.findChild(QListView,'recentDocumentsListView')
        if recentDocumentsListView:
            recentDocumentsListView.setHidden(config.enable_privacy_mode)
            recent_files_action = KritaAPI.get_action("file_open_recent")
            recent_files_native_actions = [
                "no_entries",
                "separator",
                "clear_action"
            ]
            for item in recent_files_action.menu().actions():
                if item.objectName() not in recent_files_native_actions:
                    item.setVisible(not config.enable_privacy_mode)
        #endregion



    



    