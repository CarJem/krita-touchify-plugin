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

            self.minimizeBtn = QPushButton(self)
            self.minimizeBtn.setIcon(Krita.instance().icon('arrow-down'))
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
    
    def __init__(self, parent: QWidget, args: PopupData, toolshelf_data: ToolshelfData, app_engine: "TouchifyWindow"):     
        super().__init__(parent)  

        self.isVisibleAction = self.toggleViewAction()
        self.dockLocationChanged.connect(self.onDockLocationChanged)

        self.config = args

        self.time_since_opening = QTime()

        self.is_collapsed = False
        self.collapsed_old_size = None
        self.collapsed_old_min_size = None

        self.composer_work_around = False

        self.parent_popup: TouchifyPopup | None = None
        self.child_popup_focused: bool = False

        self.closing_method = args.closing_method
        self.display_type = args.window_type
        self.last_location_saved = False
        self.draw_frame = False
        self.docking_allowed = False
        self.remember_location = False

        self.app_engine: "TouchifyWindow" = app_engine
        self.docker_manager: "DockerManager" = app_engine.docker_management
        self.actions_manager: "ActionManager" = app_engine.action_management
        self.canvas_manager: "CanvasManager" = app_engine.canvas_management
        self.toolshelf_data = toolshelf_data

        self.resizing_allowed = self.display_type == PopupData.WindowType.Window
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

        self.container_grid = QVBoxLayout(self)
        self.container_grid.setContentsMargins(0,0,0,0)
        self.container_grid.setSpacing(0)
        self.container_widget.setLayout(self.container_grid)

        self.toolshelf_widget = ToolshelfWidget(self, self.toolshelf_data)
        self.toolshelf_widget.sizeChanged.connect(self.requestViewUpdate)
        self.container_grid.addWidget(self.toolshelf_widget)

        if self.display_type == PopupData.WindowType.Popup:
            self.draw_frame = True
            self.docking_allowed = False
            self.remember_location = False
            self.setTitleBarWidget(QWidget(self))
            
        elif self.display_type == PopupData.WindowType.Window:
            self._toolbar = TouchifyPopup.Titlebar(self)
            self.docking_allowed = args.window_docking_allowed
            self.remember_location = args.window_remember_location
            self.setTitleBarWidget(self._toolbar)

        if self.docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        else: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)




    def construct(parent: QWidget, data: PopupData, app_engine: "TouchifyWindow"):      
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
                from touchify.src.cfg.docker_group.DockerGroupItem import DockerGroupItem
                for item in metadata.dockers_list:
                    item: DockerGroupItem
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
        return TouchifyPopup(parent, data, toolshelf_data, app_engine)
                

    #region Helper Methods

    def getGeometry(self, position, width, height, isMouse = False):
        dialog_width, dialog_height = self.generateSize()

        screen = QGuiApplication.screenAt(position)
        screen_geometry = screen.geometry()
        screenSize = screen.size()

        screen_x = screen_geometry.x()
        screen_y = screen_geometry.y()
        screen_height = screenSize.height()
        screen_width = screenSize.width()

        
        offset_x = position.x() 
        offset_y = position.y()
        
        if not isMouse:
            offset_x += (width // 2) - (dialog_width // 2)
            offset_y += (height)


        match self.config.popup_position_x:
            case PopupData.PopupPosition.Start:
                offset_x -= 0 
            case PopupData.PopupPosition.Center:
                offset_x -= (dialog_width // 2) 
            case PopupData.PopupPosition.End:
                offset_x -= dialog_width
            case _:
                offset_x -= 0 

        match self.config.popup_position_y:
            case PopupData.PopupPosition.Start:
                offset_y -= 0 
            case PopupData.PopupPosition.Center:
                offset_y -= (dialog_height // 2) 
            case PopupData.PopupPosition.End:
                offset_y -= dialog_height
            case _:
                offset_y -= 0 

        actual_x = offset_x
        actual_y = offset_y

        if actual_x + dialog_width > screen_x + screen_width:
            actual_x = screen_x + screen_width - dialog_width
        elif actual_x < screen_x:
            actual_x = screen_x

        if actual_y + dialog_height > screen_y + screen_height:
            actual_y = screen_y + screen_height - dialog_height

        return [actual_x, actual_y, dialog_width, dialog_height]

    def getActionSource(self, parent: QWidget | None):
        if parent != None:
            return self.getGeometry(parent.mapToGlobal(QPoint(0,0)), parent.width(), parent.height())
        else:
            return 0, 0, 0, 0

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

    def generateSize(self):
        if self.display_type == PopupData.WindowType.Popup and self.toolshelf_widget:
            dialog_width = self.sizeHint().width()
            dialog_height = self.sizeHint().height()
        else:
            dialog_width = self.minimumSizeHint().width()
            dialog_height = self.minimumSizeHint().height()

        return [int(dialog_width), int(dialog_height)]
    
    def updateSize(self, dialog_width: int, dialog_height: int):
        if self.display_type == PopupData.WindowType.Popup:
            self.setFixedSize(dialog_width, dialog_height)
        elif self.display_type == PopupData.WindowType.Window:
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
            self.isVisibleAction.trigger()

            if self.remember_location:
                self.last_location_saved = True

            if self.parent_popup:
                self.parent_popup.child_popup_focused = False
                self.parent_popup.activateWindow()

    def triggerPopup(self, parent: QWidget = None):
        if self.isVisible():
            self.closePopup()
            if not self.display_type == PopupData.WindowType.Popup: 
                return
        
        if parent != None:
            result = self.getParentPopup(parent)
            if result != None:
                self.parent_popup = result
                self.parent_popup.child_popup_focused = True
        
        if self.last_location_saved == False:
            actual_x = 0
            actual_y = 0
            dialog_width = 0
            dialog_height = 0

            if not self.isFloating():
                self.setFloating(True)

            if parent == None:
                actual_x, actual_y, dialog_width, dialog_height = self.getGeometry(QCursor.pos(), 0, 0, True)
            else:
                actual_x, actual_y, dialog_width, dialog_height = self.getActionSource(parent)
            
            self.setGeometry(actual_x, actual_y, dialog_width, dialog_height)
            self.updateSize(dialog_width, dialog_height)
            self.show()
        else:
            self.show()

        if self.display_type == PopupData.WindowType.Popup:
            self.activateWindow()
            
        self.time_since_opening = QTime.currentTime()



    def toggleShade(self):
        if self.display_type == PopupData.WindowType.Window:
            if self._toolbar:
                if self.is_collapsed:
                    self.setMinimumSize(self.collapsed_old_min_size)
                    self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)
                    self.resize(self.collapsed_old_size)
                    self.container_widget.setVisible(True)
                    self.collapsed_old_size = None
                    self.collapsed_old_min_size = None
                    self.is_collapsed = False
                    if self.docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
                else:
                    self.collapsed_old_size = self.size()
                    self.collapsed_old_min_size = self.minimumSize()
                    self.setFixedSize(self._toolbar.width(), self._toolbar.height() + 1)
                    self.container_widget.setVisible(False)
                    self.is_collapsed = True
                    if self.docking_allowed: self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
    
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
        if self.display_type != PopupData.WindowType.Window: return
        if not self._toolbar: return
        if self.isFloating():
            self._toolbar.minimizeBtn.setVisible(True)
        else:
            self._toolbar.minimizeBtn.setVisible(False)

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
    
            elif self.display_type == PopupData.WindowType.Popup: self.closePopup()
            elif self.display_type == PopupData.WindowType.Window: pass

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
