
from functools import partial
from typing import TYPE_CHECKING
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from touchify.__env__ import *
from touchify.src.components.toolshelf.ToolshelfDockerWidget import ToolshelfDockerWidget
from touchify.src.managers.WidgetPadManager import WidgetPadAlignment
from jemlib.managers.IconRepository import IconRepository
from touchify.src.settings.KritaSettings import KritaSettings
if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers




class ToolshelfDockerWidgetPad(ToolshelfDockerWidget):
    DOCKER_TITLE=f"{Env.Title.CORE_DOCKERS_PREFIX} Widget Pad"
    CLONE_DOCKER_TITLE=f"{Env.Title.CLONE_DOCKERS_PREFIX} Widget Pad"

    class TitlebarWidget(QWidget):

        sigButtonToggled = pyqtSignal(bool)
        sigContextMenuRequested = pyqtSignal(QPoint)

        def __init__(self, parent = None):
            super().__init__(parent)
            self._mode = "left"

            self.setContentsMargins(0,0,0,0)


            self._rightArrow = IconRepository.iconLoader("material:menu-right")
            self._leftArrow = IconRepository.iconLoader("material:menu-left")
            self._upArrow = IconRepository.iconLoader("material:menu-up")
            self._downArrow = IconRepository.iconLoader("material:menu-down")

            self.setLayout(QVBoxLayout())
            self.layout().setContentsMargins(0,0,0,0)
            self.layout().setSpacing(0)

            self.toggleButton = QPushButton(self)
            self.toggleButton.setMaximumHeight(18)
            self.toggleButton.setCheckable(True)
            self.toggleButton.toggled.connect(self.onButtonToggled)
            self.layout().addWidget(self.toggleButton)

            self.syncIcons(True)

        def contextMenuEvent(self, a0: QContextMenuEvent):
            self.sigContextMenuRequested.emit(a0.globalPos())
            a0.ignore()

        def onButtonToggled(self, state: bool):
            self.sigButtonToggled.emit(state)
            self.syncIcons(state)

        def syncIcons(self, state: bool):
            is_left = self._mode == "left"
            is_right = self._mode == "right"
            is_up = self._mode == "up"
            is_down = self._mode == "down"


            icon = self._rightArrow

            if state:
                if is_right: icon = self._leftArrow
                elif is_left: icon = self._rightArrow
                elif is_up: icon = self._downArrow
                elif is_down: icon = self._upArrow
            else:
                if is_right: icon = self._rightArrow
                elif is_left: icon = self._leftArrow
                elif is_up: icon = self._upArrow
                elif is_down: icon = self._downArrow

            self.toggleButton.setIconSize(QSize(24, 24))
            self.toggleButton.setIcon(icon)
                
            

        def updateButtons(self, mode: str = "left"):
            self._mode = mode
            self.syncIcons(self.toggleButton.isChecked())

    class Settings(QObject):

        def __init__(self, parent: "ToolshelfDockerWidgetPad"):
            super().__init__(parent)
            self._parent = parent

        def getSettingsPath(self):
            result = f"{Env.SettingsPath.WIDGETPAD}_{str(self._parent.PanelIndex)}"
            return result

        def getShowHeader(self):
            return KritaSettings.readSettingBool(self.getSettingsPath(), "ShowHeader", True)

        def setShowHeader(self, value: bool):
            KritaSettings.writeSettingBool(self.getSettingsPath(), "ShowHeader", value, False)

        def getCollapsed(self):
            return KritaSettings.readSettingBool(self.getSettingsPath(), "Collapsed", False)

        def setCollapsed(self, value: bool):
            KritaSettings.writeSettingBool(self.getSettingsPath(), "Collapsed", value, False)

        def getPriority(self):
            result = KritaSettings.readSettingInt(self.getSettingsPath(), "Priority", 0)
            if result < 0: return 0
            else: return result

        def setPriority(self, value: int):
            KritaSettings.writeSettingInt(self.getSettingsPath(), "Priority", value, False)

        def getAlignment(self):
            try:
                input = KritaSettings.readSettingInt(self.getSettingsPath(), "Alignment", 1)
                if input == 0: return WidgetPadAlignment.TopLeft
                return WidgetPadAlignment(input)
            except Exception as ex:
                return WidgetPadAlignment.TopLeft

        def setAlignment(self, value: WidgetPadAlignment):
            KritaSettings.writeSettingInt(self.getSettingsPath(), "Alignment", value.value, False)

    sigOnMoved = pyqtSignal(QDockWidget, QMoveEvent)
    sigOnResized = pyqtSignal(QDockWidget, QResizeEvent)

    def __init__(self, index: int = 0):
        super().__init__(-1)
        
        self.setWindowTitle(f"{ToolshelfDockerWidgetPad.CLONE_DOCKER_TITLE} (Ext. {index})")
        self.PanelIndex = 10 + index

        self._alignment = WidgetPadAlignment.AlignNone
        self._collapsed_size = QSize()
        self._collapsed_position = QPoint()
        self._priority = 0
        self._previousNeighbor: "ToolshelfDockerWidgetPad" = None
        self._nextNeighbor: "ToolshelfDockerWidgetPad" = None
        self._allowSignals = True

        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

        self._settings = self.Settings(self)

        self._titlebar = self.TitlebarWidget(self)
        self._titlebar.sigButtonToggled.connect(self.onToggled)
        self._titlebar.sigContextMenuRequested.connect(self.onContextMenu)
        self.setTitleBarWidget(self._titlebar)

    def setup(self, app_window: "TouchifyWindow"):
        super().setup(app_window)
        self.setAlignment(self._settings.getAlignment())
        self.mainWidget.setTitlebarVisibility(self._settings.getShowHeader())
        self.setPriority(self._settings.getPriority())

        is_collapsed = self._settings.getCollapsed()
        if is_collapsed:
            self._titlebar.toggleButton.blockSignals(True)
            self._titlebar.toggleButton.setChecked(True)
            self._titlebar.syncIcons(True)
            self._titlebar.toggleButton.blockSignals(False)
            self._collapsed_size = self.size()
            self.mainWidget.hide()

    def onContextMenu(self, pos: QPoint):
        menu = QMenu(self)
        
        shelfOptionsAct = menu.addAction("Toolshelf Options...")
        shelfOptionsAct.triggered.connect(partial(self.onShelfSettings, pos))
        menu.addSeparator()
        
        showHeaderAct = menu.addAction("Show Header")
        showHeaderAct.setCheckable(True)
        showHeaderAct.setChecked(self._settings.getShowHeader())
        showHeaderAct.toggled.connect(self.onHeaderToggled)

        menu.addSeparator()
        increasePriorityAct = menu.addAction("Increase Priority...")
        increasePriorityAct.setEnabled(self._nextNeighbor != None)
        increasePriorityAct.triggered.connect(self.onIncreasePriority)

        decrasePriorityAct = menu.addAction("Decrease Priority...")
        decrasePriorityAct.setEnabled(self._previousNeighbor != None)
        decrasePriorityAct.triggered.connect(self.onDecreasePriority)
        menu.addSeparator()
        

        alignmentMenu = menu.addMenu("Align to...")
        currentAlignment = self._settings.getAlignment().value
        alignmentMenuGroup = QActionGroup(menu)
        alignmentMenuGroup.setExclusive(True)
        for entry in WidgetPadAlignment:
            if entry.value == 0:
                continue

            action = alignmentMenuGroup.addAction(entry.name)
            action.setCheckable(True)
            if entry.value == currentAlignment:
                action.setChecked(True)
            action.triggered.connect(partial(self.onAlignmentUpdated, entry))
            alignmentMenu.addAction(action)

        menu.exec_(pos)

    def onIncreasePriority(self):
        result = self._priority + 2
        self.setPriority(result)
        self._settings.setPriority(self._priority)
    
    def onDecreasePriority(self):
        result = self._priority - 2
        self.setPriority(result)
        self._settings.setPriority(self._priority)

    def onAlignmentUpdated(self, value: int):
        self.setAlignment(WidgetPadAlignment(value))
        self._settings.setAlignment(value)

    def onHeaderToggled(self, state: bool):
        self.mainWidget.setTitlebarVisibility(state)
        self._settings.setShowHeader(state)

    def onShelfSettings(self, pos: QPoint):
        self.mainWidget.header.optionsMenu.exec_(pos)

    def onToggled(self, state: bool):
        self._settings.setCollapsed(state)
        if state == True:
            self._collapsed_size = self.size()
            self.mainWidget.hide()
        else:
            self.mainWidget.show()
            self.resize(self._collapsed_size)

    def setAllowSignals(self, state: bool):
        self._allowSignals = state

    def setPriority(self, level: int):
        self._priority = level
        self.managers.mgr_widgetpad.nudgeWidgetPad(self)

    def setAlignment(self, align: WidgetPadAlignment):
        old_alignment = self._alignment
        self._alignment = align

        match align:
            case WidgetPadAlignment.TopLeft:
                self._titlebar.updateButtons("left")
            case WidgetPadAlignment.MidLeft:
                self._titlebar.updateButtons("left")
            case WidgetPadAlignment.BottomLeft:
                self._titlebar.updateButtons("left")
            case WidgetPadAlignment.TopRight:
                self._titlebar.updateButtons("right")
            case WidgetPadAlignment.MidRight:
                self._titlebar.updateButtons("right")
            case WidgetPadAlignment.BottomRight:
                self._titlebar.updateButtons("right")
            case WidgetPadAlignment.TopCenter:
                self._titlebar.updateButtons("up")
            case WidgetPadAlignment.BottomCenter:
                self._titlebar.updateButtons("down")
            case _:
                pass

        self.managers.mgr_widgetpad.moveWidgetPad(self, old_alignment, align)

    def resizeEvent(self, a0: QResizeEvent):
        if self._allowSignals: self.sigOnResized.emit(self, a0)
        return super().resizeEvent(a0)
    
    def moveEvent(self, a0: QMoveEvent):
        if self._allowSignals: self.sigOnMoved.emit(self, a0)
        return super().moveEvent(a0)


def DynamicToolshelfDockerWidgetPad(value: int):
    class DynamicToolshelfDockerWidgetPad(ToolshelfDockerWidgetPad):
        def __init__(self):
            super().__init__(value)

    return DynamicToolshelfDockerWidgetPad