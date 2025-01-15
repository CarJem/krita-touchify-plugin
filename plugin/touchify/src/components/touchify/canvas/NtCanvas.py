from PyQt5.QtWidgets import QMdiArea





from touchify.src.components.touchify.canvas.NtSubWinFilter import NtSubWinFilter
from touchify.src.components.touchify.canvas.NtToolbox import NtToolbox
from touchify.src.components.touchify.canvas.NtToolshelf import NtToolshelf
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from touchify.src.helpers import TouchifyHelpers
from touchify.src.settings import TouchifySettings
from krita import *
from PyQt5.QtCore import QObject
from touchify.src.variables import *
from touchify.src.components.krita.settings import KritaSettings
from touchify.src.cfg.widget_layout.WidgetLayout import WidgetLayout
from touchify.src.cfg.widget_layout.WidgetLayoutPadOptions import WidgetLayoutPadOptions
from touchify.src.cfg.widget_layout.WidgetLayoutToolboxOptions import WidgetLayoutToolboxOptions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


class NtCanvas(QObject):
    def __init__(self, parent: QObject, window: Window):
        super().__init__(parent)

        self.krita_window = window
        self.qWin = None
        self.mdiArea = None

        self.windowEventFilter = None
        
        self.windowLoaded = False
        self.app_engine = None

        self._size = QSize()
        self._pos = QPoint()
        self._coords: dict[int, dict[int, NtWidgetPad]] = {}

        self.toolbox: NtToolbox = None
        self.toolshelf_beta: NtToolshelf = None
        self.toolshelf_alpha: NtToolshelf = None
        self.toolshelf_gamma: NtToolshelf = None
        self.toolshelf_delta: NtToolshelf = None

        self.adjust_widget_timer = QTimer(self)
        self.adjust_widget_timer.setInterval(1000)
        self.adjust_widget_timer.timeout.connect(self.adjustWidgets)
        self.adjust_widget_timer.start()

        self.toolshelf_count = 0
        self.toolbox_enabled = False

        self.presetsMenu = QMenu("Canvas Layouts...")
        self.presetsMenu.aboutToShow.connect(self.buildPresetMenu)

        self.installEventFilter(self)
        self.reloadActivePreset()

    #region Layout
    def clearCanvasCoords(self):
        self._coords.clear()

    def setCanvasCoords(self, widget: NtWidgetPad, x: int, y: int):
        if not x in self._coords: self._coords[x] = {}
        self._coords[x][y] = widget
        widget.setCanvasCoords(x, y)

    def localSize(self, x: int, y: int):
        return self.localGeometry(x,y).size()

    def localPos(self, x: int, y: int):
        return self.localGeometry(x,y).topLeft()
    
    def canvasBorderWidth(self):
        ruler_padding = 15 if KritaSettings.showRulers() else 0
        return ruler_padding
    
    def canvasBorderHeight(self):
        ruler_padding = 15 if KritaSettings.showRulers() else 0
        tab_padding = 32
        return ruler_padding + tab_padding

    def localGeometry(self, x: int, y: int):
        if not x in self._coords: return self.geometry()
        if not y in self._coords[x]: return self.geometry()
        widget = self._coords[x][y]
        if not widget: return self.geometry()

        x_sibling: NtWidgetPad = None
        if x + 1 in self._coords: 
            if y in self._coords[x+1]: x_sibling = self._coords[x+1][y]
            else: x_sibling = None
        else: x_sibling = None

        y_sibling: NtWidgetPad = None
        if y + 1 in self._coords[x]: y_sibling = self._coords[x][y+1]
        else: y_sibling = None
        
        canvas_size = self.size()
        bounds = canvas_size
        
        #if x_sibling: 
            #x_sibling.geometry().left()

        #if y_sibling: 
            #y_sibling.geometry().top()
            

        if y == 0: yrange = [0]
        else: yrange = range(0, y)

        local_x = self.pos().x()
        local_y = self.pos().y()
        local_width = self.size().width()
        local_height = self.size().height()

        for tx in range(0, x):
            if not tx in self._coords: continue
            lwv = 0

            for ty in yrange:
                if not ty in self._coords[tx]: continue
                wi = self._coords[tx][ty].width()
                if wi > lwv: lwv = wi
            
            local_x = local_x + lwv

        if local_x + widget.width() > bounds.width():
            local_x = bounds.width() - widget.width()

            
        for ty in range(0, y):
            if not ty in self._coords[x]: continue
            
            hi = self._coords[x][ty]
            local_y = local_y + hi.height()
            
        if local_y + widget.height() + widget.btnHide.height() > bounds.height():
            local_y = bounds.height() - widget.height() - widget.btnHide.height()

        if local_x < self.canvasBorderWidth(): local_x = self.canvasBorderWidth()
        if local_y < self.canvasBorderHeight(): local_y = self.canvasBorderHeight()

        return QRect(local_x, local_y, local_width, local_height)
        
        

    def geometry(self):
        return QRect(self._pos.x(), self._pos.y(), self._size.width(), self._size.height())

    def size(self):
        return self._size
    
    def pos(self):
        return self._pos
    
    def setFixedSize(self, size: QSize):
        self._size = size

    def move(self, pos: QPoint):
        self._pos = pos


    #endregion

    #region States



    def isEmpty(self):
        return False

    #endregion

    #region Setup Stuff
    def windowCreated(self, app_engine: "TouchifyWindow"):
        self.app_engine = app_engine

        Krita.instance().action("view_ruler").triggered.connect(self.updateView)


        self.krita_window = self.app_engine.windowSource
        self.qWin = self.krita_window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        self.setParent(self.mdiArea)

        self.windowEventFilter = NtSubWinFilter(self)
        self.windowEventFilter.SIGNAL_ACTIVATE_FORCE.connect(self.updateView)
        self.windowEventFilter.SIGNAL_ACTIVATE_QUEUE.connect(self.updateView)
        self.qWin.installEventFilter(self.windowEventFilter)

        self.windowLoaded = True

        self.krita_window.qwindow().themeChanged.connect(self.updatePalette)
        self.updateElements()
        self.updateActions()
        

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
                self.reloadActivePreset()

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
        self.active_preset: WidgetLayout = TouchifySettings.instance().getActiveWidgetLayout()
        self.selected_preset_id = TouchifySettings.instance().getActiveWidgetLayoutId()

        self.toolshelf_count = self.active_preset.toolshelf_count
        self.toolbox_enabled = self.active_preset.toolbox_enabled
        
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", self.selected_preset_id)
        
        if self.toolbox: self.toolbox.toolbox.toolboxWidget.setHorizontalMode(self.active_preset.toolbox.horizontal_mode)

        self.updateElements(True)
        self.updateActions()

    #endregion

    #region Event Functions
    

    def eventFilter(self, a0, a1):
        return super().eventFilter(a0, a1)

    def onConfigUpdate(self):
        self.reloadActivePreset()
        if self.toolbox: self.toolbox.updateStyle()

        if self.toolshelf_delta:
            self.toolshelf_delta.toolshelf.onConfigUpdated()
            self.toolshelf_delta.updateStyle()
        if self.toolshelf_gamma: 
            self.toolshelf_gamma.toolshelf.onConfigUpdated()
            self.toolshelf_gamma.updateStyle()
        if self.toolshelf_beta: 
            self.toolshelf_beta.toolshelf.onConfigUpdated()
            self.toolshelf_beta.updateStyle()
        if self.toolshelf_alpha: 
            self.toolshelf_alpha.toolshelf.onConfigUpdated()
            self.toolshelf_alpha.updateStyle()
            
    #endregion

    #region Update Functions

    def updateElements(self, full_unload: bool = False):

        def createEmptySpace(x: int, y: int):
            pass
  
        def deactivateToolshelf(allow_toolshelf: bool, config_index: int):
            match config_index:
                case 0: toolshelf = self.toolshelf_alpha
                case 1: toolshelf = self.toolshelf_beta
                case 2: toolshelf = self.toolshelf_gamma
                case 3: toolshelf = self.toolshelf_delta
                case _: return

            if toolshelf and not allow_toolshelf:
                toolshelf.close()
                match config_index:
                    case 0: self.toolshelf_alpha = None
                    case 1: self.toolshelf_beta = None
                    case 2: self.toolshelf_gamma = None
                    case 3: self.toolshelf_delta = None
                    case _: return
      
        def activateToolshelf(x: int, y: int, allow_toolshelf: bool, config_index: int, action: QAction, data: dict, options: WidgetLayoutPadOptions):
            match config_index:
                case 0: toolshelf = self.toolshelf_alpha
                case 1: toolshelf = self.toolshelf_beta
                case 2: toolshelf = self.toolshelf_gamma
                case 3: toolshelf = self.toolshelf_delta
                case _: return        
                
            if toolshelf == None and allow_toolshelf:
                actual_toolshelf = NtToolshelf(self, self.krita_window, config_index, self.app_engine)
                self.setCanvasCoords(actual_toolshelf, x, y)
                actual_toolshelf.btnHide.setDefaultAction(action)
                actual_toolshelf.setLayoutAlignmentX(WidgetLayoutPadOptions.HorizontalAlignment.toAlignmentFlag(options.alignment_x))
                actual_toolshelf.setLayoutAlignmentY(WidgetLayoutPadOptions.VerticalAlignment.toAlignmentFlag(options.alignment_y))
                actual_toolshelf.show()
                match config_index:
                    case 0: self.toolshelf_alpha = actual_toolshelf
                    case 1: self.toolshelf_beta = actual_toolshelf
                    case 2: self.toolshelf_gamma = actual_toolshelf
                    case 3: self.toolshelf_delta = actual_toolshelf
                    case _: return
        
        def deactivateToolbox(allow_toolbox: bool):
            if self.toolbox and not allow_toolbox:
                self.toolbox.close()
                self.toolbox = None
        
        def activateToolbox(x: int, y: int, allow_toolbox: bool, data: dict, options: WidgetLayoutToolboxOptions):
            if self.toolbox == None and allow_toolbox:
                self.toolbox = NtToolbox(self, self.krita_window)
                self.setCanvasCoords(self.toolbox, x, y)
                self.toolbox.btnHide.setDefaultAction(self.tlb_action)
                self.toolbox.setLayoutAlignmentX(WidgetLayoutPadOptions.HorizontalAlignment.toAlignmentFlag(options.alignment_x))
                self.toolbox.setLayoutAlignmentY(WidgetLayoutPadOptions.VerticalAlignment.toAlignmentFlag(options.alignment_y))
                self.toolbox.show()

        def ItemData(padOptions: WidgetLayoutPadOptions | WidgetLayoutToolboxOptions, widgetType: str) -> dict:
                return {
                    "x": padOptions.position_x,
                    "y": padOptions.position_y,
                    "widgetType": widgetType,
                    "align_x": padOptions.alignment_x,
                    "align_y": padOptions.alignment_y
                }

        if self.windowLoaded == False:
            return

        allow_toolbox = self.toolbox_enabled
        allow_toolshelf_alpha = self.toolshelf_count >= 1
        allow_toolshelf_beta = self.toolshelf_count >= 2
        allow_toolshelf_gamma = self.toolshelf_count >= 3
        allow_toolshelf_delta = self.toolshelf_count >= 4

        self.clearCanvasCoords()

        deactivateToolbox(False)
        deactivateToolshelf(False, 0)
        deactivateToolshelf(False, 1)
        deactivateToolshelf(False, 2)
        deactivateToolshelf(False, 3)
        
        preset_data = []
        if allow_toolbox: preset_data.append(ItemData(self.active_preset.toolbox, "toolbox"))
        if allow_toolshelf_alpha: preset_data.append(ItemData(self.active_preset.toolshelf_alpha, "toolshelf_1"))
        if allow_toolshelf_beta: preset_data.append(ItemData(self.active_preset.toolshelf_beta, "toolshelf_2"))
        if allow_toolshelf_gamma: preset_data.append(ItemData(self.active_preset.toolshelf_gamma, "toolshelf_3"))
        if allow_toolshelf_delta: preset_data.append(ItemData(self.active_preset.toolshelf_delta, "toolshelf_4"))

        if len(preset_data) == 0: return

        grid_width = max(preset_data, key=lambda x:x['x'])['x'] + 1
        grid_height = max(preset_data, key=lambda x:x['y'])['y'] + 1
        grid_itemMap: dict[int, dict[int, dict]] = {}

        for preset in preset_data:
            x: int = preset['x']
            y: int = preset['y']

            if x not in grid_itemMap: grid_itemMap[x] = {}
            if y not in grid_itemMap[x]: grid_itemMap[x][y] = {}

            grid_itemMap[x][y] = preset

        for x in range(0, grid_width):
            for y in range(0, grid_height):
                if x not in grid_itemMap: grid_itemMap[x] = {}
                if y not in grid_itemMap[x]:
                    if len(grid_itemMap[x]) != 0:
                        grid_itemMap[x][y] = {'widgetType': "reserved"}
                    else:
                        grid_itemMap[x][y] = {'widgetType': "empty"}

        for x in range(0, grid_width):
            for y in range(0, grid_height):
                print(f"{x,y} -- {grid_itemMap[x][y]}")
                
        for x in range(0, grid_width):
            for y in range(0, grid_height):
                data = grid_itemMap[x][y]

                if data['widgetType'] == "toolbox":
                    activateToolbox(x, y, allow_toolbox, data, self.active_preset.toolbox)
                elif data['widgetType'] == "toolshelf_1":
                    activateToolshelf(x, y, allow_toolshelf_alpha, 0, self.tlshlf_alpha_action, data, self.active_preset.toolshelf_alpha)
                elif data['widgetType'] == "toolshelf_2":
                    activateToolshelf(x, y, allow_toolshelf_beta, 1, self.tlshlf_beta_action, data, self.active_preset.toolshelf_beta)
                elif data['widgetType'] == "toolshelf_3":
                    activateToolshelf(x, y, allow_toolshelf_gamma, 2, self.tlshlf_gamma_action, data, self.active_preset.toolshelf_gamma)
                elif data['widgetType'] == "toolshelf_4":
                    activateToolshelf(x, y, allow_toolshelf_delta, 3, self.tlshlf_delta_action, data, self.active_preset.toolshelf_delta)
                elif data['widgetType'] == "empty" or data['widgetType'] == "reserved":
                    createEmptySpace(x, y)

    def updateView(self):
        if self.windowLoaded == False:
            return

        if not self.mdiArea: return

        subWindow = self.mdiArea.activeSubWindow()
        if not subWindow: return

        kis_view = subWindow.widget()
        if not kis_view: return

        canvas_controller = next((w for w in kis_view.findChildren(QAbstractScrollArea) if w.metaObject().className() == 'KisCanvasController'), None)
        if not canvas_controller: return

        viewport = next((w for w in canvas_controller.findChildren(QWidget) if w.metaObject().className() == 'Viewport'), None)
        if not viewport: return

        position = viewport.mapTo(self.mdiArea, QPoint(0,0))
        size = viewport.size()

        position.setX(position.x())
        position.setY(position.y())

        size.setWidth(size.width())
        size.setHeight(size.height())

        if self.isEmpty():
            self.move(position)
            self.setFixedSize(0, 0)
        else:
            self.move(position)
            self.setFixedSize(size)

        self.adjustWidgets()


    def adjustWidgets(self):
        if self.toolbox: self.toolbox.adjustToView()
        if self.toolshelf_alpha: self.toolshelf_alpha.adjustToView()
        if self.toolshelf_beta: self.toolshelf_beta.adjustToView()
        if self.toolshelf_gamma: self.toolshelf_gamma.adjustToView()
        if self.toolshelf_delta: self.toolshelf_delta.adjustToView()
    
    def mouseMoveEvent(self, a0):
        pos = self.cursor().pos()
        if self.toolbox: self.toolbox.updateCursor(pos)
        if self.toolshelf_alpha: self.toolshelf_alpha.updateCursor(pos)
        if self.toolshelf_beta: self.toolshelf_beta.updateCursor(pos)
        if self.toolshelf_gamma: self.toolshelf_gamma.updateCursor(pos)
        if self.toolshelf_delta: self.toolshelf_delta.updateCursor(pos)

    def updatePalette(self):
        if self.windowLoaded == False:
            return
        
        if self.toolbox: 
            self.toolbox.updateStyle()
        if self.toolshelf_delta:
            self.toolshelf_delta.updateStyle()
        if self.toolshelf_gamma: 
            self.toolshelf_gamma.updateStyle()
        if self.toolshelf_beta: 
            self.toolshelf_beta.updateStyle()
        if self.toolshelf_alpha: 
            self.toolshelf_alpha.updateStyle()

    def updateActions(self, pad: str = "", value: bool = None):
        if self.windowLoaded == False:
            return
        

        show_toolbox = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolbox"), True)
        show_toolshelf_alpha = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_alpha"), True)
        show_toolshelf_beta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_beta"), True)
        show_toolshelf_gamma = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_gamma"), True)
        show_toolshelf_delta = KritaSettings.readSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format("toolshelf_delta"), True)
        
        if pad != "" and value != None:
            KritaSettings.writeSettingBool(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "show_{0}".format(pad), value, False)
            match pad:
                case "toolbox": show_toolbox = value
                case "toolshelf_alpha": show_toolshelf_alpha = value
                case "toolshelf_beta":  show_toolshelf_beta = value
                case "toolshelf_gamma": show_toolshelf_gamma = value
                case "toolshelf_delta": show_toolshelf_delta = value
                case _: pass


        self.tlb_action.setChecked(show_toolbox)
        self.tlshlf_alpha_action.setChecked(show_toolshelf_alpha)
        self.tlshlf_beta_action.setChecked(show_toolshelf_beta)
        self.tlshlf_gamma_action.setChecked(show_toolshelf_gamma)
        self.tlshlf_delta_action.setChecked(show_toolshelf_delta)
    
        if self.toolbox: self.toolbox.setCollapsed(show_toolbox)
        if self.toolshelf_alpha: self.toolshelf_alpha.setCollapsed(show_toolshelf_alpha)
        if self.toolshelf_beta:  self.toolshelf_beta.setCollapsed(show_toolshelf_beta)
        if self.toolshelf_gamma: self.toolshelf_gamma.setCollapsed(show_toolshelf_gamma)
        if self.toolshelf_delta: self.toolshelf_delta.setCollapsed(show_toolshelf_delta)

        self.updateView()
        

    #endregion


