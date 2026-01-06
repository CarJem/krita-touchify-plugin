from functools import partial
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from jemlib.api_touchify.env import *
from jemlib.api_krita.wrappers.window import WindowAPI
from touchify.src.components.popup.PopupGeometryInfo import PopupGeometryInfo
from touchify.src.components.popup.PopupLoader import PopupLoader
from touchify.src.components.popup.PopupTitlebar import PopupTitlebar
from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget
from touchify.src.config.popup.PopupData import PopupData
from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
from touchify.src.config.toolshelf.ToolshelfAreaSettings import ToolshelfAreaSettings
import jemlib.alib_vaporjem.extensions.pyqt_extensions as PyQtExtensions
from jemlib.alib_widgets.widget.AnimatedWidget import AnimatedWidget


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers
    from touchify.src.managers.ActionManager import ActionManager
    from touchify.src.managers.DockerManager import DockerManager
    from touchify.src.managers.CanvasManager import CanvasManager


class PopupWidget(QDockWidget, AnimatedWidget):


    def __init__(self, parent: QWidget, id: str, args: PopupData, managers: "TouchifyManagers"):     
        QDockWidget.__init__(self, parent)  
        #TODO: Improve Performance
        AnimatedWidget.__init__(self, parent, 0) #0.1 

        self.popupConfiguration: PopupData = args
        self.registry_id: str = id
        self.managers: "TouchifyManagers" = managers
        self.api_window: WindowAPI = self.managers.api_window()
        self.main_window: QMainWindow = self.api_window.qwindow

        self._canDrawFrame = True
        self._isDockingAllowed = False
        self._isFixedLayout = False
        self._isResizePermitted = False
        self._isResizable = False
        self._isWindow = False
        self._isPopup = True
        self._isClampMode = False
        self._popupPosX: str = PopupData.PopupPosition.Default
        self._popupPosY: str = PopupData.PopupPosition.Default
        self._closeOnMouseLeave = False
        self._closeOnDeactivation = False

        self._timeSinceOpened = QTime()
        self._parentContainer: QWidget | None = None
        self._parentPopupWidget: PopupWidget | None = None
        self._isChildPopupFocused: bool = False
        self._hasBeenOpenedBefore = False
        self._isCollapsed = False
        self._currentCollapsedSize = None
        self._currentCollapsedMinSize = None
        self._hasComposerWorkAround = False
        self._originalSizePolicy = self.sizePolicy()
        self._toggleViewAction = self.toggleViewAction()
        self._shrinkToFit = False

        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        
        self.container = QWidget(self)
        self.container.setContentsMargins(1,1,1,1) # essential to draw the frame properly
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidget(self.container)

        self.containerLayout = QVBoxLayout(self)
        self.containerLayout.setContentsMargins(0,0,0,0)
        self.containerLayout.setSpacing(0)
        self.container.setLayout(self.containerLayout)

        self.containerLoader = PopupLoader(self)
        self.containerWidget = ShelfWidget(self, self.managers, 0, ToolshelfArea())
        self.containerLayout.addWidget(self.containerWidget)
        
        self.dockLocationChanged.connect(self.onDockLocationChanged)

        self.reload(args)

    def reload(self, args: PopupData):
        self.popupConfiguration = args

        if args.window_type == PopupData.WindowType.Window:
            self._canDrawFrame = False
            self._canRememberLayout = args.window_remember_layout
            self._isDockingAllowed = args.window_docking_allowed
            self._isFixedLayout = args.window_fixed_layout
            self._isResizePermitted = True
            self._isResizable = True
            self._isWindow = True
            self._isPopup = False
        else:
            self._canDrawFrame = True
            self._canRememberLayout = False
            self._isDockingAllowed = False
            self._isFixedLayout = False
            self._isResizePermitted = False
            self._isResizable = False
            self._isWindow = False
            self._isPopup = True

        self._popupPosX = args.popup_position_x
        self._popupPosY = args.popup_position_y

        self._isClampMode = args.clamp_to_main_window
        
        match args.closing_method:
            case PopupData.ClosingMethod.MouseLeave:
                self._closeOnMouseLeave = True
                self._closeOnDeactivation = False
            case PopupData.ClosingMethod.Deactivation:
                self._closeOnMouseLeave = False
                self._closeOnDeactivation = True
            case _:
                self._closeOnMouseLeave = False
                self._closeOnDeactivation = False

        self.containerLayout.removeWidget(self.containerWidget)
        self.containerWidget.deleteLater()
        self.containerWidget = None
        self.containerWidget = ShelfWidget(self, self.managers, 0, self.containerLoader.Init_Section(args))
        self.containerWidget.sigShelfIndexChanged.connect(self.onShelfIndexChanged)
        self.containerLayout.addWidget(self.containerWidget)

        if self._isDockingAllowed:
            self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        else:
            self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

        if self._isWindow:
            self.popupTitleBarWidget = PopupTitlebar(self)
            self.popupTitleBarWidget.setTitleBarText(args.window_title)
            self.setTitleBarWidget(self.popupTitleBarWidget)
        else:
            self.popupTitleBarWidget = None
            self.setTitleBarWidget(QWidget(self))

    #region Accessor Functions

    def dockLocation(self) -> Qt.DockWidgetArea:
        return self.main_window.dockWidgetArea(self)

    #endregion

    #region Get / Set Functions

    def getParentPopup(self, source: QWidget) -> "PopupWidget":
        from touchify.src.components.popup.PopupWidget import PopupWidget
        try:
            widget = source.parentWidget()
            while (widget):
                foo = widget
                if isinstance(foo, PopupWidget):
                    return foo
                widget = widget.parentWidget()
            return None
        except:
            return None    
        
    def getParentBounds(self, container: QWidget = None):
        if container == None:
            parent_pos = QPoint(0,0)
            parent_width = 0
            parent_height = 0
        else:
            parent_pos = container.mapToGlobal(QPoint(0,0))
            parent_width = container.width()
            parent_height = container.height()

        return PopupGeometryInfo(parent_pos, QSize(parent_width, parent_height))
        
    def getWindowBounds(self, container: QWidget = None):
        window_size = self.getWindowSizeHint()
        bounds_info = self.getParentBounds(container)

        if not container:
            mouse_point = QCursor().pos()
            window_x = mouse_point.x()
            window_y = mouse_point.y()
        else:
            window_x = bounds_info.position.x() + (bounds_info.size.width() // 2) - (window_size.width() // 2)
            window_y = bounds_info.position.y() + (bounds_info.size.height())

        match self._popupPosX:
            case PopupData.PopupPosition.Start:
                window_x -= 0 
            case PopupData.PopupPosition.Center:
                window_x -= (window_size.width() // 2) 
            case PopupData.PopupPosition.End:
                window_x -= window_size.width()
            case _:
                window_x -= 0 

        match self._popupPosY:
            case PopupData.PopupPosition.Start:
                window_y -= 0 
            case PopupData.PopupPosition.Center:
                window_y -= (window_size.height() // 2) 
            case PopupData.PopupPosition.End:
                window_y -= window_size.height()
            case _:
                window_y -= 0 

        return PopupGeometryInfo(QPoint(window_x, window_y), window_size)

    def getWindowSizeHint(self) -> QSize:
        if self._isPopup and self.containerWidget:
            dialog_width = self.sizeHint().width()
            dialog_height = self.sizeHint().height()
        else:
            dialog_width = self.minimumSizeHint().width()
            dialog_height = self.minimumSizeHint().height()

        return QSize(int(dialog_width), int(dialog_height))

    #endregion

    #region Geometry Methods

    def initPopupGeometry(self, parent: QWidget = None):
        self._parentContainer = parent

        window_bounds = self.getWindowBounds(parent)
        hint_x, hint_y = window_bounds.position.x(), window_bounds.position.y()
        hint_width, hint_height = window_bounds.size.width(), window_bounds.size.height()

        info = PopupGeometryInfo(QPoint(hint_x, hint_y), QSize(hint_width, hint_height))
        if self._isClampMode:
            info.position = PyQtExtensions.GeometryHelpers.clampToTarget(info.position, info.size, self.main_window)
        self.setGeometry(info.position.x(), info.position.y(), info.size.width(), info.size.height())
        self.updatePopupGeometry(info)

    def resetPopupGeometry(self):
        self._parentContainer = None

    def updatePopupGeometry(self, info: PopupGeometryInfo):
        if self._isPopup:
            self.resize(info.size)
            self.move(info.position)
        elif self._isWindow:
            if not self._isCollapsed:
                self.setMinimumSize(info.size)
                if not self._isResizable:
                    self.resize(info.size)
        

    #endregion

    #region Action Methods

    def toggleShade(self):
        if self._isWindow:
            if self.popupTitleBarWidget:
                if self._isCollapsed:
                    self.setMinimumSize(self._currentCollapsedMinSize)
                    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                    self.resize(self._currentCollapsedSize)
                    self.popupTitleBarWidget.updateCollapseState(True)
                    self.container.setVisible(True)
                    self._currentCollapsedSize = None
                    self._currentCollapsedMinSize = None
                    self._isCollapsed = False
                    if self._isDockingAllowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
                else:
                    self._currentCollapsedSize = self.size()
                    self._currentCollapsedMinSize = self.minimumSize()
                    self.popupTitleBarWidget.updateCollapseState(False)
                    self.setFixedSize(self.size().width(), self.popupTitleBarWidget.height() + 5)
                    self.container.setVisible(False)
                    self._isCollapsed = True
                    if self._isDockingAllowed: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

    #endregion

    #region Popup Methods

    def openPopup(self, parent: QWidget = None):
        if self.isVisible():
            self.closePopup()
            if not self._isPopup: 
                return
        
        if parent != None:
            result = self.getParentPopup(parent)
            if result != None:
                self._parentPopupWidget = result
                self._parentPopupWidget._isChildPopupFocused = True
        
        self.initPopupGeometry(parent)
        self.show()
        self.activateWindow()

        self._timeSinceOpened = QTime.currentTime()

        if self._hasBeenOpenedBefore == False:
            self._hasBeenOpenedBefore = True
            self.fixPopup(parent)
            

    def fixPopup(self, parent: QWidget = None):
        timeOffset = 50
        self._timeSinceOpened.addMSecs(250)
        self.closePopup(False)
        QTimer.singleShot(timeOffset, partial(self.openPopup, parent))
        QTimer.singleShot(timeOffset + 50, self.update)
    
    def closePopup(self, activateParent: bool = True):
        if self._isChildPopupFocused == True:
            return

        if self._timeSinceOpened.msecsTo(QTime.currentTime()) <= 250:
            self.activateWindow()
            return

        if not self._toggleViewAction.isChecked(): 
            self.activateWindow()
            return
        
        if self._isCollapsed: self.toggleShade()
        self._toggleViewAction.trigger()
        self.resetPopupGeometry()

        if self._parentPopupWidget and activateParent:
            self._parentPopupWidget._isChildPopupFocused = False
            QTimer.singleShot(150, self._parentPopupWidget.activateWindow)

    def dispose(self):
        if self.containerWidget:
            self.containerWidget.shutdownWidget()
            self.containerWidget.deleteLater()
            self.containerWidget = None
    
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.close()

    #endregion
    
    #region Signals

    def onComposerTriggerEnded(self):
        self._hasComposerWorkAround = False

    def onDockLocationChanged(self):
        if self._isWindow == False: return
        if not self.popupTitleBarWidget: return
        if self.isFloating(): self.popupTitleBarWidget.setFloatingVisibility(True)
        else: self.popupTitleBarWidget.setFloatingVisibility(False)

    def onShelfIndexChanged(self):
        if self._shrinkToFit:
            self.adjustSize()

    #endregion

    #region Events 

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self._canDrawFrame:
            painter = QPainter(self)
            painter.setPen(QPen(qApp.palette().color(QPalette.ColorRole.WindowText), 1))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def event(self, event: QEvent):
        try:
            if event.type() == QEvent.Type.WindowDeactivate:
                if self.isActiveWindow(): return super().event(event)
                if self._hasComposerWorkAround: return super().event(event)
                
                if self._closeOnDeactivation: self.closePopup()
                elif self._closeOnMouseLeave: pass

                elif self._isPopup: self.closePopup()
                elif self._isWindow: pass

            return super().event(event)
        except RuntimeError:
            return False
    
    def leaveEvent(self, event: QEvent):
        if event.type() == QEvent.Type.Leave:
            if self._closeOnMouseLeave:
                self.closePopup()

        return super().leaveEvent(event)

    def hideEvent(self, event):
        AnimatedWidget.hideEvent(self, event)

    def mousePressEvent(self, e: QMouseEvent):
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        return super().enterEvent(e)

    def shelfReloadEvent(self, state: ToolshelfArea):
        if state.options.resize_style == ToolshelfAreaSettings.ResizeStyle.Minimum:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self._shrinkToFit = True
        else:
            self.setSizePolicy(self._originalSizePolicy)
            self._shrinkToFit = False

        if self._shrinkToFit:
            self.adjustSize()
    
    #endregion
