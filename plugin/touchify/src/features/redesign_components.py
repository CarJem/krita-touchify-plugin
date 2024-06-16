from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..variables import *
from ..config import *
from ..components.nu_tools.NtToolbox import NtToolbox
from ..components.nu_tools.NtToolOptions import NtToolOptions
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class RedesignComponents:

    usesFlatTheme = False
    usesBorderlessToolbar = False
    usesThinDocumentTabs = False
    usesNuToolbox = False
    usesNuToolOptions = False
    ntTB = None
    ntTO = None

    def createActions(self, window, mainMenuBar):
        actions = []

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_TOOLBAR_BORDER, "Borderless Toolbars", ""))
        actions[0].setCheckable(True)
        actions[0].setChecked(self.usesBorderlessToolbar) 
        actions[0].toggled.connect(self.toolbarBorderToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_TAB_HEIGHT, "Thin Document Tabs", ""))
        actions[1].setCheckable(True)
        actions[1].setChecked(self.usesThinDocumentTabs)
        actions[1].toggled.connect(self.tabHeightToggled)

        #actions.append(window.createAction(TOUCHIFY_ID_ACTION_NU_TOOL_OPTIONS, "Use flat theme", ""))
        #actions[2].setCheckable(True)
        #actions[2].setChecked(self.usesFlatTheme)
        #actions[2].toggled.connect(self.flatThemeToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_NU_TOOLBOX, "NuToolbox", ""))
        actions[2].setCheckable(True)
        actions[2].setChecked(self.usesNuToolbox)
        actions[2].toggled.connect(self.nuToolboxToggled)

        actions.append(window.createAction(TOUCHIFY_ID_ACTION_NU_TOOL_OPTIONS, "NuToolOptions", ""))
        actions[3].setCheckable(True)
        if KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true":
            actions[3].setChecked(self.usesNuToolOptions)
        actions[3].toggled.connect(self.nuToolOptionsToggled)

        for a in actions:
            mainMenuBar.addAction(a)

        stylesheet.buildFlatTheme()
        
        if (self.usesNuToolOptions 
            and KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true"):
                self.ntTO = NtToolOptions(window)

        if self.usesNuToolbox: 
            self.ntTB = NtToolbox(window)

        self.rebuildStyleSheet(window.qwindow())

    def setup(self):
        #if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_FLAT_THEME, "true") == "true":
            #self.usesFlatTheme = True
        self.usesFlatTheme = False

        if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_BORDERLESS_TOOLBAR, "true") == "true":
            self.usesBorderlessToolbar = True

        if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_THIN_DOC_TABS, "true") == "true":
            self.usesThinDocumentTabs = True

        if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_NU_TOOLBOX, "true") == "true":
            self.usesNuToolbox = True
        
        if KritaSettings.readSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_NU_TOOL_OPTIONS, "true") == "true":
            self.usesNuToolOptions = True


    def toolbarBorderToggled(self, toggled):
        KritaSettings.writeSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_BORDERLESS_TOOLBAR, str(toggled).lower())

        self.usesBorderlessToolbar = toggled

        self.rebuildStyleSheet(Krita.instance().activeWindow().qwindow())

    def flatThemeToggled(self, toggled):
        KritaSettings.writeSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_FLAT_THEME, str(toggled).lower())

        self.usesFlatTheme = toggled

        self.rebuildStyleSheet(Krita.instance().activeWindow().qwindow())

    def tabHeightToggled(self, toggled):
        KritaSettings.writeSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_THIN_DOC_TABS, str(toggled).lower())

        self.usesThinDocumentTabs = toggled

        self.rebuildStyleSheet(Krita.instance().activeWindow().qwindow())

    def nuToolboxToggled(self, toggled):
        KritaSettings.writeSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_NU_TOOLBOX, str(toggled).lower())
        self.usesNuToolbox = toggled

        if toggled:
            self.ntTB = NtToolbox(Krita.instance().activeWindow())
            self.ntTB.pad.show() 
            self.ntTB.updateStyleSheet()
        elif not toggled and self.ntTB:
            self.ntTB.close()
            self.ntTB = None

    def nuToolOptionsToggled(self, toggled):
        if KritaSettings.readSetting(KRITA_ID_OPTIONSROOT_MAIN, KRITA_ID_OPTIONS_TOOLOPTIONS_IN_DOCKER, "false") == "true":
            KritaSettings.writeSetting(TOUCHIFY_ID_OPTIONSROOT_MAIN, TOUCHIFY_ID_OPTIONS_NU_TOOL_OPTIONS, str(toggled).lower())
            self.usesNuToolOptions = toggled

            if toggled:
                self.ntTO = NtToolOptions(Krita.instance().activeWindow())
                self.ntTO.pad.show() 
                self.ntTO.updateStyleSheet()
            elif not toggled and self.ntTO:
                self.ntTO.close()
                self.ntTO = None
        else:
            msg = QMessageBox()
            msg.setText("nuTools requires the Tool Options Location to be set to 'In Docker'. \n\n" +
                        "This setting can be found at Settings -> Configure Krita... -> General -> Tools -> Tool Options Location." +
                        "Once the setting has been changed, please restart Krita.")
            msg.exec_()

    def rebuildStyleSheet(self, window):
        full_style_sheet = ""
        
        # Dockers
        if self.usesFlatTheme:
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
        if self.usesFlatTheme:
            full_style_sheet += f"\n {stylesheet.flat_toolbar_style} \n"
        elif self.usesBorderlessToolbar:
            full_style_sheet += f"\n {stylesheet.no_borders_style} \n"    
        
        window.setStyleSheet(full_style_sheet)

        #print("\n\n")
        #print(full_style_sheet)
        #print("\n\n")

        # Overview
        overview = window.findChild(QWidget, KRITA_ID_DOCKER_OVERVIEW)
        overview_style = ""

        if self.usesFlatTheme:
            overview_style += f"\n {stylesheet.flat_overview_docker_style} \n"

        overview.setStyleSheet(overview_style)

        # For document tab
        canvas_style_sheet = ""

        if self.usesFlatTheme:
            if self.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.flat_tab_small_style} \n"
            else: 
                canvas_style_sheet += f"\n {stylesheet.flat_tab_big_style} \n"
        else: 
            if self.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {stylesheet.small_tab_style} \n"

        canvas = window.centralWidget()
        canvas.setStyleSheet(canvas_style_sheet)

        # This is ugly, but it's the least ugly way I can get the canvas to 
        # update it's size (for now)
        canvas.resize(canvas.sizeHint())

        # Update Tool Options stylesheet
        if self.usesNuToolOptions and self.ntTO:
            self.ntTO.updateStyleSheet()

        # Update Toolbox stylesheet
        if self.usesNuToolbox and self.ntTB:
            self.ntTB.updateStyleSheet()  
