from PyQt5.QtWidgets import *
from touchify.src.helpers import TouchifyHelpers
from touchify.src.variables import *
from touchify.src.settings import *
from touchify.src.stylesheet import Stylesheet
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..window import TouchifyWindow


from krita import *
    
class TouchifyTweaks(QObject):

    def __init__(self, instance: "TouchifyWindow"):
        super().__init__(instance)
        self.appEngine = instance
        self.qWin: QMainWindow | None = None

    #region Signals

    def Window_Load(self):
        Krita.instance().action("show_brush_editor").triggered.connect(self.onBrushEditorTrigged)
        self.qWin = self.appEngine.krita_window.qwindow()
        self.qWin.themeChanged.connect(self.rebuildStyleSheet)
        qApp.focusWindowChanged.connect(self.onFocusWindowChanged)
        self.rebuildStyleSheet()

    def onBrushEditorTrigged(self):
        self.updateBrushEditor()
    
    def onFocusWindowChanged(self):
        self.updateBrushEditor()

    #endregion

    #region Actions

    def Actions_Init(self, window: Window, subPathName: str):

        def createAction(id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
            result = window.createAction(id, text, menuLocation)
            result.setCheckable(setCheckable)
            result.setChecked(setChecked)
            result.toggled.connect(onToggled)
            return result
    
        config = TouchifySettings.instance().preferences()
        
        sublocation_name = "Tweaks"
        sublocation_path = subPathName + "/" + sublocation_name


        nu_options_menu = QMenu(sublocation_name, window.qwindow())
        options_action = window.createAction(TOUCHIFY_ID_ACTION_STYLES_MENU, sublocation_name, "settings")
        options_action.setMenu(nu_options_menu)

        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_PRIVACYMODE, "Privacy Mode", sublocation_path, True, config.Styles_PrivacyMode, self.privacyModeToggled))        
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_BORDERLESSTOOLBARS, "Borderless Toolbars", sublocation_path, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_TABHEIGHT, "Thin Document Tabs", sublocation_path, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_DOCKEDBRUSHEDITOR, "Docked Brush Editor", sublocation_path, True, config.Styles_DockedBrushEditor, self.dockedBrushEditorToggled))
        nu_options_menu.addAction(createAction(TOUCHIFY_ID_ACTION_STYLES_DOCKEDBRUSHEDITORZOOMFIX, "Brush Editor Zoom Fix", sublocation_path, True, config.Styles_BrushEditorZoomFix, self.brushEditorZoomFixToggled))

    def Actions_Post(self):
        settings_menu = self.qWin.findChild(QMenu, 'settings')
        TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_STYLES_MENU, settings_menu, settings_menu, 'style_menu')

    #endregion

    #region Toggles

    def brushEditorZoomFixToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_BrushEditorZoomFix = toggled
        TouchifySettings.instance().preferences().save()

        self.updateBrushEditor()

    def dockedBrushEditorToggled(self, toggled):
        TouchifySettings.instance().preferences().Styles_DockedBrushEditor = toggled
        TouchifySettings.instance().preferences().save()

        self.updateBrushEditor()

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

    


    def updateBrushEditor(self):
        brushEditorWidget = self.qWin.findChild(QWidget, "KisPaintOpPresetsEditor")
        if not brushEditorWidget: return
        if not brushEditorWidget.isVisible(): return
            
        brushEditorFrame = brushEditorWidget.parentWidget()
        if not brushEditorFrame: return

        parentMdiArea: QMdiArea = self.qWin.findChild(QMdiArea)
        if not parentMdiArea: return
        
        pos = parentMdiArea.mapToGlobal(QPoint(0,0))
        margins = QMargins(2,2,2,2)
        size = parentMdiArea.frameSize().shrunkBy(margins)

        if self.qWin.isMaximized():
            brushEditorFrame.resize(brushEditorFrame.size().shrunkBy(margins))
            
        if TouchifySettings.instance().preferences().Styles_DockedBrushEditor: 
            brushEditorFrame.move(pos)
            brushEditorFrame.resize(size)

        if TouchifySettings.instance().preferences().Styles_BrushEditorZoomFix:
            canvas = self.appEngine.mgr_actions.getCurrentCanvas()
            if canvas: canvas.resetZoom()

    def rebuildStyleSheet(self):
        if self.qWin == None:
            return

        config = TouchifySettings.instance().preferences()

        # region No Toolbar Borders
        full_style_sheet = ""
        if config.Styles_BorderlessToolbar:
            full_style_sheet += f"\n {Stylesheet.instance().no_borders_style} \n"    
        self.qWin.setStyleSheet(full_style_sheet)
        #endregion

        # region Small Tabs
        canvas_style_sheet = ""
        
        if config.Styles_ThinDocumentTabs:
            canvas_style_sheet += f"\n {Stylesheet.instance().small_tab_style} \n"

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