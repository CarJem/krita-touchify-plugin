from PyQt5.QtWidgets import *
from touchify.src.components.krita.extensions import KritaExtensions
from touchify.src.managers.shared.resources import ResourceManager
from touchify.variables import *
from touchify.src.managers.shared.settings import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...window import TouchifyWindow


from krita import *

SMALL_TAB_SIZE = 22
SMALL_TAB_ICON_SIZE = 12
SMALL_TAB_CLOSE_BUTTON_MARGIN = 2



class TweakManager(QObject):

    def __init__(self, instance: "TouchifyWindow"):
        super().__init__(instance)
        self.appEngine = instance
        self.qWin: QMainWindow | None = None
        self.brush_editor_tweak: Tweak_BrushEditor | None = None

    #region Signals

    def Window_Load(self):
        Krita.instance().action("show_brush_editor").triggered.connect(self.onBrushEditorTrigged)
        self.qWin = self.appEngine.krita_window.qwindow()
        self.qWin.themeChanged.connect(self.rebuildStyleSheet)
        self.brush_editor_tweak = Tweak_BrushEditor(self.qWin, self.appEngine)

        self.rebuildStyleSheet()

    def onBrushEditorTrigged(self):
        self.brush_editor_tweak.Update_State()

    #endregion

    #region Actions

    def Actions_Init(self, window: Window, path: str):

        def createAction(id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
            result = window.createAction(id, text, menuLocation)
            result.setCheckable(setCheckable)
            result.setChecked(setChecked)
            result.toggled.connect(onToggled)
            return result
    
        config = TouchifySettings.instance().preferences()

        nu_options_menu = QMenu("Tweaks", window.qwindow())
        options_action = window.createAction(TOUCHIFY_ID_ACTION_STYLES_MENU, "Tweaks", path)
        options_action.setMenu(nu_options_menu)
        sublocation_path = "{0}/{1}".format(path, TOUCHIFY_ID_ACTION_STYLES_MENU)

        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_PRIVACYMODE, "Privacy Mode", sublocation_path, True, config.Styles_PrivacyMode, self.privacyModeToggled))        
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_BORDERLESSTOOLBARS, "Borderless Toolbars", sublocation_path, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_TABHEIGHT, "Thin Document Tabs", sublocation_path, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_DOCKEDBRUSHEDITOR, "Docked Brush Editor", sublocation_path, True, config.Styles_DockedBrushEditor, self.dockedBrushEditorToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_DOCKEDBRUSHEDITORZOOMFIX, "Brush Editor Zoom Fix", sublocation_path, True, config.Styles_BrushEditorZoomFix, self.brushEditorZoomFixToggled))

    def Actions_Post(self):
        settings_menu = self.qWin.findChild(QMenu, 'settings')
        KritaExtensions.moveActionTo(TOUCHIFY_ID_ACTION_STYLES_MENU, settings_menu, settings_menu, 'style_menu')

    #endregion

    #region Toggles

    def brushEditorZoomFixToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_BrushEditorZoomFix = toggled
        TouchifySettings.instance().preferences().save()
        self.brush_editor_tweak.Update_State()

    def dockedBrushEditorToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_DockedBrushEditor = toggled
        TouchifySettings.instance().preferences().save()
        self.brush_editor_tweak.Update_State()

    def toolbarBorderToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_BorderlessToolbar = toggled
        TouchifySettings.instance().preferences().save()
        self.qWin.themeChanged.emit()

    def tabHeightToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_ThinDocumentTabs = toggled
        TouchifySettings.instance().preferences().save()
        self.qWin.themeChanged.emit()
        
    def privacyModeToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_PrivacyMode = toggled
        TouchifySettings.instance().preferences().save()
        self.qWin.themeChanged.emit()

    #endregion

    #region Methods

    def rebuildStyleSheet(self):
        if self.qWin == None:
            return

        config = TouchifySettings.instance().preferences()

        # region No Toolbar Borders
        full_style_sheet = ""
        if config.Styles_BorderlessToolbar:
            full_style_sheet += f"\n QToolBar {{ border: none; }} \n"    
        self.qWin.setStyleSheet(full_style_sheet)
        #endregion

        # region Small Tabs
        canvas_style_sheet = ""
        
        if config.Styles_ThinDocumentTabs:
            canvas_style_sheet += f"""\n 
            QTabBar {{ icon-size: {SMALL_TAB_ICON_SIZE}px {SMALL_TAB_ICON_SIZE}px; }}
            QTabBar::tab {{ height: {SMALL_TAB_SIZE}px;  }} 
            QTabBar::close-button {{ margin: {SMALL_TAB_CLOSE_BUTTON_MARGIN}px; }} 
            \n"""

        canvas = self.qWin.centralWidget()
        if canvas:
            canvas.setStyleSheet(canvas_style_sheet)
            canvas.adjustSize()
        # endregion
        
        # region Privacy Mode
        recentDocumentsListView = self.qWin.findChild(QListView,'recentDocumentsListView')
        if recentDocumentsListView:
            recentDocumentsListView.setHidden(config.Styles_PrivacyMode)
            recent_files_action = Krita.instance().action("file_open_recent")
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


