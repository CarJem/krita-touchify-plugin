from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *


from touchify.src.components.toolshelf_old.Header import Header

from touchify.src.components.toolshelf_old.TabList import TabList
from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *

from touchify.src.config.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions
from touchify.src.components.toolshelf_old.PageStack import PageStack

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfCanvasWidget import ToolshelfCanvasWidget
    from .ToolshelfDockWidget import ToolshelfDockWidget, ToolshelfDockWidgetAlt
    from ..special.TouchifyPopup import TouchifyPopup
    from touchify.src.PluginManagers import TouchifyManagers
    from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad

class ToolshelfWidget(QWidget):
    toolshelfResized=pyqtSignal()
    toolshelfChanged=pyqtSignal()
    dataLoaded=pyqtSignal()

    toolshelfPageChanged=pyqtSignal()
    
    resizeByDefaultRequested=pyqtSignal()

    class PreviousState:
        def __init__(self):
            self._last_toolshelf_id: str | None = None
            self._last_pinned: bool = False
            self._last_resizable: bool = False
            self._last_panel_id: str | None = None

    def __init__(self, parent, managers: "TouchifyManagers", cfg: ToolshelfData, registry_index: int = -3):
        super(ToolshelfWidget, self).__init__(parent)
        self.display: "ToolshelfCanvasWidget" | "ToolshelfDockWidget" | "ToolshelfDockWidgetAlt" | "TouchifyPopup" = parent
        self.managers = managers

        self.INTERNAL_SHOW_EVENT_INIT = True

        self.pinned = False
        self.resizable = cfg.header_options.default_to_resize_mode
        self.registry_index = registry_index
        self.cfg = cfg
        self.toolshelf_id = cfg.preset_name

        self.activateWidget()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
        headerOrientation = Qt.Orientation.Horizontal
        headerBeforePages = True

        match self.cfg.header_options.position:
            case ToolshelfDataOptions.Position.Top:
                headerOrientation = Qt.Orientation.Horizontal
                headerBeforePages = True
            case ToolshelfDataOptions.Position.Bottom:
                headerOrientation = Qt.Orientation.Horizontal
                headerBeforePages = False
            case ToolshelfDataOptions.Position.Left:
                headerOrientation = Qt.Orientation.Vertical
                headerBeforePages = True
            case ToolshelfDataOptions.Position.Right:
                headerOrientation = Qt.Orientation.Vertical
                headerBeforePages = False

        self.header = Header(self, self.cfg, self.registry_index, headerOrientation)
        self.tabs = TabList(self.header, headerOrientation)
        self.pages = PageStack(self, self.cfg)

        self.pages.dataLoaded.connect(self.onPagesLoaded)
        self.pages.contentsChanged.connect(self.onContentsChanged)
        self.pages.contentsResized.connect(self.onContentsResized)

        self.mainLayout = QVBoxLayout(self) if headerOrientation == Qt.Orientation.Horizontal else QHBoxLayout(self)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.header)
        self.mainLayout.addWidget(self.tabs)
        self.mainLayout.addWidget(self.pages)

        self.header.optionsMenu.editModeAction.changed.connect(self.onEditModeChanged)
        self.header.optionsMenu.SIGNAL_RESIZE_STATE_CHANGED.connect(self.onResizableChanged)


        if headerOrientation == Qt.Orientation.Horizontal:
            self.mainLayout.setDirection(QVBoxLayout.Direction.TopToBottom if headerBeforePages else QBoxLayout.Direction.BottomToTop)
        else:
            self.mainLayout.setDirection(QHBoxLayout.Direction.LeftToRight if headerBeforePages else QHBoxLayout.Direction.RightToLeft)

        if not self.cfg.header_options.show_titlebar:
            self.header.setVisible(False)

        if not self.cfg.header_options.show_tabs:
            self.tabs.setVisible(False)

        if self.cfg.header_options.default_to_pinned:
            self.setPinned(True)



    #region Events

    def firstShowEvent(self):
        if self.cfg.header_options.default_to_resize_mode:
            self.resizeByDefaultRequested.emit()

    def resizeEvent(self, event: QResizeEvent):
        self.toolshelfResized.emit()
        super().resizeEvent(event)

    def showEvent(self, event: QShowEvent):
        if self.INTERNAL_SHOW_EVENT_INIT:
            self.firstShowEvent()
            self.INTERNAL_SHOW_EVENT_INIT = False

        self.activateWidget()
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        self.deactivateWidget()
        super().hideEvent(event)

    #endregion
    
    #region Getters / Setters

    def setPinned(self, value: bool | None = None):
        if value == None:
            self.pinned = not self.pinned
        else:
            self.pinned = value
        self.header.pinButton.setChecked(self.pinned)

    #endregion

    #region Actions

    def goHome(self):
        if self.pages:
            self.pages.goHome()

    def togglePinned(self):
        self.pinned = not self.pinned
        self.header.pinButton.setChecked(self.pinned)

    def restorePreviousState(self, previous_state: PreviousState):
        if previous_state._last_toolshelf_id == self.toolshelf_id:            
            self.header.optionsMenu.toggleResizeAct.setChecked(previous_state._last_resizable)
            self.setPinned(previous_state._last_pinned)

            if self.pages.panel(previous_state._last_panel_id) != None:
                self.pages.changePanel(previous_state._last_panel_id)

    def backupPreviousState(self):
        state = ToolshelfWidget.PreviousState()
        state._last_toolshelf_id = self.toolshelf_id
        state._last_pinned = self.pinned
        state._last_resizable = self.resizable
        state._last_panel_id = self.pages._current_panel_id
        return state
    
    def deactivateWidget(self):
        if self.is_active == True:
            self.managers.mgr_canvas.delayedFocus.disconnect(self.onCanvasFocused)
            self.pages.deactivateWidget()
            self.is_active = False

    def activateWidget(self):
        if not hasattr(self, "is_active"):
            self.managers.mgr_canvas.delayedFocus.connect(self.onCanvasFocused)
            self.is_active = True
        else:
            if self.is_active == False:
                self.managers.mgr_canvas.delayedFocus.connect(self.onCanvasFocused)
                self.pages.activateWidget()
                self.is_active = True
    
    def shutdownWidget(self):
        self.deactivateWidget()
        self.pages.shutdownWidget()
        self.header.close()

    #endregion

    #region Signals

    def onPagesLoaded(self):
        self.dataLoaded.emit()

    def onResizableChanged(self, state: bool):
        self.resizable = state

    def onEditModeChanged(self):
        edit_mode = self.header.optionsMenu.editModeAction.isChecked()
        self.pages.setEditMode(edit_mode)
    
    def onPageChanged(self, current_panel_id: str):
        if hasattr(self, 'header'):
            self.header.onPageChanged(current_panel_id)
            self.tabs.onPageChanged(current_panel_id)
        self.toolshelfPageChanged.emit()

    def onContentsChanged(self):
        self.toolshelfChanged.emit()

    def onContentsResized(self):
        self.toolshelfResized.emit()

    def onCanvasFocused(self):
        if self.pinned == False: self.goHome()

    #endregion

    #region Overrides

    def sizeHint(self):
        resultingsize = super().sizeHint()
        return resultingsize.grownBy(QMargins(1,1,1,1))

    #endregion