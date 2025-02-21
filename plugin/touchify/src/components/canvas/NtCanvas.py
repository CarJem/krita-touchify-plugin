from PyQt5.QtWidgets import QMdiArea





from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.canvas.NtToolbox import NtToolbox
from touchify.src.components.canvas.NtToolshelf import NtToolshelf
from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad
from touchify.src.components.canvas.NtWorker import NtWorker
from touchify.src.managers.shared.events import GlobalEvents
from touchify.src.extensions.krita_extensions import KritaExtensions
from touchify.src.managers.shared.settings import TouchifySettings
from krita import *
from touchify.src.api_krita import KritaAPI
from PyQt5.QtCore import QObject
from touchify.__env__ import *
from touchify.src.managers.shared.settings_krita import KritaSettings
from touchify.src.config.widget_layout.WidgetLayout import WidgetLayout
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow


class NtCanvas(QWidget):
    def __init__(self, parent: QObject, window: WindowAPI):
        super().__init__(parent)
        self.Variables_Init(window)
        self.Components_Init()
        self.Connections_Init()
        self.Preset_Reload()

    #region Init Functions

    def Variables_Init(self, window: WindowAPI):
        self.__window_loaded = False
        self.__krita_window = window
        self.__mdi_area = None

        self.adjust_filter = None
        
        self.app_engine = None

        self.toolbox: NtToolbox = None
        self.toolshelf_beta: NtToolshelf = None
        self.toolshelf_alpha: NtToolshelf = None
        self.toolshelf_gamma: NtToolshelf = None
        self.toolshelf_delta: NtToolshelf = None

        self.toolshelf_count = 0
        self.toolbox_enabled = False

        self.selected_preset_id = None
    
    def Components_Init(self):
        self.presetsMenu = QMenu("Canvas Layouts...")

        self.canvasLayout = QGridLayout(self)
        self.canvasLayout.setContentsMargins(0,0,0,0)
        self.canvasLayout.setSpacing(0)
        self.setLayout(self.canvasLayout)
    
    def Connections_Init(self):
        self.presetsMenu.aboutToShow.connect(self.Preset_Menu)
    
    def Actions_Init(self, window: WindowAPI, subItemPath: str): 
        layouts_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_PRESETS_MENU, "Configure Layout...", subItemPath)
        layouts_action.setIcon(KritaAPI.get_icon("configure"))
        layouts_action.setMenu(self.presetsMenu)

        options_menu = QMenu("Widgets Shown", window.qwindow())
        options_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_MENU, "Widgets Shown", subItemPath)
        options_action.setMenu(options_menu)


        menu_path = ""

        self.tlb_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLBOX, "Toolbox", menu_path)
        self.tlb_action.setCheckable(True)
        self.tlb_action.setChecked(KritaSettings.readSettingBool(TOUCHIFY_SETTINGPATH_WIDGETPAD, "show_{0}".format("toolbox"), True))

        self.tlshlf_alpha_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_ALPHA, "Toolshelf (Alpha)", menu_path)
        self.tlshlf_alpha_action.setCheckable(True)
        self.tlshlf_alpha_action.setChecked(KritaSettings.readSettingBool(TOUCHIFY_SETTINGPATH_WIDGETPAD, "show_{0}".format("toolshelf_alpha"), True))

        self.tlshlf_beta_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_BETA, "Toolshelf (Beta)", menu_path)
        self.tlshlf_beta_action.setCheckable(True)
        self.tlshlf_beta_action.setChecked(KritaSettings.readSettingBool(TOUCHIFY_SETTINGPATH_WIDGETPAD, "show_{0}".format("toolshelf_beta"), True))

        self.tlshlf_gamma_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_GAMMA, "Toolshelf (Gamma)", menu_path)
        self.tlshlf_gamma_action.setCheckable(True)
        self.tlshlf_gamma_action.setChecked(KritaSettings.readSettingBool(TOUCHIFY_SETTINGPATH_WIDGETPAD, "show_{0}".format("toolshelf_gamma"), True))

        self.tlshlf_delta_action = window.createAction(TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_DELTA, "Toolshelf (Delta)", menu_path)
        self.tlshlf_delta_action.setCheckable(True)
        self.tlshlf_delta_action.setChecked(KritaSettings.readSettingBool(TOUCHIFY_SETTINGPATH_WIDGETPAD, "show_{0}".format("toolshelf_delta"), True))
        
        self.tlb_action.triggered.connect(lambda a: self.Update_Actions("toolbox", a))
        self.tlshlf_alpha_action.triggered.connect(lambda a: self.Update_Actions("toolshelf_alpha", a))
        self.tlshlf_beta_action.triggered.connect(lambda a: self.Update_Actions("toolshelf_beta", a))
        self.tlshlf_gamma_action.triggered.connect(lambda a: self.Update_Actions("toolshelf_gamma", a))
        self.tlshlf_delta_action.triggered.connect(lambda a: self.Update_Actions("toolshelf_delta", a))

        options_menu.addAction(self.tlb_action)
        options_menu.addAction(self.tlshlf_alpha_action)
        options_menu.addAction(self.tlshlf_beta_action)
        options_menu.addAction(self.tlshlf_gamma_action)
        options_menu.addAction(self.tlshlf_delta_action)
    
    #endregion

    #region Post-Init Functions

    def Variables_Post(self, app_engine: "TouchifyWindow"):
        self.app_engine = app_engine
        self.__krita_window = self.app_engine.krita_window
        self.__mdi_area = self.QWindow().findChild(QMdiArea)
        self.__window_loaded = True

    def Components_Post(self):
        self.setParent(self.MdiArea())

    def Connections_Post(self):
        self.MdiArea().installEventFilter(self)
        KritaAPI.get_action("view_ruler").triggered.connect(self.Update_View)
        GlobalEvents.instance().SIGNAL_TOUCHIFY_CONFIG_UPDATED.connect(self.Preset_Reload)
        GlobalEvents.instance().SIGNAL_CANVAS_LAYOUT_CHANGED.connect(self.Preset_Reload)

    def Actions_Post(self):
        settings_menu = self.QWindow().findChild(QMenu, 'settings')

        layoutsMenuAction = KritaExtensions.moveActionTo(TOUCHIFY_ACTIONID_WIDGETPAD_MENU, settings_menu, settings_menu, 'toolbars_submenu_action')
        optionsMenuAction = KritaExtensions.moveActionTo(TOUCHIFY_ACTIONID_WIDGETPAD_PRESETS_MENU, settings_menu, settings_menu, 'toolbars_submenu_action')
        seperator = settings_menu.insertSeparator(optionsMenuAction)

    #endregion

    #region Window Functions

    def Window_Load(self, app_engine: "TouchifyWindow"):
        self.Variables_Post(app_engine)
        self.Components_Post()
        self.Connections_Post()
        self.Update_Widgets()

    #endregion

    #region Preset Functions

    def Preset_Change(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                TouchifySettings.instance().setActiveWidgetLayout(id)

    def Preset_Menu(self):
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
                action.triggered.connect(self.Preset_Change)
                index += 1
                
                menus[key.id].addAction(action)

    def Preset_Reload(self):
        last_preset_id = self.selected_preset_id
        self.active_preset: WidgetLayout = TouchifySettings.instance().getActiveWidgetLayout()
        self.selected_preset_id = TouchifySettings.instance().getActiveWidgetLayoutId()

        self.toolshelf_count = self.active_preset.toolshelf_count
        self.toolbox_enabled = self.active_preset.toolbox_enabled
        
        if last_preset_id != self.selected_preset_id:
            KritaSettings.writeSettingInt(TOUCHIFY_SETTINGPATH_WIDGETPAD, "SelectedPreset", self.selected_preset_id)
        
        if self.toolbox: 
            self.toolbox.toolbox.toolboxWidget.setHorizontalMode(self.active_preset.toolbox.horizontal_mode)

        self.Update_Widgets(True)

    #endregion

    #region Update Functions

    def Update_Core(self, mode: str, args: dict = {}):

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

    def Update_Widgets(self, full_unload: bool = False):
        if self.State_WindowLoaded() == False:
            return
        if full_unload: self.Update_Core("LOAD_ELEMENTS")
        else: self.Update_Core("RELOAD_ELEMENTS")

    def Update_View(self):
        self.Update_Core("VIEW")

    def Update_Actions(self, pad: str = "", value: bool = None):
        self.Update_Core("ACTIONS", {"pad": pad, "value": value})

    #endregion

    #region Component Relay

    def MdiArea(self):
        return self.__mdi_area

    def QWindow(self):
        return self.__krita_window.qwindow()

    def Window(self):
        return self.__krita_window

    #endregion

    #region State Functions

    def State_IsEmpty(self):
        if self.toolbox: return False
        elif self.toolshelf_alpha: return False
        elif self.toolshelf_beta: return False
        elif self.toolshelf_gamma: return False
        elif self.toolshelf_delta: return False
        else: return True

    def State_WindowLoaded(self):
        return self.__window_loaded

    #endregion

    #region Event Functions
    
    def eventFilter(self, obj: QObject, e: QEvent):
        if obj == self.MdiArea() and (e.type() == QEvent.Type.Move or \
                  e.type() == QEvent.Type.Resize or \
                  e.type() ==  QEvent.Type.WindowActivate): 
            self.Update_View()
        return False

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)

    def paintEvent(self, e: QPaintEvent):
        maskedRegion = QRegion(self.frameGeometry())
        maskedRegion -= QRegion(self.geometry())

        if self.toolbox: 
            maskedRegion += self.toolbox.geometry()

        if self.toolshelf_alpha: 
            maskedRegion += self.toolshelf_alpha.geometry()

        if self.toolshelf_beta: 
            maskedRegion += self.toolshelf_beta.geometry()

        if self.toolshelf_gamma: 
            maskedRegion += self.toolshelf_gamma.geometry()

        if self.toolshelf_delta: 
            maskedRegion += self.toolshelf_delta.geometry()

        self.setMask(maskedRegion)


    def widgetResizeEvent(self, target: NtWidgetPad):
        self.Update_View()


    #endregion
 

