from PyQt5.QtWidgets import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
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

    #region Signals

    def Window_Load(self):
        KritaAPI.get_action("show_brush_editor").triggered.connect(self.onBrushEditorTrigged)
        self.api_window = self.app_window.api_window
        self.qt_window = self.api_window.qwindow
        self.qt_window.themeChanged.connect(self.rebuildStyleSheet)
        self.brush_editor_tweak = BrushEditorTweak(self.app_window.api_window)
        self.rebuildStyleSheet()

    def onBrushEditorTrigged(self):
        self.brush_editor_tweak.Update_State()

    #endregion

    #region Actions

    def Actions_Init(self, window: WindowAPI, path: str):

        def createAction(id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
            result = window.create_action(id, text, menuLocation)
            result.setCheckable(setCheckable)
            result.setChecked(setChecked)
            result.toggled.connect(onToggled)
            return result
    
        config = TouchifySettings.preferences()

        nu_options_menu = QMenu("Tweaks", window.qwindow)
        options_action = window.create_action(TouchifyEnv.ActionID.Styles.MENU, "Tweaks", path)
        options_action.setMenu(nu_options_menu)
        sublocation_path = "{0}/{1}".format(path, TouchifyEnv.ActionID.Styles.MENU)

        nu_options_menu.addAction(createAction(TouchifyEnv.ActionID.Styles.PRIVACYMODE, "Privacy Mode", sublocation_path, True, config.Styles_PrivacyMode, self.privacyModeToggled))        
        nu_options_menu.addAction(createAction(TouchifyEnv.ActionID.Styles.BORDERLESSTOOLBARS, "Borderless Toolbars", sublocation_path, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        nu_options_menu.addAction(createAction(TouchifyEnv.ActionID.Styles.TABHEIGHT, "Thin Document Tabs", sublocation_path, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))
        nu_options_menu.addAction(createAction(TouchifyEnv.ActionID.Styles.DOCKEDBRUSHEDITOR, "Docked Brush Editor", sublocation_path, True, config.Styles_DockedBrushEditor, self.dockedBrushEditorToggled))
        nu_options_menu.addAction(createAction(TouchifyEnv.ActionID.Styles.DOCKEDBRUSHEDITORZOOMFIX, "Brush Editor Zoom Fix", sublocation_path, True, config.Styles_BrushEditorZoomFix, self.brushEditorZoomFixToggled))

    def Actions_Post(self):
        settings_menu = self.qt_window.findChild(QMenu, 'settings')
        KritaExtensions.moveActionTo(TouchifyEnv.ActionID.Styles.MENU, settings_menu, settings_menu, 'style_menu')

    #endregion

    #region Toggles

    def brushEditorZoomFixToggled(self, toggled):
        TouchifySettings.preferences().Styles_BrushEditorZoomFix = toggled
        TouchifySettings.preferences().save()
        self.brush_editor_tweak.Update_State()

    def dockedBrushEditorToggled(self, toggled):
        TouchifySettings.preferences().Styles_DockedBrushEditor = toggled
        TouchifySettings.preferences().save()
        self.brush_editor_tweak.Update_State()

    def toolbarBorderToggled(self, toggled):
        TouchifySettings.preferences().Styles_BorderlessToolbar = toggled
        TouchifySettings.preferences().save()
        self.rebuildStyleSheet()

    def tabHeightToggled(self, toggled):
        TouchifySettings.preferences().Styles_ThinDocumentTabs = toggled
        TouchifySettings.preferences().save()
        self.rebuildStyleSheet()
        
    def privacyModeToggled(self, toggled):
        TouchifySettings.preferences().Styles_PrivacyMode = toggled
        TouchifySettings.preferences().save()
        self.rebuildStyleSheet()

    #endregion

    #region Methods

    def rebuildStyleSheet(self):
        if self.qt_window == None:
            return

        config = TouchifySettings.preferences()

        # region No Toolbar Borders
        full_style_sheet = ""
        if config.Styles_BorderlessToolbar:
            full_style_sheet += f"\n QToolBar {{ border: none; }} \n"    
        self.qt_window.setStyleSheet(full_style_sheet)
        #endregion

        # region Small Tabs
        canvas_style_sheet = ""
        
        if config.Styles_ThinDocumentTabs:
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
            recentDocumentsListView.setHidden(config.Styles_PrivacyMode)
            recent_files_action = KritaAPI.get_action("file_open_recent")
            recent_files_native_actions = [
                "no_entries",
                "separator",
                "clear_action"
            ]
            for item in recent_files_action.menu().actions():
                if item.objectName() not in recent_files_native_actions:
                    item.setVisible(not config.Styles_PrivacyMode)
        #endregion

    #endregion


    



    