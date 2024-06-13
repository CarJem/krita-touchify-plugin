from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from .redesign.nttoolbox import ntToolBox
from .redesign.nttooloptions import ntToolOptions
from . import variables
from PyQt5.QtWidgets import QMessageBox

from .core.ui.settings import *
from .core.tweaks.custom_styles import *
from .core.features.docker_toggles import *
from .core.features.docker_groups import *
from .core.features.popup_buttons import *
from .core.features.workspace_toggles import *

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ext.PyKrita import *
else:
    from krita import *

class Touchify(Extension):

    usesFlatTheme = False
    usesBorderlessToolbar = False
    usesThinDocumentTabs = False
    usesNuToolbox = False
    usesNuToolOptions = False
    ntTB = None
    ntTO = None

    mainMenuBar: QMenuBar = None

    basic_dockers: DockerToggles = None
    docker_groups: DockerGroups = None
    workspace_toggles: WorkspaceToggles = None
    popup_toggles: PopupButtons = None

    def __init__(self, parent):
        super().__init__(parent)
        self.basic_dockers = DockerToggles()
        self.docker_groups = DockerGroups()
        self.workspace_toggles = WorkspaceToggles()
        self.popup_toggles = PopupButtons()

    def setup(self):
        #region Core
        appNotifier  = Krita.instance().notifier()
        appNotifier.windowCreated.connect(self.buildPostLaunchMenus)
        appNotifier.windowCreated.connect(self.buildTweaks)
        #endregion
        #region Redesign
        if Application.readSetting("Redesign", "usesFlatTheme", "true") == "true":
            self.usesFlatTheme = True

        if Application.readSetting("Redesign", "usesBorderlessToolbar", "true") == "true":
            self.usesBorderlessToolbar = True

        if Application.readSetting("Redesign", "usesThinDocumentTabs", "true") == "true":
            self.usesThinDocumentTabs = True

        if Application.readSetting("Redesign", "usesNuToolbox", "true") == "true":
            self.usesNuToolbox = True
        
        if Application.readSetting("Redesign", "usesNuToolOptions", "true") == "true":
            self.usesNuToolOptions = True
        #endregion

    def buildTweaks(self):
        qwin = Krita.instance().activeWindow().qwindow()
        CustomStyles.applyStyles(qwin)

    def createActions(self, window):
        self.mainMenuBar = window.qwindow().menuBar().addMenu("Touchify")

        #region Core
        ConfigManager.init_instance()

        subItemPath = "VaporJem_Actions"

        for i in range(1, 10):
            hotkeyName = "vjt_action" + str(i)
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)
   
        self.basic_dockers.createActions(window, subItemPath)  
        self.docker_groups.createActions(window, subItemPath)     
        self.workspace_toggles.createActions(window, subItemPath)
        self.popup_toggles.createActions(window, subItemPath)
        #endregion

        #region Redesign
        actions = []

        actions.append(window.createAction("toolbarBorder", "Borderless Toolbars", ""))
        actions[0].setCheckable(True)
        actions[0].setChecked(self.usesBorderlessToolbar) 

        actions.append(window.createAction("tabHeight", "Thin Document Tabs", ""))
        actions[1].setCheckable(True)
        actions[1].setChecked(self.usesThinDocumentTabs)

        actions.append(window.createAction("flatTheme", "Use flat theme", ""))
        actions[2].setCheckable(True)
        actions[2].setChecked(self.usesFlatTheme)

        actions.append(window.createAction("nuToolbox", "NuToolbox", ""))
        actions[3].setCheckable(True)
        actions[3].setChecked(self.usesNuToolbox)

        actions.append(window.createAction("nuToolOptions", "NuToolOptions", ""))
        actions[4].setCheckable(True)

        if Application.readSetting("", "ToolOptionsInDocker", "false") == "true":
            actions[4].setChecked(self.usesNuToolOptions)

        for a in actions:
            self.mainMenuBar.addAction(a)

        actions[0].toggled.connect(self.toolbarBorderToggled)
        actions[1].toggled.connect(self.tabHeightToggled)
        actions[2].toggled.connect(self.flatThemeToggled)
        actions[3].toggled.connect(self.nuToolboxToggled)
        actions[4].toggled.connect(self.nuToolOptionsToggled)

        variables.buildFlatTheme()

        if (self.usesNuToolOptions and
            Application.readSetting("", "ToolOptionsInDocker", "false") == "true"):
                self.ntTO = ntToolOptions(window)

        if self.usesNuToolbox: 
            self.ntTB = ntToolBox(window)

        self.rebuildStyleSheet(window.qwindow())
        #endregion

    def buildPostLaunchMenus(self):
        qwin = Krita.instance().activeWindow().qwindow()

        reloadItemsAction = QAction("Reload Known Items...", self.mainMenuBar)
        reloadItemsAction.triggered.connect(self.reloadKnownItems)
        self.mainMenuBar.menuAction().menu().addAction(reloadItemsAction)

        openSettingsAction = QAction("Configure Touchify...", self.mainMenuBar)
        openSettingsAction.triggered.connect(self.openSettings)
        self.mainMenuBar.menuAction().menu().addAction(openSettingsAction)

        seperator = QAction("", self.mainMenuBar)
        seperator.setSeparator(True)
        self.mainMenuBar.addAction(seperator)

        self.basic_dockers.buildMenu(self.mainMenuBar)  
        self.docker_groups.buildMenu(self.mainMenuBar)     
        self.workspace_toggles.buildMenu(self.mainMenuBar)
        self.popup_toggles.buildMenu(self.mainMenuBar)       

    #region Action Triggers

    def toolbarBorderToggled(self, toggled):
        Application.writeSetting("Touchify", "usesBorderlessToolbar", str(toggled).lower())

        self.usesBorderlessToolbar = toggled

        self.rebuildStyleSheet(Application.activeWindow().qwindow())

    def flatThemeToggled(self, toggled):
        Application.writeSetting("Touchify", "usesFlatTheme", str(toggled).lower())

        self.usesFlatTheme = toggled

        self.rebuildStyleSheet(Application.activeWindow().qwindow())

    def tabHeightToggled(self, toggled):
        Application.instance().writeSetting("Touchify", "usesThinDocumentTabs", str(toggled).lower())

        self.usesThinDocumentTabs = toggled

        self.rebuildStyleSheet(Application.activeWindow().qwindow())

    def nuToolboxToggled(self, toggled):
        Application.writeSetting("Touchify", "usesNuToolbox", str(toggled).lower())
        self.usesNuToolbox = toggled

        if toggled:
            self.ntTB = ntToolBox(Application.activeWindow())
            self.ntTB.pad.show() 
            self.ntTB.updateStyleSheet()
        elif not toggled and self.ntTB:
            self.ntTB.close()
            self.ntTB = None

    def nuToolOptionsToggled(self, toggled):
        if Application.readSetting("", "ToolOptionsInDocker", "false") == "true":
            Application.writeSetting("Touchify", "usesNuToolOptions", str(toggled).lower())
            self.usesNuToolOptions = toggled

            if toggled:
                self.ntTO = ntToolOptions(Application.activeWindow())
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
            full_style_sheet += f"\n {variables.flat_dock_style} \n"
            full_style_sheet += f"\n {variables.flat_button_style} \n"
            full_style_sheet += f"\n {variables.flat_main_window_style} \n"
            full_style_sheet += f"\n {variables.flat_menu_bar_style} \n"
            full_style_sheet += f"\n {variables.flat_combo_box_style} \n"
            full_style_sheet += f"\n {variables.flat_status_bar_style} \n"
            full_style_sheet += f"\n {variables.flat_tab_base_style} \n"
            full_style_sheet += f"\n {variables.flat_tree_view_style} \n"
            full_style_sheet += f"\n {variables.flat_tab_base_style} \n"

        # Toolbar
        if self.usesFlatTheme:
            full_style_sheet += f"\n {variables.flat_toolbar_style} \n"
        elif self.usesBorderlessToolbar:
            full_style_sheet += f"\n {variables.no_borders_style} \n"    
        
        window.setStyleSheet(full_style_sheet)

        #print("\n\n")
        #print(full_style_sheet)
        #print("\n\n")

        # Overview
        overview = window.findChild(QWidget, 'OverviewDocker')
        overview_style = ""

        if self.usesFlatTheme:
            overview_style += f"\n {variables.flat_overview_docker_style} \n"

        overview.setStyleSheet(overview_style)

        # For document tab
        canvas_style_sheet = ""

        if self.usesFlatTheme:
            if self.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {variables.flat_tab_small_style} \n"
            else: 
                canvas_style_sheet += f"\n {variables.flat_tab_big_style} \n"
        else: 
            if self.usesThinDocumentTabs:
                canvas_style_sheet += f"\n {variables.small_tab_style} \n"

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

    def reloadKnownItems(self):
        self.basic_dockers.reloadDockers()
        self.workspace_toggles.reloadWorkspaces()
        msg = QMessageBox(Krita.instance().activeWindow().qwindow())
        msg.setText("Reloaded Known Workspaces/Dockers. You will need to reload to use them with this extension")
        msg.exec_()

    def openSettings(self):
        SettingsDialog().show()

    #endregion

Krita.instance().addExtension(Touchify(Krita.instance()))