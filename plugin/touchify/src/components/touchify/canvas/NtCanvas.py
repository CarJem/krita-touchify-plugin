from PyQt5.QtWidgets import QMdiArea




from touchify.src.components.touchify.canvas.NtSubWinFilter import NtSubWinFilter

from touchify.src.components.touchify.canvas.NtWorker import NtWorker
from touchify.src.global_events import TouchifyEvents
from touchify.src.helpers import TouchifyHelpers
from touchify.src.settings import TouchifySettings
from krita import *
from PyQt5.QtCore import QObject
from touchify.src.variables import *
from touchify.src.components.krita.settings import KritaSettings
from touchify.src.cfg.widget_layout.WidgetLayout import WidgetLayout
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


class NtCanvas(QWidget):
    def __init__(self, parent: QObject, window: Window):
        super().__init__(parent)

        self.krita_window = window
        self.qWin = None
        self.mdiArea = None

        self.adjustFilter = None
        
        self.windowLoaded = False
        self.app_engine = None

        self.toolbox = None
        self.toolshelf_beta = None
        self.toolshelf_alpha = None
        self.toolshelf_gamma = None
        self.toolshelf_delta = None

        self.toolshelf_count = 0
        self.toolbox_enabled = False

        self.selected_preset_id = None

        self.presetsMenu = QMenu("Canvas Layouts...")
        self.presetsMenu.aboutToShow.connect(self.buildPresetMenu)

        self.canvasLayout = QGridLayout(self)
        self.canvasLayout.setContentsMargins(0,0,0,0)
        self.canvasLayout.setSpacing(0)
        self.setLayout(self.canvasLayout)

        self.reloadActivePreset()

    #region States

    def isEmpty(self):
        if self.toolbox: return False
        elif self.toolshelf_alpha: return False
        elif self.toolshelf_beta: return False
        elif self.toolshelf_gamma: return False
        elif self.toolshelf_delta: return False
        else: return True

    #endregion

    #region Setup Stuff
    def windowCreated(self, app_engine: "TouchifyWindow"):
        self.app_engine = app_engine

        Krita.instance().action("view_ruler").triggered.connect(self.updateView)


        self.krita_window = self.app_engine.windowSource
        self.qWin = self.krita_window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)

        self.adjustFilter = NtSubWinFilter(self.mdiArea)
        self.adjustFilter.SIGNAL_EVENT_REQUESTED.connect(self.subWindowEvent)
        self.adjustFilter.setTargetWidget(self)
        self.qWin.installEventFilter(self.adjustFilter)
        self.setParent(self.mdiArea)

        TouchifyEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.reloadActivePreset)
        TouchifyEvents.instance().SIGNAL_CANVAS_LAYOUT_CHANGED.connect(self.reloadActivePreset)

        self.windowLoaded = True

        self.updateElements()

    def finishMenuActions(self):
        settings_menu = self.qWin.findChild(QMenu, 'settings')

        layoutsMenuAction = TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_WIDGETPAD_MENU, settings_menu, settings_menu, 'toolbars_submenu_action')
        optionsMenuAction = TouchifyHelpers.moveActionTo(TOUCHIFY_ID_ACTION_WIDGETPAD_PRESETS_MENU, settings_menu, settings_menu, 'toolbars_submenu_action')
        seperator = settings_menu.insertSeparator(optionsMenuAction)

    def createMenuActions(self, window: Window, menu: QMenuBar): 



        layouts_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_PRESETS_MENU, "Configure Layout...", "settings")
        layouts_action.setIcon(Krita.instance().icon("configure"))
        layouts_action.setMenu(self.presetsMenu)

        optionsMenu = QMenu("Widgets Shown", window.qwindow())
        options_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_MENU, "Widgets Shown", "settings")
        options_action.setMenu(optionsMenu)



        show_toolbox = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolbox"), True)
        show_toolshelf_alpha = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_alpha"), True)
        show_toolshelf_beta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_beta"), True)
        show_toolshelf_gamma = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_gamma"), True)
        show_toolshelf_delta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_delta"), True)


        self.tlb_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_SHOWTOOLBOX, "Toolbox", "")
        self.tlb_action.triggered.connect(lambda a: self.updateActions("toolbox", a))
        self.tlb_action.setCheckable(True)
        self.tlb_action.setChecked(show_toolbox)
        optionsMenu.addAction(self.tlb_action)

        self.tlshlf_alpha_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_SHOWTOOLSHELF_ALPHA, "Toolshelf (Alpha)", "")
        self.tlshlf_alpha_action.triggered.connect(lambda a: self.updateActions("toolshelf_alpha", a))
        self.tlshlf_alpha_action.setCheckable(True)
        self.tlshlf_alpha_action.setChecked(show_toolshelf_alpha)
        optionsMenu.addAction(self.tlshlf_alpha_action)

        self.tlshlf_beta_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_SHOWTOOLSHELF_BETA, "Toolshelf (Beta)", "")
        self.tlshlf_beta_action.triggered.connect(lambda a: self.updateActions("toolshelf_beta", a))
        self.tlshlf_beta_action.setCheckable(True)
        self.tlshlf_beta_action.setChecked(show_toolshelf_beta)
        optionsMenu.addAction(self.tlshlf_beta_action)

        self.tlshlf_gamma_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_SHOWTOOLSHELF_GAMMA, "Toolshelf (Gamma)", "")
        self.tlshlf_gamma_action.triggered.connect(lambda a: self.updateActions("toolshelf_gamma", a))
        self.tlshlf_gamma_action.setCheckable(True)
        self.tlshlf_gamma_action.setChecked(show_toolshelf_gamma)
        optionsMenu.addAction(self.tlshlf_gamma_action)

        self.tlshlf_delta_action = window.createAction(TOUCHIFY_ID_ACTION_WIDGETPAD_SHOWTOOLSHELF_DELTA, "Toolshelf (Delta)", "")
        self.tlshlf_delta_action.triggered.connect(lambda a: self.updateActions("toolshelf_delta", a))
        self.tlshlf_delta_action.setCheckable(True)
        self.tlshlf_delta_action.setChecked(show_toolshelf_delta)
        optionsMenu.addAction(self.tlshlf_delta_action)
    #endregion

    #region Preset Functions

    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                TouchifySettings.instance().setActiveWidgetLayout(id)

    def buildPresetMenu(self):
        self.presetsMenu.clear()
        menus: dict[str, QMenu] = {}
        index = 0
        registry = TouchifySettings.instance().getRegistry(WidgetLayout)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = self.presetsMenu.addMenu(key.name)
                preset: WidgetLayout
                action = QAction(preset.preset_name, self.presetsMenu)
                action.setCheckable(True)
                if self.selected_preset_id == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.changePreset)
                index += 1
                
                menus[key.id].addAction(action)

    def reloadActivePreset(self):

        last_preset_id = self.selected_preset_id
        self.active_preset: WidgetLayout = TouchifySettings.instance().getActiveWidgetLayout()
        self.selected_preset_id = TouchifySettings.instance().getActiveWidgetLayoutId()

        self.toolshelf_count = self.active_preset.toolshelf_count
        self.toolbox_enabled = self.active_preset.toolbox_enabled
        
        if last_preset_id != self.selected_preset_id:
            KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", self.selected_preset_id)
        
        if self.toolbox: 
            self.toolbox.toolbox.toolboxWidget.setHorizontalMode(self.active_preset.toolbox.horizontal_mode)

        self.updateElements(True)

    #endregion

    #region Event Functions

    def subWindowEvent(self):
        self.updateView()

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        self.updateView()

    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)
            
    #endregion

    #region Update Functions


    def updateStart(self, mode: str, args: dict = {}):

        if hasattr(self, "thread_packer"):
            if self.thread_packer.isRunning(): return

        # Thread
        self.thread_packer = QThread()
        # Worker
        self.worker_packer = NtWorker()
        self.worker_packer.moveToThread( self.thread_packer )
        # Thread
        self.thread_packer.started.connect( lambda : self.worker_packer.run( self, mode, args ) )
        self.thread_packer.start()

    def updateElements(self, full_unload: bool = False):
        if self.windowLoaded == False:
            return
        if full_unload: self.updateStart("LOAD_ELEMENTS")
        else: self.updateStart("RELOAD_ELEMENTS")

    def updateView(self):
        self.updateStart("VIEW")

    def updateActions(self, pad: str = "", value: bool = None):
        self.updateStart("ACTIONS", {"pad": pad, "value": value})
        
    def mouseMoveEvent(self, a0):
        if self.toolbox: self.toolbox.updateCursor()
        if self.toolshelf_alpha: self.toolshelf_alpha.updateCursor()
        if self.toolshelf_beta: self.toolshelf_beta.updateCursor()
        if self.toolshelf_gamma: self.toolshelf_gamma.updateCursor()
        if self.toolshelf_delta: self.toolshelf_delta.updateCursor()


        

    #endregion