class Tweak_BrushEditor_Container(QWidget):
    def __init__(self, parent: QStackedWidget, tweak: "Tweak_BrushEditor", editor: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setContentsMargins(0,0,0,0)

        self.Stack = parent
        self.Tweak = tweak

        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.setSpacing(0)
        self.setLayout(self.lay)

        self.close_action = QAction(self)
        self.close_action.setIcon(ResourceManager.kritaIcon("window-close"))
        self.close_action.setText("Close")
        self.close_action.setToolTip("Close")
        self.close_action.triggered.connect(self.OnEvent_Close) 

        self.toolbar = QToolBar(self)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolbar.addAction(self.close_action)
        self.lay.addWidget(self.toolbar)

        self.OnEvent_Show(editor)

    def OnEvent_Close(self):
        self.editor.setParent(self.__widget_last_parent)
        self.editor.setWindowFlags(self.__widget_last_winflags)

        self.Stack.removeWidget(self)
        self.Tweak.stack_docker = None
        self.close()

    def OnEvent_Show(self, editor: QWidget):
        self.editor = editor
        self.__widget_last_parent = editor.parent()
        self.__widget_last_winflags = editor.windowFlags()
        self.lay.addWidget(editor)


class Tweak_BrushEditor(QObject):

    def __init__(self, qWin: QMainWindow, instance: "TouchifyWindow"):
        self.appEngine = instance
        self.qWin = qWin

        self.stack_docker: Tweak_BrushEditor_Container | None = None
        self.stack_index: int | None = None

    def Get_DockArea(self) -> QStackedWidget | None:
        mdi_area: QMdiArea = self.qWin.findChild(QMdiArea)
        if not mdi_area: return None

        stack_area: QStackedWidget = mdi_area.parentWidget()
        if not stack_area: return None
        if not isinstance(stack_area, QStackedWidget): return None

        return stack_area

    def Get_Editor(self):
        container = self.qWin.findChild(QWidget, "KisPaintOpPresetsEditor")
        if not container: return None
        if not container.isVisible(): return None

        editor = container.parentWidget()
        if not editor: return None

        return editor

    def Subwindow_Spawn(self):
        if self.stack_docker: return
        
        docking_area = self.Get_DockArea()
        if not docking_area: return None
            
        editor = self.Get_Editor()
        if not editor: return

        self.stack_docker = Tweak_BrushEditor_Container(docking_area, self, editor)
        stack_index = docking_area.addWidget(self.stack_docker)
        docking_area.setCurrentIndex(stack_index)

    def Subwindow_Kill(self):
        if self.stack_docker == None: return
        self.stack_docker.OnEvent_Close()

    def Update_State(self):
        is_docked = TouchifySettings.instance().preferences().Styles_DockedBrushEditor
        fix_zoom = TouchifySettings.instance().preferences().Styles_BrushEditorZoomFix

        if is_docked: self.Subwindow_Spawn()
        else: self.Subwindow_Kill()

        if fix_zoom:
            canvas = self.appEngine.mgr_actions.getCurrentCanvas()
            if canvas: canvas.resetZoom()
    



    