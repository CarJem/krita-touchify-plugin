from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from ..settings.TouchifySettings import TouchifySettings
from ..variables import *
from ..settings.TouchifyConfig import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance


from krita import *
    
class TouchifyLooks(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance

    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()

    def createAction(self, window: Window, id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
        result = window.createAction(id, text, menuLocation)
        result.setCheckable(setCheckable)
        result.setChecked(setChecked)
        result.toggled.connect(onToggled)
        return result

    def createActions(self, window: Window, mainMenuBar: QMenuBar):
        config = TouchifySettings.instance()
        
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_BORDERLESSTOOLBARS, "Borderless Toolbars", TOUCHIFY_ID_MENU_ROOT, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_TABHEIGHT, "Thin Document Tabs", TOUCHIFY_ID_MENU_ROOT, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))

    def toolbarBorderToggled(self, toggled):
        TouchifySettings.instance().Styles_BorderlessToolbar = toggled
        TouchifySettings.instance().saveSettings()
        self.rebuildStyleSheet(self.qWin)

    def tabHeightToggled(self, toggled):
        TouchifySettings.instance().Styles_ThinDocumentTabs = toggled
        TouchifySettings.instance().saveSettings()
        self.rebuildStyleSheet(self.qWin)

    def rebuildStyleSheet(self, window: QMainWindow):
        config = TouchifySettings.instance()

        full_style_sheet = ""

        if config.Styles_BorderlessToolbar:
            full_style_sheet += f"\n {stylesheet.no_borders_style} \n"    
        
        window.setStyleSheet(full_style_sheet)


        # For document tab
        canvas_style_sheet = ""
        
        if config.Styles_ThinDocumentTabs:
            canvas_style_sheet += f"\n {stylesheet.small_tab_style} \n"

        canvas = window.centralWidget()
        canvas.setStyleSheet(canvas_style_sheet)
        canvas.adjustSize()
