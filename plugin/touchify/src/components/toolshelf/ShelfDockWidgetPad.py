
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from touchify.__env__ import *
from touchify.src.components.toolshelf.ShelfDockWidget import ShelfDockWidget
from touchify.src.managers.shared.resources import ResourceManager
from touchify.src.managers.shared.settings_krita import KritaSettings
if TYPE_CHECKING:
    from ...PluginWindow import TouchifyWindow
    from touchify.src.PluginManagers import TouchifyManagers

class ShelfWidgetPad(ShelfDockWidget):
    DOCKER_TITLE=f"{Env.Title.CORE_DOCKERS_PREFIX} Widget Pad"
    CLONE_DOCKER_TITLE=f"{Env.Title.CLONE_DOCKERS_PREFIX} Widget Pad"

    class TitlebarWidget(QWidget):

        sigButtonToggled = pyqtSignal(bool)
        sigContextMenuRequested = pyqtSignal(QPoint)

        def __init__(self, parent = None):
            super().__init__(parent)
            self._mode = "left"

            self.setContentsMargins(0,0,0,0)


            self._rightArrow = ResourceManager.iconLoader("material:menu-right")
            self._leftArrow = ResourceManager.iconLoader("material:menu-left")
            self._upArrow = ResourceManager.iconLoader("material:menu-up")
            self._downArrow = ResourceManager.iconLoader("material:menu-down")

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

    class WidgetAlignment(Enum):
        TopLeft = 1
        TopCenter = 2
        TopRight = 3
        MidLeft = 4
        MidRight = 5
        BottomLeft = 6
        BottomCenter = 7
        BottomRight = 8

    class Settings(QObject):

        def __init__(self, parent: "ShelfWidgetPad"):
            super().__init__(parent)
            self._parent = parent

        def getSettingsPath(self):
            return f"{Env.SettingsPath.WIDGETPAD}_{str(self._parent.PanelIndex)}"

        def getShowHeader(self):
            return KritaSettings.readSettingBool(self.getSettingsPath(), "ShowHeader", True)

        def setShowHeader(self, value: bool):
            KritaSettings.writeSettingBool(self.getSettingsPath(), "ShowHeader", value, False)

        def getCollapsed(self):
            return KritaSettings.readSettingBool(self.getSettingsPath(), "Collapsed", False)

        def setCollapsed(self, value: bool):
            KritaSettings.writeSettingBool(self.getSettingsPath(), "Collapsed", value, False)

        def getAlignment(self):
            try:
                input = KritaSettings.readSettingInt(self.getSettingsPath(), "Alignment", 0)
                return ShelfWidgetPad.WidgetAlignment(input)
            except:
                return ShelfWidgetPad.WidgetAlignment.TopLeft

        def setAlignment(self, value: int):
            KritaSettings.writeSettingInt(self.getSettingsPath(), "Alignment", value, False)

    def __init__(self, index: int = 0):
        super().__init__(-1)
        
        self.setWindowTitle(f"{ShelfWidgetPad.CLONE_DOCKER_TITLE} (Ext. {index})")
        self.PanelIndex = 10 + index

        self._alignment = self.WidgetAlignment.TopLeft
        self._edgePosition = QPoint(0,0)
        self._collapsed_size = QSize()
        self._collapsed_position = QPoint()
        self._max_width = 1
        self._max_height = 1
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

        alignmentMenu = menu.addMenu("Align to...")


        currentAlignment = self._settings.getAlignment().value
        alignmentMenuGroup = QActionGroup(menu)
        alignmentMenuGroup.setExclusive(True)
        for entry in ShelfWidgetPad.WidgetAlignment:
            action = alignmentMenuGroup.addAction(entry.name)
            action.setCheckable(True)
            if entry.value == currentAlignment:
                action.setChecked(True)
            action.triggered.connect(partial(self.onAlignmentUpdated, entry.value))
            alignmentMenu.addAction(action)

        menu.exec_(pos)

    def onAlignmentUpdated(self, value: int):
        alignment = ShelfWidgetPad.WidgetAlignment.TopLeft
        try:
            alignment = ShelfWidgetPad.WidgetAlignment(value)
        except:
            pass
        self.setAlignment(alignment)
        self._settings.setAlignment(alignment.value)

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
            
    def timerEvent(self, a0):
        self.syncPosition()
        super().timerEvent(a0)

    def setAlignment(self, align: WidgetAlignment):
        self._alignment = align
        match align:
            case self.WidgetAlignment.TopLeft:
                self._titlebar.updateButtons("left")
            case self.WidgetAlignment.MidLeft:
                self._titlebar.updateButtons("left")
            case self.WidgetAlignment.BottomLeft:
                self._titlebar.updateButtons("left")
            case self.WidgetAlignment.TopRight:
                self._titlebar.updateButtons("right")
            case self.WidgetAlignment.MidRight:
                self._titlebar.updateButtons("right")
            case self.WidgetAlignment.BottomRight:
                self._titlebar.updateButtons("right")
            case self.WidgetAlignment.TopCenter:
                self._titlebar.updateButtons("up")
            case self.WidgetAlignment.BottomCenter:
                self._titlebar.updateButtons("down")
            case _:
                pass

    def syncPosition(self):
        if not self.isVisible():
            return
        
        if self.isFloating() == False:
            self.setFloating(True)

        if not self.managers:
            return
        
        active_canvas = self.managers.mgr_canvas.active_canvas

        if not active_canvas:
            return

        edge_padding: int = 5
        space_rect = active_canvas.rect()
        docker_width = self.width()
        docker_height = self.height()

        if docker_width != 0 and docker_height != 0:
            docker_halfwidth = int(docker_width / 2)
            docker_halfheight = int(docker_height / 2)
        else:
            docker_halfwidth = 0
            docker_halfheight = 0

        top_left = QPoint(space_rect.topLeft()) + QPoint(edge_padding, edge_padding)
        top_center = QPoint(space_rect.center().x(),space_rect.top()) - QPoint(docker_halfwidth, 0) + QPoint(0, edge_padding)
        top_right = QPoint(space_rect.topRight()) - QPoint(docker_width, 0) + QPoint(-edge_padding, edge_padding)

        mid_left = QPoint(space_rect.left(), space_rect.center().y()) - QPoint(0, docker_halfheight) + QPoint(edge_padding, 0)
        mid_right = QPoint(space_rect.right(), space_rect.center().y()) - QPoint(docker_width, docker_halfheight) + QPoint(-edge_padding, 0)

        bottom_left = QPoint(space_rect.bottomLeft()) - QPoint(0, docker_height) + QPoint(edge_padding, -edge_padding)
        bottom_center = QPoint(space_rect.center().x(), space_rect.bottom()) - QPoint(docker_halfwidth, docker_height) + QPoint(0, -edge_padding)
        bottom_right = QPoint(space_rect.bottomRight()) - QPoint(docker_width, docker_height) + QPoint(-edge_padding, -edge_padding)
        

        _position: QPoint = QPoint(0,0)
        match self._alignment:
            case self.WidgetAlignment.TopLeft:
                _position = active_canvas.mapToGlobal(top_left)
            case self.WidgetAlignment.TopRight:
                _position = active_canvas.mapToGlobal(top_right)
            case self.WidgetAlignment.BottomRight:
                _position = active_canvas.mapToGlobal(bottom_right)
            case self.WidgetAlignment.BottomLeft:
                _position = active_canvas.mapToGlobal(bottom_left)
            case self.WidgetAlignment.TopCenter:
                _position = active_canvas.mapToGlobal(top_center)
            case self.WidgetAlignment.BottomCenter:
                _position = active_canvas.mapToGlobal(bottom_center)
            case self.WidgetAlignment.MidLeft:
                _position = active_canvas.mapToGlobal(mid_left)
            case self.WidgetAlignment.MidRight:
                _position = active_canvas.mapToGlobal(mid_right)
            case _:
                _position = active_canvas.mapToGlobal(QPoint(0,0))
        
        _max_height = space_rect.height() - edge_padding *2
        _max_width = space_rect.width() - edge_padding * 2


        _c_width = self.width()
        _c_height = self.height()
        _c_pos = self.pos()

        if self.isSizeManaged:
            self.shrinkToFit()

        if _c_width > _max_width:
            self.resize(_max_width, _c_height)

        if _c_height > _max_height:
            self.resize(_c_width, _max_height)

        if _c_pos != _position:
            self.move(_position)