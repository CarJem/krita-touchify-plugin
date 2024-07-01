from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from ..components.nu_tools.NtCanvas import NtCanvas

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance


from krita import *
    
class RedesignComponents(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance
        self.ntCanvas: NtCanvas | None = None

    def windowCreated(self):
        self.qWin = self.appEngine.instanceWindow.qwindow()
        self.ntCanvas.windowCreated(self.appEngine.instanceWindow)

    def createAction(self, window: Window, id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
        result = window.createAction(id, text, menuLocation)
        result.setCheckable(setCheckable)
        result.setChecked(setChecked)
        result.toggled.connect(onToggled)
        return result

    def createActions(self, window: Window, mainMenuBar: QMenuBar):

        config = InternalConfig.instance()
        
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_BORDERLESSTOOLBARS, "Borderless Toolbars", TOUCHIFY_ID_MENU_ROOT, True, config.Styles_BorderlessToolbar, self.toolbarBorderToggled))
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_STYLES_TABHEIGHT, "Thin Document Tabs", TOUCHIFY_ID_MENU_ROOT, True, config.Styles_ThinDocumentTabs, self.tabHeightToggled))

        sublocation_name = "On-Canvas Widgets"
        sublocation_path = TOUCHIFY_ID_MENU_ROOT + "/" + sublocation_name

        nu_options_menu = QtWidgets.QMenu(sublocation_name, mainMenuBar)
        mainMenuBar.addMenu(nu_options_menu)

        nu_options_menu.addSection("Widgets")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLBOX, "Enable Toolbox", sublocation_path, True, config.CanvasWidgets_EnableToolbox, self.nuToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLSHELF, "Enable Toolshelf", sublocation_path, True, config.CanvasWidgets_EnableToolshelf, self.nuToolOptionsToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ENABLETOOLSHELF_ALT, "Enable Toolshelf (Alt.)", sublocation_path, True, config.CanvasWidgets_EnableAltToolshelf, self.nuToolOptionsAltToggled))
        
        nu_options_menu.addSection("Widget Options")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_RIGHTHANDTOOLBOX, "Right Hand Toolbox", sublocation_path, True, config.CanvasWidgets_ToolboxOnRight, self.nuOptionsRightHandToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_CANVAS_ALTTOOLBOXPOSITION, "Alternative Toolbox Position", sublocation_path, True, config.CanvasWidgets_AlternativeToolboxPosition, self.nuOptionsAltToolboxPosToggled))

        self.ntCanvas = NtCanvas(window)
        self.ntCanvas.createActions(window, nu_options_menu, sublocation_path)

    def onKritaConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onKritaConfigUpdate()

    def onConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onConfigUpdate()

    #region Theming Actions
    def toolbarBorderToggled(self, toggled):
        InternalConfig.instance().Styles_BorderlessToolbar = toggled
        InternalConfig.instance().saveSettings()
        self.rebuildStyleSheet(self.qWin)

    def tabHeightToggled(self, toggled):
        InternalConfig.instance().Styles_ThinDocumentTabs = toggled
        InternalConfig.instance().saveSettings()
        self.rebuildStyleSheet(self.qWin)
    #endregion

    #region NuWidgetPad Actions
    def nuToolboxToggled(self, toggled):
        InternalConfig.instance().CanvasWidgets_EnableToolbox = toggled
        InternalConfig.instance().saveSettings()

    def nuToolOptionsToggled(self, toggled):
        InternalConfig.instance().CanvasWidgets_EnableToolshelf = toggled
        InternalConfig.instance().saveSettings()
    
    def nuToolOptionsAltToggled(self, toggled):
        InternalConfig.instance().CanvasWidgets_EnableAltToolshelf = toggled
        InternalConfig.instance().saveSettings()

    def nuOptionsAltToolboxPosToggled(self, toggled):
        InternalConfig.instance().CanvasWidgets_AlternativeToolboxPosition = toggled
        InternalConfig.instance().saveSettings()

    def nuOptionsRightHandToolboxToggled(self, toggled):
        InternalConfig.instance().CanvasWidgets_ToolboxOnRight = toggled
        InternalConfig.instance().saveSettings()
    #endregion

    def rebuildStyleSheet(self, window):

        config = InternalConfig.instance()


        full_style_sheet = ""
        
        # Dockers
        if config.Styles_FlatTheme:
            full_style_sheet += f"\n {stylesheet.flat_dock_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_button_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_main_window_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_menu_bar_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_combo_box_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_status_bar_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_tab_base_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_tree_view_style} \n"
            full_style_sheet += f"\n {stylesheet.flat_tab_base_style} \n"

        # Toolbar
        if config.Styles_FlatTheme:
            full_style_sheet += f"\n {stylesheet.flat_toolbar_style} \n"
        elif config.Styles_BorderlessToolbar:
            full_style_sheet += f"\n {stylesheet.no_borders_style} \n"    
        
        window.setStyleSheet(full_style_sheet)

        #print("\n\n")
        #print(full_style_sheet)
        #print("\n\n")

        # For document tab
        canvas_style_sheet = ""

        if config.Styles_FlatTheme:
            if config.Styles_ThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.flat_tab_small_style} \n"
            else: 
                canvas_style_sheet += f"\n {stylesheet.flat_tab_big_style} \n"
        else: 
            if config.Styles_ThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.small_tab_style} \n"

        canvas = window.centralWidget()
        canvas.setStyleSheet(canvas_style_sheet)

        # This is ugly, but it's the least ugly way I can get the canvas to 
        # update it's size (for now)
        canvas.resize(canvas.sizeHint())

        # Update Toolbox stylesheet
        if config.CanvasWidgets_EnableToolbox and self.ntCanvas:
            self.ntCanvas.updateStyleSheet()  
