from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from ..components.nu_tools.NtCanvas import NtCanvas

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class RedesignComponents:

    ntCanvas = None


    def createAction(self, window: Window, id: str, text: str, menuLocation: str, setCheckable: bool, setChecked: bool, onToggled: any):
        result = window.createAction(id, text, menuLocation)
        result.setCheckable(setCheckable)
        result.setChecked(setChecked)
        result.toggled.connect(onToggled)
        return result

    def createActions(self, window: Window, mainMenuBar: QMenuBar):

        config = InternalConfig.instance()
        
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_TOOLBAR_BORDER, "Borderless Toolbars", TOUCHIFY_ID_MENU_ROOT, True, config.usesBorderlessToolbar, self.toolbarBorderToggled))
        mainMenuBar.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_TAB_HEIGHT, "Thin Document Tabs", TOUCHIFY_ID_MENU_ROOT, True, config.usesThinDocumentTabs, self.tabHeightToggled))

        sublocation_name = "On-Canvas Widgets"
        sublocation_path = TOUCHIFY_ID_MENU_ROOT + "/" + sublocation_name

        nu_options_menu = QtWidgets.QMenu(sublocation_name, mainMenuBar)
        mainMenuBar.addMenu(nu_options_menu)

        nu_options_menu.addSection("Widgets")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_NU_TOOLBOX, "Enable Toolbox", sublocation_path, True, config.usesNuToolbox, self.nuToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_NU_TOOL_OPTIONS, "Enable Toolshelf", sublocation_path, True, config.usesNuToolOptions, self.nuToolOptionsToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_ACTION_NU_TOOL_OPTIONS_ALT, "Enable Toolshelf (Alt.)", sublocation_path, True, config.usesNuToolOptionsAlt, self.nuToolOptionsAltToggled))
        
        nu_options_menu.addSection("Widget Options")
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_OPTIONS_NU_OPTIONS_RIGHT_HAND_TOOLBOX, "Right Hand Toolbox", sublocation_path, True, config.nuOptions_ToolboxOnRight, self.nuOptionsRightHandToolboxToggled))
        nu_options_menu.addAction(self.createAction(window, TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, "Alternative Toolbox Position", sublocation_path, True, config.nuOptions_AlternativeToolboxPosition, self.nuOptionsAltToolboxPosToggled))

        self.ntCanvas = NtCanvas(window)
        self.ntCanvas.createActions(window, nu_options_menu, sublocation_path)

    def windowCreated(self, window: Window):
        self.ntCanvas.updateWindow(window)

    def onKritaConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onKritaConfigUpdate()

    def onConfigUpdated(self):
        if self.ntCanvas:
            self.ntCanvas.onConfigUpdate()

    #region Theming Actions
    def toolbarBorderToggled(self, toggled):
        InternalConfig.instance().usesBorderlessToolbar = toggled
        InternalConfig.instance().saveSettings()
        self.rebuildStyleSheet(Krita.instance().activeWindow().qwindow())

    def tabHeightToggled(self, toggled):
        InternalConfig.instance().usesThinDocumentTabs = toggled
        InternalConfig.instance().saveSettings()
        self.rebuildStyleSheet(Krita.instance().activeWindow().qwindow())
    #endregion

    #region NuWidgetPad Actions
    def nuToolboxToggled(self, toggled):
        InternalConfig.instance().usesNuToolbox = toggled
        InternalConfig.instance().saveSettings()

    def nuToolOptionsToggled(self, toggled):
        InternalConfig.instance().usesNuToolOptions = toggled
        InternalConfig.instance().saveSettings()
    
    def nuToolOptionsAltToggled(self, toggled):
        InternalConfig.instance().usesNuToolOptionsAlt = toggled
        InternalConfig.instance().saveSettings()

    def nuOptionsAltToolboxPosToggled(self, toggled):
        InternalConfig.instance().nuOptions_AlternativeToolboxPosition = toggled
        InternalConfig.instance().saveSettings()

    def nuOptionsRightHandToolboxToggled(self, toggled):
        InternalConfig.instance().nuOptions_ToolboxOnRight = toggled
        InternalConfig.instance().saveSettings()
    #endregion

    def rebuildStyleSheet(self, window):

        config = InternalConfig.instance()


        full_style_sheet = ""
        
        # Dockers
        if config.usesFlatTheme:
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
        if config.usesFlatTheme:
            full_style_sheet += f"\n {stylesheet.flat_toolbar_style} \n"
        elif config.usesBorderlessToolbar:
            full_style_sheet += f"\n {stylesheet.no_borders_style} \n"    
        
        window.setStyleSheet(full_style_sheet)

        #print("\n\n")
        #print(full_style_sheet)
        #print("\n\n")

        # Overview
        overview = window.findChild(QWidget, KRITA_ID_DOCKER_OVERVIEW)
        overview_style = ""

        if config.usesFlatTheme:
            overview_style += f"\n {stylesheet.flat_overview_docker_style} \n"

        overview.setStyleSheet(overview_style)

        # For document tab
        canvas_style_sheet = ""

        if config.usesFlatTheme:
            if config.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.flat_tab_small_style} \n"
            else: 
                canvas_style_sheet += f"\n {stylesheet.flat_tab_big_style} \n"
        else: 
            if config.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.small_tab_style} \n"

        canvas = window.centralWidget()
        canvas.setStyleSheet(canvas_style_sheet)

        # This is ugly, but it's the least ugly way I can get the canvas to 
        # update it's size (for now)
        canvas.resize(canvas.sizeHint())

        # Update Toolbox stylesheet
        if config.usesNuToolbox and self.ntCanvas:
            self.ntCanvas.updateStyleSheet()  
