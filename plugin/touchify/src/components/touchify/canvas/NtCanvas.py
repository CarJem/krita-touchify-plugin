from PyQt5.QtWidgets import QMdiArea




from .NtSubWinFilter import NtSubWinFilter

from ....docker_manager import DockerManager
from ....action_manager import ActionManager
from .NtToolbox import NtToolbox
from .NtToolshelf import NtToolshelf
from ....settings.TouchifySettings import TouchifySettings
from ....settings.TouchifyConfig import TouchifyConfig
from krita import *
from PyQt5.QtCore import QObject
from ....variables import *
from .NtWidgetPad import NtWidgetPad
from ....ext.KritaSettings import KritaSettings
from ....cfg.widget_pad.CfgWidgetPadPreset import CfgWidgetPadPreset
from ....cfg.widget_pad.CfgWidgetPadOptions import CfgWidgetPadOptions
from ....cfg.widget_pad.CfgWidgetPadToolboxOptions import CfgWidgetPadToolboxOptions
from ....cfg.CfgWidgetPadRegistry import CfgWidgetPadRegistry


class NtCanvas(QWidget):
    def __init__(self, parent: QObject, window: Window):
        super().__init__(parent)

        self.krita_window = window
        self.qWin = None
        self.mdiArea = None

        self.adjustFilter = None
        
        self.windowLoaded = False
        self.dockerManager = None

        self.toolbox = None
        self.toolboxOptions = None
        self.toolOptions = None

        self.presetsMenu = QMenu("Layouts...")
        self.presetsMenu.aboutToShow.connect(self.buildPresetMenu)

        self.canvasLayout = QGridLayout(self)
        self.canvasLayout.setContentsMargins(0,0,0,0)
        self.canvasLayout.setSpacing(0)
        self.setLayout(self.canvasLayout)

        self.reloadActivePreset()

    #region Setup Stuff
    def setManagers(self, manager: DockerManager, actionsManager: ActionManager):
        self.dockerManager = manager
        self.actions_manager = actionsManager

        Krita.instance().action("view_ruler").triggered.connect(self.onKritaConfigUpdate)

    def windowCreated(self, window: Window):
        self.krita_window = window
        self.qWin = self.krita_window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)

        self.adjustFilter = NtSubWinFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self)
        self.qWin.installEventFilter(self.adjustFilter)
        self.setParent(self.mdiArea)

        self.windowLoaded = True

        
        self.krita_window.qwindow().themeChanged.connect(self.updatePalette)

        self.updateElements()
        self.updateView()

    def createActions(self, window: Window, menu: QMenu, path: str):
        menu.addSection("Widget Options")
        menu.addMenu(self.presetsMenu)
        menu.addSection("Widget Visibility")

        self.tlb_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLBOX, "Show Toolbox", path)
        self.tlb_action.triggered.connect(lambda: self.togglePadVisibility("toolbox"))
        self.tlb_action.setCheckable(True)
        self.tlb_action.setChecked(True)
        menu.addAction(self.tlb_action)

        self.tlshlf_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLSHELF, "Show Toolshelf", path)
        self.tlshlf_action.triggered.connect(lambda: self.togglePadVisibility("toolshelf"))
        self.tlshlf_action.setCheckable(True)
        self.tlshlf_action.setChecked(True)
        menu.addAction(self.tlshlf_action)

        self.tlshlf_alt_action = window.createAction(TOUCHIFY_ID_ACTION_CANVAS_SHOWTOOLSHELF_ALT, "Show Toolshelf (Alt.)", path)
        self.tlshlf_alt_action.triggered.connect(lambda: self.togglePadVisibility("toolshelf_alt"))
        self.tlshlf_alt_action.setCheckable(True)
        self.tlshlf_alt_action.setChecked(True)
        menu.addAction(self.tlshlf_alt_action)
    #endregion

    #region Preset Functions

    def changePreset(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            index: int = ac.data()
            if isinstance(index, int):
                KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", index)
                self.reloadActivePreset()

    def buildPresetMenu(self):
        self.presetsMenu.clear()

        index = 0
        for preset in self.preset_registry.presets:
            preset: CfgWidgetPadPreset
            action = QAction(preset.preset_name, self.presetsMenu)
            action.setCheckable(True)
            if self.selectedPresetIndex == index:
                action.setChecked(True)
            action.setData(index)
            action.triggered.connect(self.changePreset)
            index += 1
            self.presetsMenu.addAction(action)

    def reloadActivePreset(self):
        self.preset_registry: CfgWidgetPadRegistry = TouchifyConfig.instance().getConfig().widget_pads
        self.active_preset: CfgWidgetPadPreset = CfgWidgetPadPreset()

        self.selectedPresetIndex = KritaSettings.readSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", 0)

        if 0 <= self.selectedPresetIndex < len(self.preset_registry.presets):
            self.active_preset: CfgWidgetPadPreset = self.preset_registry.presets[self.selectedPresetIndex]
        elif len(self.preset_registry.presets) >= 1:
            self.selectedPresetIndex = 0
            self.active_preset: CfgWidgetPadPreset = self.preset_registry.presets[self.selectedPresetIndex]
        else:
            self.selectedPresetIndex = 0
            newItem = CfgWidgetPadPreset()
            self.active_preset = newItem
        
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", self.selectedPresetIndex)
        
        if self.toolbox:
            self.toolbox.toolbox.toolboxWidget.setHorizontalMode(self.active_preset.toolbox.horizontal_mode)
        elif TouchifySettings.instance().CanvasWidgets_EnableToolbox:
            KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_TOOLBOX, "IsHorizontal", self.active_preset.toolbox.horizontal_mode)

        self.updateElements()
        self.updateView()

    #endregion

    #region Action Functions

    def togglePadVisibility(self, pad: str):
        if pad == "toolbox" and self.toolbox: self.toolbox.toggleWidgetVisible()
        elif pad == "toolshelf" and self.toolOptions: self.toolOptions.toggleWidgetVisible()
        elif pad == "toolshelf_alt" and self.toolboxOptions: self.toolboxOptions.toggleWidgetVisible()
        self.updateView()

    #endregion

    #region Event Functions

    def subWindowEvent(self):
        self.updateView()

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        self.updateView()

    def paintEvent(self, e: QPaintEvent):
        super().paintEvent(e)

    def onConfigUpdate(self):
        if self.toolboxOptions: self.toolboxOptions.toolshelf.onConfigUpdated()
        if self.toolOptions: self.toolOptions.toolshelf.onConfigUpdated()
    
    def onKritaConfigUpdate(self):        
        self.updateElements()
        self.updateView()

        if self.toolboxOptions: self.toolboxOptions.toolshelf.onKritaConfigUpdate()
        if self.toolOptions: self.toolOptions.toolshelf.onKritaConfigUpdate()
            
    #endregion

    #region Update Functions

    def updateElements(self):
        if self.windowLoaded == False:
            return
        
        usesNuToolbox = TouchifySettings.instance().CanvasWidgets_EnableToolbox
        usesNuToolOptionsAlt = TouchifySettings.instance().CanvasWidgets_EnableAltToolshelf
        usesNuToolOptions = TouchifySettings.instance().CanvasWidgets_EnableToolshelf

        if self.toolbox == None and usesNuToolbox:
            self.toolbox = NtToolbox(self, self.krita_window)
            self.installEventFilters(self.toolbox)
            self.canvasLayout.addWidget(self.toolbox)
            self.toolbox.show()
        elif self.toolbox and not usesNuToolbox:
            self.removeEventFilters(self.toolbox)
            self.canvasLayout.removeWidget(self.toolbox)
            self.toolbox.close()
            self.toolbox = None

        if self.toolboxOptions == None and usesNuToolOptionsAlt:
            self.toolboxOptions = NtToolshelf(self, self.krita_window, False, self.dockerManager, self.actions_manager)
            self.installEventFilters(self.toolboxOptions)
            self.canvasLayout.addWidget(self.toolboxOptions)
            self.toolboxOptions.show()
        elif self.toolboxOptions and not usesNuToolOptionsAlt:
            self.removeEventFilters(self.toolboxOptions)
            self.toolboxOptions.close()
            self.canvasLayout.removeWidget(self.toolboxOptions)
            self.toolboxOptions = None

        if self.toolOptions == None and usesNuToolOptions:
            self.toolOptions = NtToolshelf(self, self.krita_window, True, self.dockerManager, self.actions_manager)
            self.installEventFilters(self.toolOptions)
            self.canvasLayout.addWidget(self.toolboxOptions)
            self.toolOptions.show()
        elif self.toolOptions and not usesNuToolOptions:
            self.removeEventFilters(self.toolOptions)
            self.canvasLayout.removeWidget(self.toolOptions)
            self.toolOptions.close()
            self.toolOptions = None

        for x in range(self.canvasLayout.columnCount()):
            self.canvasLayout.setColumnStretch(x, 0)

        for y in range(self.canvasLayout.rowCount()):
            self.canvasLayout.setRowStretch(y, 0)


        def insertWidgetPad(pad: NtWidgetPad, padOptions: CfgWidgetPadOptions | CfgWidgetPadToolboxOptions):
            alignment_x = CfgWidgetPadOptions.HorizontalAlignment.toAlignmentFlag(padOptions.alignment_x)
            alignment_y = CfgWidgetPadOptions.VerticalAlignment.toAlignmentFlag(padOptions.alignment_y)
            pad.setLayoutAlignmentX(alignment_x)
            pad.setLayoutAlignmentY(alignment_y)
            if padOptions.span_x != -1 and padOptions.span_y != -1:
                self.canvasLayout.addWidget(pad, padOptions.position_y, padOptions.position_x, padOptions.span_y, padOptions.span_x, alignment_x | alignment_y)
            else:
                self.canvasLayout.addWidget(pad, padOptions.position_y, padOptions.position_x, alignment_x | alignment_y)
            self.canvasLayout.setColumnStretch(padOptions.position_x, padOptions.stretch_x)
            self.canvasLayout.setRowStretch(padOptions.position_y, padOptions.stretch_y)
            

        if self.toolbox: 
            insertWidgetPad(self.toolbox, self.active_preset.toolbox)
        if self.toolOptions: 
            insertWidgetPad(self.toolOptions, self.active_preset.toolshelf)
        if self.toolboxOptions: 
            insertWidgetPad(self.toolboxOptions, self.active_preset.toolshelf_alt)

    def updateView(self):
        if self.windowLoaded == False:
            return

        def rulerMargin():
            padding = 4
            # Canvas ruler pixel width on Windows
            if KritaSettings.showRulers(): return 20 + padding
            return 0

        def scrollBarMargin():
            padding = 4
            # Canvas scrollbar pixel width/height on Windows 
            if KritaSettings.hideScrollbars(): return 0
            return 10 + padding

        if self.mdiArea:
            position = self.mdiArea.viewport().pos()
            size = self.mdiArea.viewport().size()

            position.setX(position.x() + rulerMargin())
            position.setY(position.y() + rulerMargin())

            size.setWidth(size.width() - rulerMargin() - scrollBarMargin())
            size.setHeight(size.height() - rulerMargin() - scrollBarMargin())

            self.move(position)
            self.setFixedSize(size)

            maskedRegion = QRegion(self.frameGeometry())
            maskedRegion -= QRegion(self.geometry())
            maskedRegion += self.childrenRegion()
            self.setMask(maskedRegion)
    
            if self.toolbox: self.toolbox.adjustToView()
            if self.toolboxOptions: self.toolboxOptions.adjustToView()
            if self.toolOptions: self.toolOptions.adjustToView()

    def updatePalette(self):
        if self.windowLoaded == False:
            return
        
        if self.toolboxOptions: self.toolboxOptions.toolshelf.onConfigUpdated()
        if self.toolOptions: self.toolOptions.toolshelf.onConfigUpdated()

    def updateActions(self):
        if self.toolbox: self.tlb_action.setChecked(self.toolbox.isWidgetVisible())
        if self.toolboxOptions: self.tlshlf_alt_action.setChecked(self.toolboxOptions.isWidgetVisible())
        if self.toolOptions: self.tlshlf_action.setChecked(self.toolOptions.isWidgetVisible())
        

    #endregion

    #region Connect/Disconnect Functions

    def installEventFilters(self, widget: NtWidgetPad):
        widget.btnHide.clicked.connect(self.updateView)
        widget.btnHide.clicked.connect(self.updateActions)

    def removeEventFilters(self, widget: NtWidgetPad):
        widget.btnHide.clicked.disconnect(self.updateView)
        widget.btnHide.clicked.disconnect(self.updateActions)

    #endregion


