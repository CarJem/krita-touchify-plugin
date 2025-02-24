from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from touchify.__env__ import *
from touchify.src.api_krita import KritaAPI
from touchify.src.config.popup.PopupData import PopupData
from touchify.src.config.toolshelf.ToolshelfData import ToolshelfData
import touchify.src.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.components.common.widget.AnimatedWidget import AnimatedWidget
from touchify.src.components.common.labels.ElidedLabel import ElidedLabel
from touchify.src.components.toolshelf.ToolshelfWidget import ToolshelfWidget
from touchify.src.managers.shared.settings import TouchifySettings
from touchify.src.managers.shared.settings_krita import KritaSettings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow
    from touchify.src.managers.normal.action_manager import ActionManager
    from touchify.src.managers.normal.dockers import DockerManager
    from touchify.src.managers.normal.canvas import CanvasManager


class TouchifyPopup(QDockWidget, AnimatedWidget):

    class LayoutState:
        def __init__(self, x: int, y: int, width: int, height: int):
            self.__x = x
            self.__y = y
            self.__width = width
            self.__height = height

        @staticmethod
        def prase(state_str: str):
            try:
                results = list(map(int, state_str.split(",")))
                if len(results) == 4:
                    return TouchifyPopup.LayoutState(results[0], results[1], results[2], results[3])
                else:
                    return None
            except:
                return None
            
        def position(self, main_window: QMainWindow):
            widget_position = QPoint(self.__x, self.__y)
            window_position = main_window.pos()
            actual_x = window_position.x() + widget_position.x()
            actual_y = window_position.y() + widget_position.y()
            return QPoint(actual_x, actual_y)

        def positionRelative(main_window: QMainWindow, widget: QDockWidget) -> QPoint:
            window_position = main_window.pos()
            widget_position = widget.pos()
            relative_x = widget_position.x() - window_position.x()
            relative_y = widget_position.y() - window_position.y()
            relative_position = QPoint(relative_x, relative_y)
            return relative_position

            
        def value(self):
            return f"{self.__x},{self.__y},{self.__width},{self.__height}"
        
        def width(self):
            return self.__width
        
        def height(self):
            return self.__height

    class Titlebar(QWidget):
        def __init__(self, parent_popup: "TouchifyPopup"):
            super().__init__(parent_popup)
            self.parent_popup = parent_popup
            self.setObjectName("touchify_popup_titlebar")

            self.isMoving = False

            self.setFixedHeight(17)
            
            
            self.ourLayout = QHBoxLayout(self)
            self.ourLayout.setContentsMargins(0,0,0,0)
            self.setLayout(self.ourLayout)


            self.titlebarText = ElidedLabel(self)
            self.titlebarText.setText(self.parent_popup.config.window_title)
            self.ourLayout.addWidget(self.titlebarText)

            if self.parent_popup.State_Window_isFixed == PopupData.WindowFixedLayoutMode.On or \
                  self.parent_popup.State_Window_isFixed == PopupData.WindowFixedLayoutMode.OnRequest:
                restoreMenu = QMenu(self)
                storeFixedLocationAct = restoreMenu.addAction("Store Fixed Layout...")
                storeFixedLocationAct.triggered.connect(self.parent_popup.FixedLayoutState_Store)
                restoreFixedLocationAct = restoreMenu.addAction("Restore Fixed Layout...")
                restoreFixedLocationAct.triggered.connect(self.parent_popup.FixedLayoutState_Restore)

                self.restoreLocation = QPushButton(self)
                self.restoreLocation.setIcon(KritaAPI.get_icon('settings-button'))
                self.restoreLocation.setFixedSize(18,18)
                self.restoreLocation.setMenu(restoreMenu)
                self.restoreLocation.setFlat(True)
                self.ourLayout.addWidget(self.restoreLocation)
            else:
                self.restoreLocation = None

            self.minimizeBtn = QPushButton(self)
            self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_a'))
            self.minimizeBtn.setFixedSize(18,18)
            self.minimizeBtn.clicked.connect(self.parent_popup.Action_ToggleCollapse)
            self.minimizeBtn.setFlat(True)
            self.ourLayout.addWidget(self.minimizeBtn)

            self.closeButton = QPushButton(self)
            self.closeButton.setIcon(KritaAPI.get_icon('docker_close'))
            self.closeButton.setFixedSize(18,18)
            self.closeButton.setFlat(True)
            self.closeButton.clicked.connect(self.parent_popup.Popup_Close)
            self.ourLayout.addWidget(self.closeButton)

        def updateCollapseState(self, is_collapsed: bool):
            if is_collapsed:
                self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_a'))
                if self.restoreLocation: self.restoreLocation.setEnabled(True)
            else:
                self.minimizeBtn.setIcon(KritaAPI.get_icon('docker_collapse_b'))
                if self.restoreLocation: self.restoreLocation.setEnabled(False)
                

        def setFloatingVisibility(self, value: bool):
            self.minimizeBtn.setVisible(value)
            if self.restoreLocation: self.restoreLocation.setVisible(value)
    
    class GeometryInfo:
        def __init__(self, position: QPoint, size: QSize):
            self.position: QPoint = position
            self.size: QSize = size

    def __init__(self, parent: QWidget, id: str, args: PopupData, toolshelf_data: ToolshelfData, app_engine: "TouchifyWindow"):     
        QDockWidget.__init__(self, parent)  
        #TODO: Improve Performance
        AnimatedWidget.__init__(self, parent, 0) #0.1        
        self.Variables(id, args, toolshelf_data, app_engine)
        self.Components()
        self.Connections()

    def Variables(self, id: str, args: PopupData, toolshelf_data: ToolshelfData, app_engine: "TouchifyWindow"):
        self.config = args
        self.registry_id = id
        self.app_engine: "TouchifyWindow" = app_engine
        self.docker_manager: "DockerManager" = app_engine.mgr_dockers
        self.actions_manager: "ActionManager" = app_engine.mgr_actions
        self.canvas_manager: "CanvasManager" = app_engine.mgr_canvas
        self.toolshelf_data = toolshelf_data
        self.main_window = self.app_engine.krita_window.qwindow()
        self.toggle_view_action = self.toggleViewAction()


        self.State_timeSinceOpening = QTime()
        self.State_isCollapsed = False
        self.State_collapsedOldSize = None
        self.State_collapsedOldMinSize = None
        self.State_composerWorkAround = False
        self.State_childPopupFocused: bool = False
        self.State_parentPopup: TouchifyPopup | None = None
        self.State_containerParent: QWidget | None = None
        self.State_hasOpenedOnce = False
        self.State_dockWidgetType = self.config.window_type
        self.State_resizingAllowed = self.State_dockWidgetType == PopupData.WindowType.Window
        self.State_resizingEnabled = self.toolshelf_data.header_options.default_to_resize_mode if self.State_resizingAllowed else False
        self.State_currentDockLocation = Qt.DockWidgetArea.NoDockWidgetArea

        if self.State_dockWidgetType == PopupData.WindowType.Window:
            self.State_Window_drawFrame = False
            self.State_Window_rememberLayout = self.config.window_remember_layout
            self.State_Window_isDockingAllowed = self.config.window_docking_allowed
            self.State_Window_isFixed = self.config.window_fixed_layout
        else:
            self.State_Window_drawFrame = True
            self.State_Window_rememberLayout = False
            self.State_Window_isDockingAllowed = False
            self.State_Window_isFixed = PopupData.WindowFixedLayoutMode.Off

    def Components(self):
        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        
        self.container_widget = QWidget(self)
        self.container_widget.setContentsMargins(1,1,1,1) # essential to draw the frame properly
        self.container_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidget(self.container_widget)

        self.container_grid = QVBoxLayout(self)
        self.container_grid.setContentsMargins(0,0,0,0)
        self.container_grid.setSpacing(0)
        self.container_widget.setLayout(self.container_grid)

        self.toolshelf_widget = ToolshelfWidget(self, self.toolshelf_data)
        self.toolshelf_widget.dataLoaded.connect(self.OnEvent_ToolshelfUpdated)
        self.toolshelf_widget.toolshelfResized.connect(self.OnEvent_ToolshelfUpdated)
        self.toolshelf_widget.toolshelfPageChanged.connect(self.OnEvent_ToolshelfUpdated)
        self.container_grid.addWidget(self.toolshelf_widget)

        if self.State_dockWidgetType == PopupData.WindowType.Window:
            self.container_titlebar = TouchifyPopup.Titlebar(self)
            self.setTitleBarWidget(self.container_titlebar)
        else:
            self.container_titlebar = None
            self.setTitleBarWidget(QWidget(self))
            
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas \
            if self.State_Window_isDockingAllowed \
            else Qt.DockWidgetArea.NoDockWidgetArea)
        
    def Connections(self):
        self.dockLocationChanged.connect(self.OnEvent_DockLocationChanged)

    def Construct(id: str, parent: QWidget, data: PopupData, app_engine: "TouchifyWindow"):      
        from touchify.src.config.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions
        from touchify.src.config.toolshelf.ToolshelfDataPage import ToolshelfDataPage
        from touchify.src.config.toolshelf.ToolshelfDataSection import ToolshelfDataSection
        
        def constructDockerType(metadata: PopupData):  
            toolshelf_data: ToolshelfData = ToolshelfData()
            toolshelf_data.header_options = ToolshelfDataOptions()
            toolshelf_data.homepage = ToolshelfDataPage()
            toolshelf_data.header_options.show_menu_button = False
            toolshelf_data.header_options.show_pin_button = False
            toolshelf_data.header_options.show_tabs = False
            toolshelf_data.header_options.show_titlebar = False
            toolshelf_data.header_options.default_to_resize_mode = True


            dockers = [ ]

            if metadata.type == PopupData.Variants.MultipleDockers:
                from touchify.src.config.docker_group.DockerItem import DockerItem
                for item in metadata.dockers_list:
                    item: DockerItem
                    dockers.append(item.id)
            else:
                dockers.append(metadata.docker_id)
            
            toolshelf_data.homepage.tab_type = metadata.dockers_tab_type

            for docker_id in dockers:
                docker_section: ToolshelfDataSection = ToolshelfDataSection()
                docker_section.section_type = ToolshelfDataSection.SectionType.Docker
                docker_section.docker_nesting_mode = ToolshelfDataSection.DockerNestingMode.Docking
                docker_section.docker_unloaded_visibility = ToolshelfDataSection.DockerUnloadedVisibility.Hidden
                docker_section.docker_id = docker_id
                docker_section.size_x = metadata.popup_width
                docker_section.size_y = metadata.popup_height
                docker_section.min_size_x = metadata.popup_min_width
                docker_section.min_size_y = metadata.popup_min_height
                toolshelf_data.homepage.sections.append(docker_section)

            return toolshelf_data
        
        def constructActionType(metadata: PopupData):
            toolshelf_data: ToolshelfData = ToolshelfData()
            toolshelf_data.header_options = ToolshelfDataOptions()
            toolshelf_data.homepage = ToolshelfDataPage()
            toolshelf_data.header_options.show_menu_button = False
            toolshelf_data.header_options.show_pin_button = False
            toolshelf_data.header_options.show_tabs = False
            toolshelf_data.header_options.show_titlebar = False


            action_section: ToolshelfDataSection = ToolshelfDataSection()
            action_section.section_type = ToolshelfDataSection.SectionType.Actions
            action_section.action_section_icon_size =  metadata.actions_icon_size
            action_section.action_section_display_mode = ToolshelfDataSection.ActionSectionDisplayMode.Detailed
            action_section.action_section_contents = metadata.actions_items
            action_section.action_section_btn_height = metadata.actions_item_height
            action_section.action_section_btn_width = metadata.actions_item_width
            action_section.min_size_x = metadata.popup_min_width
            action_section.min_size_y = metadata.popup_min_height
            action_section.size_x = metadata.popup_width
            action_section.size_y = metadata.popup_height

            toolshelf_data.homepage.sections.append(action_section)
            return toolshelf_data

        match data.type:
            case PopupData.Variants.Actions:
                toolshelf_data: ToolshelfData = constructActionType(data)
            case PopupData.Variants.Docker |PopupData.Variants.MultipleDockers:
                toolshelf_data: ToolshelfData = constructDockerType(data)
            case PopupData.Variants.Toolshelf:
                toolshelf_data: ToolshelfData = TouchifySettings.instance().getRegistryItem(data.toolshelf_id, ToolshelfData)
            case _:
                toolshelf_data = None
        
        if not isinstance(toolshelf_data, ToolshelfData) or toolshelf_data == None: return None                
        return TouchifyPopup(parent, id, data, toolshelf_data, app_engine)

    #region Geometry Methods

    def Geometry_GetParentBounds(self, container: QWidget = None):
        if container == None:
            parent_pos = QPoint(0,0)
            parent_width = 0
            parent_height = 0
        else:
            parent_pos = container.mapToGlobal(QPoint(0,0))
            parent_width = container.width()
            parent_height = container.height()

        return TouchifyPopup.GeometryInfo(parent_pos, QSize(parent_width, parent_height))

    def Geometry_GetWindowBounds(self, container: QWidget = None):
        window_size = self.Geometry_GetWindowHint()
        bounds_info = self.Geometry_GetParentBounds(container)

        if not container:
            mouse_point = QCursor().pos()
            window_x = mouse_point.x()
            window_y = mouse_point.y()
        else:
            window_x = bounds_info.position.x() + (bounds_info.size.width() // 2) - (window_size.width() // 2)
            window_y = bounds_info.position.y() + (bounds_info.size.height())

        match self.config.popup_position_x:
            case PopupData.PopupPosition.Start:
                window_x -= 0 
            case PopupData.PopupPosition.Center:
                window_x -= (window_size.width() // 2) 
            case PopupData.PopupPosition.End:
                window_x -= window_size.width()
            case _:
                window_x -= 0 

        match self.config.popup_position_y:
            case PopupData.PopupPosition.Start:
                window_y -= 0 
            case PopupData.PopupPosition.Center:
                window_y -= (window_size.height() // 2) 
            case PopupData.PopupPosition.End:
                window_y -= window_size.height()
            case _:
                window_y -= 0 

        return TouchifyPopup.GeometryInfo(QPoint(window_x, window_y), window_size)

    def Geometry_GetWindowHint(self) -> QSize:
        if self.State_dockWidgetType == PopupData.WindowType.Popup and self.toolshelf_widget:
            dialog_width = self.sizeHint().width()
            dialog_height = self.sizeHint().height()
        else:
            dialog_width = self.minimumSizeHint().width()
            dialog_height = self.minimumSizeHint().height()

        return QSize(int(dialog_width), int(dialog_height))

    def Geometry_Init(self, parent: QWidget = None):
        self.State_containerParent = parent

        last_state = self.LastLayoutState_Previous()
        fixed_state = self.FixedLayoutState_Previous()

        if self.State_Window_isFixed == PopupData.WindowFixedLayoutMode.On and fixed_state != None:
            fixed_pos = fixed_state.position(self.main_window)
            hint_x, hint_y = fixed_pos.x(), fixed_pos.y()
            hint_width, hint_height = fixed_state.width(), fixed_state.height()
        elif self.State_Window_rememberLayout and last_state != None:
            last_pos = last_state.position(self.main_window)
            hint_x, hint_y = last_pos.x(), last_pos.y()
            hint_width, hint_height = last_state.width(), last_state.height()
        else:
            window_bounds = self.Geometry_GetWindowBounds(parent)
            hint_x, hint_y = window_bounds.position.x(), window_bounds.position.y()
            hint_width, hint_height = window_bounds.size.width(), window_bounds.size.height()

        info = TouchifyPopup.GeometryInfo(QPoint(hint_x, hint_y), QSize(hint_width, hint_height))
        if self.config.clamp_to_main_window:
            info.position = PyQtExtensions.GeometryHelpers.clampToTarget(info.position, info.size, self.main_window)
        self.setGeometry(info.position.x(), info.position.y(), info.size.width(), info.size.height())
        self.Geometry_Apply(info)

    def Geometry_Reset(self):
        self.State_containerParent = None

    def Geometry_Update(self):
        window_bounds = self.Geometry_GetWindowBounds(self.State_containerParent)
        self.Geometry_Apply(window_bounds)

    def Geometry_Apply(self, info: GeometryInfo):
        match self.State_dockWidgetType:
            case PopupData.WindowType.Popup:
                self.resize(info.size)
                self.move(info.position)
            case PopupData.WindowType.Window:
                if not self.State_isCollapsed:
                    self.setMinimumSize(info.size)
                    if not self.State_resizingEnabled:
                        self.resize(info.size)
            case _:
                pass


    #endregion

    #region OnEvent Methods

    def OnEvent_ToolshelfUpdated(self):
        self.State_timeSinceOpening = QTime.currentTime()
        self.Geometry_Update()

    def OnEvent_ComposerEnd(self):
        self.State_composerWorkAround = False

    def OnEvent_DockLocationChanged(self):
        self.State_currentDockLocation = self.main_window.dockWidgetArea(self)
        if self.State_dockWidgetType != PopupData.WindowType.Window: return
        if not self.container_titlebar: return
        if self.isFloating(): self.container_titlebar.setFloatingVisibility(True)
        else: self.container_titlebar.setFloatingVisibility(False)

    #endregion

    #region Action Methods

    def Action_SetResizable(self, value: bool):
        if self.State_resizingAllowed:
            self.State_resizingEnabled = value
            self.OnEvent_ToolshelfUpdated()

    def Action_ToggleCollapse(self):
        if self.State_dockWidgetType == PopupData.WindowType.Window:
            if self.container_titlebar:
                if self.State_isCollapsed:
                    self.setMinimumSize(self.State_collapsedOldMinSize)
                    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                    self.resize(self.State_collapsedOldSize)
                    self.container_titlebar.updateCollapseState(True)
                    self.container_widget.setVisible(True)
                    self.State_collapsedOldSize = None
                    self.State_collapsedOldMinSize = None
                    self.State_isCollapsed = False
                    if self.State_Window_isDockingAllowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
                else:
                    self.State_collapsedOldSize = self.size()
                    self.State_collapsedOldMinSize = self.minimumSize()
                    self.container_titlebar.updateCollapseState(False)
                    self.setFixedSize(self.size().width(), self.container_titlebar.height() + 5)
                    self.container_widget.setVisible(False)
                    self.State_isCollapsed = True
                    if self.State_Window_isDockingAllowed: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)

    #endregion

    #region Popup Methods

    def Popup_Open(self, parent: QWidget = None):
        if self.isVisible():
            self.Popup_Close()
            if not self.State_dockWidgetType == PopupData.WindowType.Popup: 
                return
        
        if parent != None:
            result = self.Popup_Parent(parent)
            if result != None:
                self.State_parentPopup = result
                self.State_parentPopup.State_childPopupFocused = True
        
        self.Geometry_Init(parent)
        self.show()
        self.activateWindow()

        self.State_timeSinceOpening = QTime.currentTime()

    def Popup_Close(self):
        if self.State_childPopupFocused == True:
            return

        if self.State_timeSinceOpening.msecsTo(QTime.currentTime()) <= 250:
            self.activateWindow()
            return

        if not self.toggle_view_action.isChecked(): 
            self.activateWindow()
            return
        
        if self.State_isCollapsed: self.Action_ToggleCollapse()
        self.toggle_view_action.trigger()

        self.State_hasOpenedOnce = True
        self.Geometry_Reset()

        if self.State_Window_rememberLayout: self.LastLayoutState_Store()

        if self.State_parentPopup:
            self.State_parentPopup.State_childPopupFocused = False
            QTimer.singleShot(150, self.State_parentPopup.activateWindow)

    def Popup_Shutdown(self):
        if self.toolshelf_widget:
            self.toolshelf_widget.shutdownWidget()
            self.toolshelf_widget.deleteLater()
            self.toolshelf_widget = None
    
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.close()

    def Popup_Parent(self, source: QWidget) -> "TouchifyPopup":
        from touchify.src.components.special.TouchifyPopup import TouchifyPopup
        try:
            widget = source.parentWidget()
            while (widget):
                foo = widget
                if isinstance(foo, TouchifyPopup):
                    return foo
                widget = widget.parentWidget()
            return None
        except:
            return None    
    
    #endregion

    #region LayoutState Methods

    def LayoutState_Current(self):
        current_location = TouchifyPopup.LayoutState.positionRelative(self.main_window, self)
        current_size = self.size()
        return TouchifyPopup.LayoutState(current_location.x(), current_location.y(), current_size.width(), current_size.height())


    def LastLayoutState_Previous(self) -> LayoutState | None:
        if self.isFloating() and self.State_isCollapsed == False:
            state_str: str = KritaSettings.readSetting(TOUCHIFY_SETTINGPATH_POPUPS_LAST_LOCATIONS, self.registry_id, "")
            return TouchifyPopup.LayoutState.prase(state_str)
        else:
            return None

    def LastLayoutState_Store(self):
        if self.isFloating() and self.State_isCollapsed == False:
            current_state = self.LayoutState_Current()
            KritaSettings.writeSetting(TOUCHIFY_SETTINGPATH_POPUPS_LAST_LOCATIONS, self.registry_id, current_state.value(), False)


    def FixedLayoutState_Previous(self) -> LayoutState | None:
        if self.isFloating() and self.State_isCollapsed == False:
            state_str: str = KritaSettings.readSetting(TOUCHIFY_SETTINGPATH_POPUPS_FIXED_LOCATIONS, self.registry_id, "")
            return TouchifyPopup.LayoutState.prase(state_str)
        else:
            return None
    
    def FixedLayoutState_Store(self):
        if self.isFloating() and self.State_isCollapsed == False:
            current_state = self.LayoutState_Current()
            KritaSettings.writeSetting(TOUCHIFY_SETTINGPATH_POPUPS_FIXED_LOCATIONS, self.registry_id, current_state.value(), False)

    def FixedLayoutState_Restore(self):
        state = self.FixedLayoutState_Previous()
        if state and self.State_isCollapsed == False:
            self.setFloating(True)
            self.move(state.position(self.main_window))
            self.resize(state.width(), state.height())

    #endregion
    
    #region Events 

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self.State_Window_drawFrame:
            painter = QPainter(self)
            painter.setPen(QPen(qApp.palette().color(QPalette.ColorRole.WindowText), 1))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def event(self, event: QEvent):
        try:
            if event.type() == QEvent.Type.WindowDeactivate:
                if self.isActiveWindow(): return super().event(event)
                if self.State_composerWorkAround: return super().event(event)
                
                if self.config.closing_method == PopupData.ClosingMethod.Deactivation: self.Popup_Close()
                elif self.config.closing_method == PopupData.ClosingMethod.MouseLeave: pass

                elif self.State_dockWidgetType == PopupData.WindowType.Popup: self.Popup_Close()
                elif self.State_dockWidgetType == PopupData.WindowType.Window: pass

            return super().event(event)
        except RuntimeError:
            return False
    
    def leaveEvent(self, event: QEvent):
        if event.type() == QEvent.Type.Leave:
            if self.config.closing_method == PopupData.ClosingMethod.MouseLeave:
                self.Popup_Close()

        return super().leaveEvent(event)

    def hideEvent(self, event):
        AnimatedWidget.hideEvent(self, event)

    def mousePressEvent(self, e: QMouseEvent):
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        return super().enterEvent(e)
    
    #endregion
