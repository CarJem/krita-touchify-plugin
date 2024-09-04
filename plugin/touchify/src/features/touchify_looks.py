from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from ..settings.TouchifySettings import TouchifySettings
from ..variables import *
from ..settings.TouchifyConfig import *
from ..stylesheet import Stylesheet
from PyQt5.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import Touchify


from krita import *
    
class TouchifyLooks(object):

    def __init__(self, instance: "Touchify"):
        self.appEngine = instance
        self.qWin: QMainWindow | None = None


    def windowCreated(self):
        self.qWin = self.appEngine.windowSource.qwindow()
        self.qWin.themeChanged.connect(self.rebuildStyleSheet)
        self.rebuildStyleSheet()

    def createAction(self, window: Window, id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
        result = window.createAction(id, text, menuLocation)
        result.setCheckable(setCheckable)
        result.setChecked(setChecked)
        result.toggled.connect(onToggled)
        return result

    def createActions(self, window: Window, mainMenuBar: QMenuBar):
        config = TouchifySettings.instance()
        
        sublocation_name = "Styles and Tweaks"
        sublocation_path = TOUCHIFY_ID_MENU_ROOT + "/" + sublocation_name

        nu_options_menu = QtWidgets.QMenu(sublocation_name, mainMenuBar)
        mainMenuBar.addMenu(nu_options_menu)

        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_PRIVACYMODE, "Privacy Mode", sublocation_path, True, config.Styles_PrivacyMode, self.privacyModeToggled))        
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_BORDERLESSTOOLBARS, "Borderless Toolbars", sublocation_path, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_TABHEIGHT, "Thin Document Tabs", sublocation_path, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))

    def toolbarBorderToggled(self, toggled):
        TouchifySettings.instance().Styles_BorderlessToolbar = toggled
        TouchifySettings.instance().saveSettings()
        
        self.qWin.themeChanged.emit()

    def tabHeightToggled(self, toggled):
        TouchifySettings.instance().Styles_ThinDocumentTabs = toggled
        TouchifySettings.instance().saveSettings()
        self.qWin.themeChanged.emit()
        
    def privacyModeToggled(self, toggled):
        TouchifySettings.instance().Styles_PrivacyMode = toggled
        TouchifySettings.instance().saveSettings()
        self.qWin.themeChanged.emit()

    def rebuildStyleSheet(self):
        if self.qWin == None:
            return

        config = TouchifySettings.instance()

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
