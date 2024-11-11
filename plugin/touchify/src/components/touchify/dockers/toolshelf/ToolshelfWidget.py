from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from .ToolshelfHeader import ToolshelfHeader

from .....settings.TouchifyConfig import *
from .....variables import *
from .....docker_manager import *

from .....cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from .ToolshelfPageStack import ToolshelfPageStack
from .extras.MouseListener import MouseListener

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfDockWidget import ToolshelfDockWidget
    from .ToolshelfDocker import ToolshelfDocker
    from ...popups.PopupDialog_Toolshelf import PopupDialog_Toolshelf

class ToolshelfWidget(QWidget):
    def __init__(self, parent: "ToolshelfDockWidget", cfg: CfgToolshelf, registry_index: int = -1):
        super(ToolshelfWidget, self).__init__(parent)

        self.mouse_listener = MouseListener()
        self.pinned = False
        self.parent_docker: "ToolshelfDockWidget" | "ToolshelfDocker" | "PopupDialog_Toolshelf"  = parent
        self.registry_index = registry_index
        self.cfg = cfg

        self.mouse_listener.mouseReleased.connect(self.onMouseRelease)
        QApplication.instance().installEventFilter(self.mouse_listener)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        
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


        if headerOrientation == Qt.Orientation.Horizontal:
            self.mainLayout.setDirection(QVBoxLayout.Direction.TopToBottom if headerBeforePages else QBoxLayout.Direction.BottomToTop)
        else:
            self.mainLayout.setDirection(QHBoxLayout.Direction.LeftToRight if headerBeforePages else QHBoxLayout.Direction.RightToLeft)


    
    #region Getters / Setters

    def setPinned(self, value):
        self.pinned = not self.pinned
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
    
    def shutdownWidget(self):
        QApplication.instance().removeEventFilter(self.mouse_listener)
        self.mouse_listener.mouseReleased.disconnect(self.onMouseRelease)
        self.pages.shutdownWidget()
        self.header.close()

    #endregion

    #region Signals
    
    def onPageChanged(self, current_panel_id: str):
        if hasattr(self, 'header'):
            self.header.onPageChanged(current_panel_id)

    def onSizeChanged(self):
        self.parent_docker.onSizeChanged()

    def onMouseRelease(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
        
        if not isinstance(widget_under_cursor, QOpenGLWidget): return
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return
        
        if self.pinned == False:
            self.goHome()

    #endregion