from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfEditMode import ToolshelfEditMode
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfHeader import ToolshelfHeader

from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *

from touchify.src.cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfPageStack import ToolshelfPageStack
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfCanvasListener import ToolshelfCanvasListener

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfDockWidget import ToolshelfDockWidget
    from .ToolshelfDockWidgetKrita import ToolshelfDockWidgetKrita
    from ...popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf

class ToolshelfWidget(QWidget):
    sizeChanged=pyqtSignal()

    def __init__(self, parent: "ToolshelfDockWidget", cfg: CfgToolshelf, registry_index: int = -1):
        super(ToolshelfWidget, self).__init__(parent)

        self.mouse_listener = ToolshelfCanvasListener()
        self.pinned = False
        self.parent_docker: "ToolshelfDockWidget" | "ToolshelfDockWidgetKrita" | "PopupDialog_Toolshelf"  = parent
        self.registry_index = registry_index
        self.cfg = cfg

        self.activateWidget()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.edit_mode_connector = ToolshelfEditMode(self)
     
        headerOrientation = Qt.Orientation.Horizontal
        headerBeforePages = True

        match self.cfg.header_options.position:
            case CfgToolshelfHeaderOptions.Position.Top:
                headerOrientation = Qt.Orientation.Horizontal
                headerBeforePages = True
            case CfgToolshelfHeaderOptions.Position.Bottom:
                headerOrientation = Qt.Orientation.Horizontal
                headerBeforePages = False
            case CfgToolshelfHeaderOptions.Position.Left:
                headerOrientation = Qt.Orientation.Vertical
                headerBeforePages = True
            case CfgToolshelfHeaderOptions.Position.Right:
                headerOrientation = Qt.Orientation.Vertical
                headerBeforePages = False

        self.header = ToolshelfHeader(self, self.cfg, self.registry_index, headerOrientation)
        self.pages = ToolshelfPageStack(self, self.cfg)

        self.mainLayout = QVBoxLayout(self) if headerOrientation == Qt.Orientation.Horizontal else QHBoxLayout(self)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.header)
        self.mainLayout.addWidget(self.pages)

        self.header.optionsMenu.editMode.changed.connect(self.editModeChanged)


        if headerOrientation == Qt.Orientation.Horizontal:
            self.mainLayout.setDirection(QVBoxLayout.Direction.TopToBottom if headerBeforePages else QBoxLayout.Direction.BottomToTop)
        else:
            self.mainLayout.setDirection(QHBoxLayout.Direction.LeftToRight if headerBeforePages else QHBoxLayout.Direction.RightToLeft)

        if self.cfg.header_options.default_to_pinned:
            self.setPinned(True)


    def resizeEvent(self, event: QResizeEvent):
        self.sizeChanged.emit()
        super().resizeEvent(event)

    def showEvent(self, event: QShowEvent):
        self.activateWidget()
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        self.deactivateWidget()
        super().hideEvent(event)
    
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

    def restorePreviousState(self, _last_pinned: bool, _last_panel_id: str):
        if _last_pinned:
            self.setPinned(_last_pinned)

        if self.pages.panel(_last_panel_id) != None:
            self.pages.changePanel(_last_panel_id)

    def backupPreviousState(self):
        return (self.pinned, self.pages._current_panel_id)
    
    def deactivateWidget(self):
        if self.is_active == True:
            QApplication.instance().removeEventFilter(self.mouse_listener)
            self.mouse_listener.mouseReleased.disconnect(self.onMouseRelease)
            self.pages.deactivateWidget()
            self.is_active = False

    def activateWidget(self):
        if not hasattr(self, "is_active"):
            self.mouse_listener.mouseReleased.connect(self.onMouseRelease)
            QApplication.instance().installEventFilter(self.mouse_listener)
            self.is_active = True
        else:
            if self.is_active == False:
                QApplication.instance().installEventFilter(self.mouse_listener)
                self.mouse_listener.mouseReleased.connect(self.onMouseRelease)
                self.pages.activateWidget()
                self.is_active = True
    
    def shutdownWidget(self):
        self.deactivateWidget()
        self.pages.shutdownWidget()
        self.header.close()

    #endregion

    #region Signals

    def editModeChanged(self):
        self.edit_mode = self.header.optionsMenu.editMode.isChecked()
        self.edit_mode_connector.setEnabled(self.edit_mode)
    
    def onPageChanged(self, current_panel_id: str):
        self.requestViewUpdate()
        if hasattr(self, 'header'):
            self.header.onPageChanged(current_panel_id)

    def requestViewUpdate(self):
        QTimer.singleShot(150, self.parent_docker.requestViewUpdate)

    def onMouseRelease(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
        
        if not isinstance(widget_under_cursor, QOpenGLWidget): return
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return
        
        if self.pinned == False:
            self.goHome()

    #endregion

    #region Overrides

    def sizeHint(self):
        resultingsize = super().sizeHint()
        return resultingsize.grownBy(QMargins(1,1,1,1))

    #endregion