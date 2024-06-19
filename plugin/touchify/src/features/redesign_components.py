from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..components.nu_tools.NtToolOptions import NtToolOptions

from ..components.nu_tools.NtToolbox import NtToolbox
from ..components.nu_tools.NtDockers import *

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class RedesignComponents:

    ntToolbox = None
    ntToolOptions = None

    def createActions(self, window, mainMenuBar: QMenuBar):

        config = InternalConfig.instance()

        actions = []

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_TOOLBAR_BORDER, "Borderless Toolbars", ""))
        actions[0].setCheckable(True)
        actions[0].setChecked(config.usesBorderlessToolbar) 
        actions[0].toggled.connect(self.toolbarBorderToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_TAB_HEIGHT, "Thin Document Tabs", ""))
        actions[1].setCheckable(True)
        actions[1].setChecked(config.usesThinDocumentTabs)
        actions[1].toggled.connect(self.tabHeightToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_NU_TOOLBOX, "Show NuToolbox", ""))
        actions[2].setCheckable(True)
        actions[2].setChecked(config.usesNuToolbox)
        actions[2].toggled.connect(self.nuToolboxToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_NU_TOOL_OPTIONS, "Show NuToolOptions", ""))
        actions[3].setCheckable(True)
        if KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true":
            actions[3].setChecked(config.usesNuToolOptions)
        actions[3].toggled.connect(self.nuToolOptionsToggled)

        for a in actions:
            mainMenuBar.addAction(a)

        nu_options_menu = QtWidgets.QMenu("NuOptions", mainMenuBar)
        mainMenuBar.addMenu(nu_options_menu)
        nu_options_actions = []
        

        nu_options_actions.append(window.createAction(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_SHAREDTOOLDOCKER, "Show Tool Options"))
        nu_options_actions[0].setCheckable(True)
        nu_options_actions[0].setChecked(config.nuOptions_SharedToolDocker)
        nu_options_actions[0].toggled.connect(self.nuOptionsSharedToolDockerToggled)

        nu_options_actions.append(window.createAction(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_RIGHT_HAND_TOOLBOX, "Right Hand Toolbox"))
        nu_options_actions[1].setCheckable(True)
        nu_options_actions[1].setChecked(config.nuOptions_ToolboxOnRight)
        nu_options_actions[1].toggled.connect(self.nuOptionsRightHandToolboxToggled)

        nu_options_actions.append(window.createAction(TOUCHIFY_ID_OPTIONS_NU_OPTIONS_ALTERNATIVE_TOOLBOX_POSITION, "Alternative Toolbox Position"))
        nu_options_actions[2].setCheckable(True)
        nu_options_actions[2].setChecked(config.nuOptions_AlternativeToolboxPosition)
        nu_options_actions[2].toggled.connect(self.nuOptionsAltToolboxPosToggled)

        for a in nu_options_actions:
            nu_options_menu.addAction(a)


        self.build(window)

    def build(self, window):
        stylesheet.buildFlatTheme()
        
        if (InternalConfig.instance().usesNuToolOptions 
            and KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true"):
                self.ntToolOptions = NtToolOptions(window)

        if InternalConfig.instance().usesNuToolbox: 
            self.ntToolbox = NtToolbox(window)
            
        self.rebuildStyleSheet(window.qwindow())


    def onKritaConfigUpdated(self):
        if self.ntToolOptions:
            self.ntToolOptions.onKritaConfigUpdate()
        if self.ntToolbox:
            self.ntToolbox.onKritaConfigUpdate()

    def onConfigUpdated(self):
        if self.ntToolOptions:
            self.ntToolOptions.onConfigUpdate()
        if self.ntToolbox:
            self.ntToolbox.onConfigUpdate()



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

        if toggled:
            self.ntToolbox = NtToolbox(Krita.instance().activeWindow())
            self.ntToolbox.show() 
            self.ntToolbox.updateStyleSheet()
        elif not toggled:
            if self.ntToolbox:
                self.ntToolbox.close()
                self.ntToolbox = None

    def nuToolOptionsToggled(self, toggled):
        InternalConfig.instance().usesNuToolOptions = toggled
        InternalConfig.instance().saveSettings()

        if toggled:

            self.ntToolOptions = NtToolOptions(Krita.instance().activeWindow())
            self.ntToolOptions.show() 
            self.ntToolOptions.updateStyleSheet()

        elif not toggled:

            if self.ntToolOptions:
                self.ntToolOptions.close()
                self.ntToolOptions = None
    #endregion

    #region NuOptions Actions
    def nuOptionsSharedToolDockerToggled(self, toggled):
        if KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true":
            InternalConfig.instance().nuOptions_SharedToolDocker = toggled
            InternalConfig.instance().saveSettings()
        else:
            msg = QMessageBox()
            msg.setText("This setting requires the Tool Options Location to be set to 'In Docker'. \n\n" +
                        "This setting can be found at Settings -> Configure Krita... -> General -> Tools -> Tool Options Location." +
                        "Once the setting has been changed, please restart Krita.")
            msg.exec_()

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

        # Update Tool Options stylesheet
        if config.usesNuToolOptions and self.ntToolOptions:
            self.ntToolOptions.updateStyleSheet()

        # Update Toolbox stylesheet
        if config.usesNuToolbox and self.ntToolbox:
            self.ntToolbox.updateStyleSheet()  
