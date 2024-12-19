from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from touchify.src.cfg.popup.PopupData import PopupData
from touchify.src.components.pyqt.widgets.ElidedLabel import ElidedLabel
from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import ToolshelfWidget
from touchify.src.settings import *
from touchify.src.resources import *

from krita import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow
    from touchify.src.action_manager import ActionManager
    from touchify.src.docker_manager import DockerManager
    from touchify.src.canvas_manager import CanvasManager


class TouchifyPopup(QDockWidget):

    class LayoutState:
        def __init__(self, x: int, y: int, width: int, height: int):
            self.__x = x
            self.__y = y
            self.__width = width
            self.__height = height

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

        def positionRelative(main_window: QMainWindow, widget: QDockWidget):
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

            if self.parent_popup.window_fixed_layout_mode == PopupData.WindowFixedLayoutMode.On or \
                  self.parent_popup.window_fixed_layout_mode == PopupData.WindowFixedLayoutMode.OnRequest:
                restoreMenu = QMenu(self)
                storeFixedLocationAct = restoreMenu.addAction("Store Fixed Layout...")
                storeFixedLocationAct.triggered.connect(self.parent_popup.storeFixedLayoutState)
                restoreFixedLocationAct = restoreMenu.addAction("Restore Fixed Layout...")
                restoreFixedLocationAct.triggered.connect(self.parent_popup.restoreFixedLayoutState)

                self.restoreLocation = QPushButton(self)
                self.restoreLocation.setIcon(Krita.instance().icon('settings-button'))
                self.restoreLocation.setFixedSize(18,18)
                self.restoreLocation.setMenu(restoreMenu)
                self.restoreLocation.setFlat(True)
                self.ourLayout.addWidget(self.restoreLocation)
            else:
                self.restoreLocation = None

            self.minimizeBtn = QPushButton(self)
            self.minimizeBtn.setIcon(Krita.instance().icon('docker_collapse_a'))
            self.minimizeBtn.setFixedSize(18,18)
            self.minimizeBtn.clicked.connect(self.parent_popup.toggleShade)
            self.minimizeBtn.setFlat(True)
            self.ourLayout.addWidget(self.minimizeBtn)

            self.closeButton = QPushButton(self)
            self.closeButton.setIcon(Krita.instance().icon('docker_close'))
            self.closeButton.setFixedSize(18,18)
            self.closeButton.setFlat(True)
            self.closeButton.clicked.connect(self.parent_popup.closePopup)
            self.ourLayout.addWidget(self.closeButton)

        def updateCollapseState(self, is_collapsed: bool):
            if is_collapsed:
                self.minimizeBtn.setIcon(Krita.instance().icon('docker_collapse_a'))
                if self.restoreLocation: self.restoreLocation.setEnabled(True)
            else:
                self.minimizeBtn.setIcon(Krita.instance().icon('docker_collapse_b'))
                if self.restoreLocation: self.restoreLocation.setEnabled(False)
                

        def setFloatingVisibility(self, value: bool):
            self.minimizeBtn.setVisible(value)
            if self.restoreLocation: self.restoreLocation.setVisible(value)
    
    def __init__(self, parent: QWidget, id: str, args: PopupData, toolshelf_data: ToolshelfData, app_engine: "TouchifyWindow"):     
        super().__init__(parent)  

        self.isVisibleAction = self.toggleViewAction()
        self.dockLocationChanged.connect(self.onDockLocationChanged)
        self.current_dock_location = Qt.DockWidgetArea.NoDockWidgetArea

        self.config = args
        self.registry_id = id
        self.time_since_opening = QTime()
        self.is_collapsed = False
        self.collapsed_old_size = None
        self.collapsed_old_min_size = None
        self.composer_work_around = False
        self.parent_popup: TouchifyPopup | None = None
        self.child_popup_focused: bool = False
        self.has_previously_opened = False


        self.app_engine: "TouchifyWindow" = app_engine
        self.docker_manager: "DockerManager" = app_engine.docker_management
        self.actions_manager: "ActionManager" = app_engine.action_management
        self.canvas_manager: "CanvasManager" = app_engine.canvas_management
        self.toolshelf_data = toolshelf_data

        self.main_window = self.app_engine.windowSource.qwindow()
        self.closing_method = args.closing_method
        self.clamp_to_main_window = args.clamp_to_main_window
        self.dock_widget_type = args.window_type

        self.resizing_allowed = self.dock_widget_type == PopupData.WindowType.Window
        self.resizing_enabled = self.toolshelf_data.header_options.default_to_resize_mode if self.resizing_allowed else False

        self.setAutoFillBackground(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setMouseTracking(True)
        
        self.container_widget = QWidget(self)
        self.container_widget.setContentsMargins(1,1,1,1) # essential to draw the frame properly
        self.container_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setWidget(self.container_widget)

        self.setFixedWidth()

        self.container_grid = QVBoxLayout(self)
        self.container_grid.setContentsMargins(0,0,0,0)
        self.container_grid.setSpacing(0)
        self.container_widget.setLayout(self.container_grid)

        self.toolshelf_widget = ToolshelfWidget(self, self.toolshelf_data)
        self.toolshelf_widget.sizeChanged.connect(self.requestViewUpdate)
        self.container_grid.addWidget(self.toolshelf_widget)

        if self.dock_widget_type == PopupData.WindowType.Popup:
            self.draw_frame = True
            self.window_docking_allowed = False
            self.window_remember_layout = False
            self.window_fixed_layout_mode = PopupData.WindowFixedLayoutMode.Off
            self.setTitleBarWidget(QWidget(self))
            
        elif self.dock_widget_type == PopupData.WindowType.Window:
            self.draw_frame = False
            self.window_docking_allowed = args.window_docking_allowed
            self.window_remember_layout = args.window_remember_layout
            self.window_fixed_layout_mode = args.window_fixed_layout
            self._toolbar = TouchifyPopup.Titlebar(self)
            self.setTitleBarWidget(self._toolbar)

        if self.window_docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        else: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)




    def construct(id: str, parent: QWidget, data: PopupData, app_engine: "TouchifyWindow"):      
        from touchify.src.cfg.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions
        from touchify.src.cfg.toolshelf.ToolshelfDataPage import ToolshelfDataPage
        from touchify.src.cfg.toolshelf.ToolshelfDataSection import ToolshelfDataSection
        
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
                from touchify.src.cfg.docker_group.DockerItem import DockerItem
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
                

    #region Helper Methods

    def getParentPopup(self, source: QWidget):
        from touchify.src.components.touchify.special.TouchifyPopup import TouchifyPopup
        try:
            widget = source.parent()
            while (widget):
                foo = widget
                if isinstance(foo, TouchifyPopup):
                    return foo
                widget = widget.parent()
            return None
        except:
            return None


    #endregion

    #region Size Methods

    def prepareSize(self,  parent: QWidget = None):
        def OffsetPosition(__hint_width: int, __hint_height: int):
            if parent == None:
                parent_pos = QCursor.pos()
                parent_width = 0
                parent_height = 0

                offset_x = parent_pos.x()
                offset_y = parent_pos.y()
            else:
                parent_pos = parent.mapToGlobal(QPoint(0,0))
                parent_width = parent.width()
                parent_height = parent.height()

                offset_x = parent_pos.x() + (parent_width // 2) - (__hint_width // 2)
                offset_y = parent_pos.y() + (parent_height)

            match self.config.popup_position_x:
                case PopupData.PopupPosition.Start:
                    offset_x -= 0 
                case PopupData.PopupPosition.Center:
                    offset_x -= (__hint_width // 2) 
                case PopupData.PopupPosition.End:
                    offset_x -= __hint_width
                case _:
                    offset_x -= 0 

            match self.config.popup_position_y:
                case PopupData.PopupPosition.Start:
                    offset_y -= 0 
                case PopupData.PopupPosition.Center:
                    offset_y -= (__hint_height // 2) 
                case PopupData.PopupPosition.End:
                    offset_y -= __hint_height
                case _:
                    offset_y -= 0 
        
            return [offset_x, offset_y]

        def ClampPosition(__x: int, __y: int, __hint_width: int, __hint_height: int):
            screen_x = self.main_window.geometry().x()
            screen_y = self.main_window.geometry().y()
            screen_height = self.main_window.size().height()
            screen_width = self.main_window.size().width()

            if __x + __hint_width > screen_x + screen_width:
                __x = screen_x + screen_width - __hint_width
            elif __x < screen_x:
                __x = screen_x

            if __y + __hint_height > screen_y + screen_height:
                __y = screen_y + screen_height - __hint_height

            return [__x, __y]

        last_state = self.getLastLayoutState()
        fixed_state = self.getFixedLayoutState()

        hint_width, hint_height = self.generateSize()
        hint_x, hint_y = OffsetPosition(hint_width, hint_height)

        if self.window_fixed_layout_mode == PopupData.WindowFixedLayoutMode.On and fixed_state != None:
            fixed_pos = fixed_state.position(self.main_window)
            hint_x, hint_y = fixed_pos.x(), fixed_pos.y()
            hint_width, hint_height = fixed_state.width(), fixed_state.height()

        elif self.window_remember_layout and last_state != None:
            last_pos = last_state.position(self.main_window)
            hint_x, hint_y = last_pos.x(), last_pos.y()
            hint_width, hint_height = last_state.width(), last_state.height()


        if self.clamp_to_main_window:
            hint_x, hint_y = ClampPosition(hint_x, hint_y, hint_width, hint_height)

        self.setGeometry(hint_x, hint_y, hint_width, hint_height)
        self.updateSize(hint_width, hint_height)

    def generateSize(self):
        if self.dock_widget_type == PopupData.WindowType.Popup and self.toolshelf_widget:
            dialog_width = self.sizeHint().width()
            dialog_height = self.sizeHint().height()
        else:
            dialog_width = self.minimumSizeHint().width()
            dialog_height = self.minimumSizeHint().height()

        return [int(dialog_width), int(dialog_height)]
    
    def updateSize(self, dialog_width: int, dialog_height: int):
        if self.dock_widget_type == PopupData.WindowType.Popup:
            self.setFixedSize(dialog_width, dialog_height)
        elif self.dock_widget_type == PopupData.WindowType.Window:
            if self.is_collapsed == False:
                self.setMinimumSize(dialog_width, dialog_height)
                if self.resizing_enabled == False:
                    self.resize(dialog_width, dialog_height)

    #endregion

    #region Interface Methods

    def requestViewUpdate(self):
        size = self.generateSize()
        self.updateSize(size[0], size[1])

    def updateResizingState(self, value: bool):
        if self.resizing_allowed:
            self.resizing_enabled = value
            self.requestViewUpdate()
    #endregion

    #region Window Methods

    def closePopup(self):
        if self.child_popup_focused: return

        if self.isVisibleAction.isChecked():
            if self.is_collapsed: self.toggleShade()
            self.isVisibleAction.trigger()

            self.has_previously_opened = True


            if self.window_remember_layout:    
                self.storeLastLayoutState()

            if self.parent_popup:
                self.parent_popup.child_popup_focused = False
                self.parent_popup.activateWindow()

    def triggerPopup(self, parent: QWidget = None):
        if self.isVisible():
            self.closePopup()
            if not self.dock_widget_type == PopupData.WindowType.Popup: 
                return
        
        if parent != None:
            result = self.getParentPopup(parent)
            if result != None:
                self.parent_popup = result
                self.parent_popup.child_popup_focused = True
        
        self.prepareSize(parent)
        self.show()
        
        if self.dock_widget_type == PopupData.WindowType.Popup:
            self.activateWindow()
            
        self.time_since_opening = QTime.currentTime()


    def getLastLayoutState(self) -> LayoutState | None:
        if self.isFloating() and self.is_collapsed == False:
            state_str: str = KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_POPUPS_LAST_LOCATIONS, self.registry_id, "")
            return TouchifyPopup.LayoutState.prase(state_str)
        else:
            return None

    def getFixedLayoutState(self) -> LayoutState | None:
        if self.isFloating() and self.is_collapsed == False:
            state_str: str = KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_POPUPS_FIXED_LOCATIONS, self.registry_id, "")
            return TouchifyPopup.LayoutState.prase(state_str)
        else:
            return None
    
    def getCurrentLayoutState(self):
        current_location = TouchifyPopup.LayoutState.positionRelative(self.main_window, self)
        current_size = self.size()
        return TouchifyPopup.LayoutState(current_location.x(), current_location.y(), current_size.width(), current_size.height())

    def storeLastLayoutState(self):
        if self.isFloating() and self.is_collapsed == False:
            current_state = self.getCurrentLayoutState()
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_POPUPS_LAST_LOCATIONS, self.registry_id, current_state.value(), False)

    def storeFixedLayoutState(self):
        if self.isFloating() and self.is_collapsed == False:
            current_state = self.getCurrentLayoutState()
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_POPUPS_FIXED_LOCATIONS, self.registry_id, current_state.value(), False)

    def restoreFixedLayoutState(self):
        state = self.getFixedLayoutState()
        if state and self.is_collapsed == False:
            self.setFloating(True)
            self.move(state.position(self.main_window))
            self.resize(state.width(), state.height())


    def toggleShade(self):
        if self.dock_widget_type == PopupData.WindowType.Window:
            if self._toolbar:
                if self.is_collapsed:
                    self.setMinimumSize(self.collapsed_old_min_size)
                    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                    self.resize(self.collapsed_old_size)
                    self._toolbar.updateCollapseState(True)
                    self.container_widget.setVisible(True)
                    self.collapsed_old_size = None
                    self.collapsed_old_min_size = None
                    self.is_collapsed = False
                    if self.window_docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
                else:
                    self.collapsed_old_size = self.size()
                    self.collapsed_old_min_size = self.minimumSize()
                    self._toolbar.updateCollapseState(False)
                    self.setFixedSize(self.size().width(), self._toolbar.height() + 5)
                    self.container_widget.setVisible(False)
                    self.is_collapsed = True
                    if self.window_docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
    
    def shutdownWidget(self):
        if self.toolshelf_widget:
            self.toolshelf_widget.shutdownWidget()
            self.toolshelf_widget.deleteLater()
            self.toolshelf_widget = None
    
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.close()

    #endregion
    
    #region Events 

    def onDockLocationChanged(self):
        self.current_dock_location = self.main_window.dockWidgetArea(self)
        if self.dock_widget_type != PopupData.WindowType.Window: return
        if not self._toolbar: return
        if self.isFloating(): self._toolbar.setFloatingVisibility(True)
        else: self._toolbar.setFloatingVisibility(False)

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        if self.draw_frame:
            painter = QPainter(self)
            painter.setPen(QPen(qApp.palette().color(QPalette.ColorRole.WindowText), 1))
            painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def composerEndEvent(self):
        self.composer_work_around = False

    def event(self, event: QEvent):
        if event.type() == QEvent.Type.WindowDeactivate:
            if self.isActiveWindow(): return super().event(event)
            if self.composer_work_around: return super().event(event)
            
            if self.closing_method == PopupData.ClosingMethod.Deactivation: self.closePopup()
            elif self.closing_method == PopupData.ClosingMethod.MouseLeave: pass
    
            elif self.dock_widget_type == PopupData.WindowType.Popup: self.closePopup()
            elif self.dock_widget_type == PopupData.WindowType.Window: pass

        return super().event(event)

    def leaveEvent(self, event: QEvent):
        if event.type() == QEvent.Type.Leave:
            if self.closing_method == PopupData.ClosingMethod.MouseLeave:
                self.closePopup()

        return super().leaveEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)

    def mousePressEvent(self, e: QMouseEvent):
        return super().mousePressEvent(e)

    def enterEvent(self, e: QEnterEvent):
        return super().enterEvent(e)
    
    #endregion
