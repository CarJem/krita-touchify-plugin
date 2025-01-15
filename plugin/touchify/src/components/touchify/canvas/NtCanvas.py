from PyQt5.QtWidgets import QMdiArea





from touchify.src.components.touchify.canvas.NtSubWinFilter import NtSubWinFilter
from touchify.src.components.touchify.canvas.NtToolbox import NtToolbox
from touchify.src.components.touchify.canvas.NtToolshelf import NtToolshelf
from touchify.src.helpers import TouchifyHelpers
from touchify.src.settings import TouchifySettings
from krita import *
from PyQt5.QtCore import QObject
from touchify.src.variables import *
from touchify.src.components.touchify.canvas.NtWidgetPad import NtWidgetPad
from touchify.src.components.krita.settings import KritaSettings
from touchify.src.cfg.widget_layout.WidgetLayout import WidgetLayout
from touchify.src.cfg.widget_layout.WidgetLayoutPadOptions import WidgetLayoutPadOptions
from touchify.src.cfg.widget_layout.WidgetLayoutToolboxOptions import WidgetLayoutToolboxOptions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


class NtCanvas(QWidget):
    def __init__(self, parent: QObject, window: Window):
        super().__init__(parent)

        self.krita_window = window
        self.qWin = None
        self.mdiArea = None

        self.windowEventFilter = None
        
        self.windowLoaded = False
        self.app_engine = None

        self.toolbox: NtToolbox = None
        self.toolshelf_beta: NtToolshelf = None
        self.toolshelf_alpha: NtToolshelf = None
        self.toolshelf_gamma: NtToolshelf = None
        self.toolshelf_delta: NtToolshelf = None

        self.view_update_timer = QTimer(self)
        self.view_update_timer.setSingleShot(True)
        self.view_update_timer.timeout.connect(self.updateView)

        self.toolshelf_count = 0
        self.toolbox_enabled = False

        self.presetsMenu = QMenu("Canvas Layouts...")
        self.presetsMenu.aboutToShow.connect(self.buildPresetMenu)

        self.installEventFilter(self)

        self.resetCanvasLayout()

        self.reloadActivePreset()

    def resetCanvasLayout(self):
        self.canvasLayout = QGridLayout(self)
        self.canvasLayout.setContentsMargins(0,0,0,0)
        self.canvasLayout.setSpacing(0)
        self.setLayout(self.canvasLayout)

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

        Krita.instance().action("view_ruler").triggered.connect(self.requestViewUpdate)


        self.krita_window = self.app_engine.windowSource
        self.qWin = self.krita_window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)
        self.setParent(self.mdiArea)

        self.windowEventFilter = NtSubWinFilter(self)
        self.windowEventFilter.SIGNAL_ACTIVATE_FORCE.connect(self.updateView)
        self.windowEventFilter.SIGNAL_ACTIVATE_QUEUE.connect(self.requestViewUpdate)
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
        self.updateMask()
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
        def onToolshelfCheck(toolshelf: NtToolshelf | None, allow_toolshelf: bool, config_index: int, action: QAction):
            if toolshelf == None and allow_toolshelf:
                actual_toolshelf = NtToolshelf(self, self.krita_window, config_index, self.app_engine)
                actual_toolshelf.btnHide.setDefaultAction(action)
                self.canvasLayout.addWidget(actual_toolshelf)
                actual_toolshelf.show()
                return actual_toolshelf
            elif toolshelf and not allow_toolshelf:
                toolshelf.close()
                self.canvasLayout.removeWidget(toolshelf)
                return None
            else:
                return "ignore"
        
        def onToolboxCheck(allow_toolbox: bool):
            if self.toolbox == None and allow_toolbox:
                self.toolbox = NtToolbox(self, self.krita_window)
                self.toolbox.btnHide.setDefaultAction(self.tlb_action)
                self.canvasLayout.addWidget(self.toolbox)
                self.toolbox.show()
            elif self.toolbox and not allow_toolbox:
                self.canvasLayout.removeWidget(self.toolbox)
                self.toolbox.close()
                self.toolbox = None

        def insertWidgetPad(pad: NtWidgetPad, padOptions: WidgetLayoutPadOptions | WidgetLayoutToolboxOptions):
            alignment_x = WidgetLayoutPadOptions.HorizontalAlignment.toAlignmentFlag(padOptions.alignment_x)
            alignment_y = WidgetLayoutPadOptions.VerticalAlignment.toAlignmentFlag(padOptions.alignment_y)
            pos_y = padOptions.position_y
            pos_x = padOptions.position_x
            span_x = padOptions.span_x
            span_y = padOptions.span_y
            pad.setLayoutAlignmentX(alignment_x)
            pad.setLayoutAlignmentY(alignment_y)
            pad.setTargetCoords(pos_y, pos_x)

            if span_x != -1 and span_y != -1:
                self.canvasLayout.addWidget(pad, pos_y, pos_x, padOptions.span_y, padOptions.span_x, alignment_x | alignment_y)
            else:
                self.canvasLayout.addWidget(pad, pos_y, pos_x, alignment_x | alignment_y)
            self.canvasLayout.setColumnStretch(pos_x, padOptions.stretch_x)
            self.canvasLayout.setRowStretch(pos_y, padOptions.stretch_y)

        if self.windowLoaded == False:
            return
        

        if full_unload:
            onToolboxCheck(False)

            alpha = onToolshelfCheck(self.toolshelf_alpha, False, 0, self.tlshlf_alpha_action)
            if alpha != "ignore": self.toolshelf_alpha = alpha

            beta = onToolshelfCheck(self.toolshelf_beta,  False, 1, self.tlshlf_beta_action)
            if beta != "ignore": self.toolshelf_beta = beta

            gamma = onToolshelfCheck(self.toolshelf_gamma, False, 2, self.tlshlf_gamma_action)
            if gamma != "ignore": self.toolshelf_gamma = gamma

            delta = onToolshelfCheck(self.toolshelf_delta, False, 3, self.tlshlf_delta_action)
            if delta != "ignore": self.toolshelf_delta = delta

            #TODO: Implement Toggle Button Positions, NtWidgetPad Resize Constrations 
            # to Prevent Overlap, and Better Overlay Bounds Calculations
            if self.canvasLayout.count() != 0:
                self.resetCanvasLayout()
        
        
        
        allow_toolbox = self.toolbox_enabled
        allow_toolshelf_alpha = self.toolshelf_count >= 1
        allow_toolshelf_beta = self.toolshelf_count >= 2
        allow_toolshelf_gamma = self.toolshelf_count >= 3
        allow_toolshelf_delta = self.toolshelf_count >= 4

        onToolboxCheck(allow_toolbox)

        alpha = onToolshelfCheck(self.toolshelf_alpha, allow_toolshelf_alpha, 0, self.tlshlf_alpha_action)
        if alpha != "ignore": self.toolshelf_alpha = alpha

        beta = onToolshelfCheck(self.toolshelf_beta,  allow_toolshelf_beta, 1, self.tlshlf_beta_action)
        if beta != "ignore": self.toolshelf_beta = beta

        gamma = onToolshelfCheck(self.toolshelf_gamma, allow_toolshelf_gamma, 2, self.tlshlf_gamma_action)
        if gamma != "ignore": self.toolshelf_gamma = gamma

        delta = onToolshelfCheck(self.toolshelf_delta, allow_toolshelf_delta, 3, self.tlshlf_delta_action)
        if delta != "ignore": self.toolshelf_delta = delta



        if self.toolbox: insertWidgetPad(self.toolbox, self.active_preset.toolbox)
        if self.toolshelf_alpha: insertWidgetPad(self.toolshelf_alpha, self.active_preset.toolshelf_alpha)
        if self.toolshelf_beta: insertWidgetPad(self.toolshelf_beta, self.active_preset.toolshelf_beta)
        if self.toolshelf_gamma: insertWidgetPad(self.toolshelf_gamma, self.active_preset.toolshelf_gamma)
        if self.toolshelf_delta: insertWidgetPad(self.toolshelf_delta, self.active_preset.toolshelf_delta)

    def requestViewUpdate(self):
        if self.view_update_timer.isActive():
            self.view_update_timer.stop()
        self.view_update_timer.start(250)

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

        if self.toolbox: self.toolbox.adjustToView()
        if self.toolshelf_alpha: self.toolshelf_alpha.adjustToView()
        if self.toolshelf_beta: self.toolshelf_beta.adjustToView()
        if self.toolshelf_gamma: self.toolshelf_gamma.adjustToView()
        if self.toolshelf_delta: self.toolshelf_delta.adjustToView()
    

    def updateMask(self):
        if not self.isEmpty():
            maskedRegion = QRegion(self.frameGeometry())
            maskedRegion -= QRegion(self.geometry())
            maskedRegion += self.childrenRegion()
            self.setMask(maskedRegion)

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

        self.requestViewUpdate()
        

    #endregion


