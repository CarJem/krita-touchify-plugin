from enum import Enum
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from touchify.src.components.toolshelf.ShelfDockWidget import ShelfDockWidget
from touchify.src.managers.shared.resources import ResourceManager

class ShelfFloatingDockWidget(ShelfDockWidget):

    class TitlebarWidget(QWidget):

        sigButtonToggled = pyqtSignal(bool)

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

    def __init__(self):
        super().__init__()
        self._alignment = self.WidgetAlignment.TopLeft
        self._edgePosition = QPoint(0,0)
        self._isCollapsed = False
        self._collapsed_size = QSize()
        self._collapsed_position = QPoint()
        self._max_width = 1
        self._max_height = 1
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
        self.startTimer(25)

        self._titlebar = self.TitlebarWidget(self)
        self._titlebar.sigButtonToggled.connect(self.onToggled)
        self.setTitleBarWidget(self._titlebar)
        

    def onToggled(self, state: bool):
        self.widget().setVisible(not state)

    def timerEvent(self, a0):
        self.syncPosition()
        return super().timerEvent(a0)

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
            
    def move(self, point: QPoint):
        if self.shrinkToFit:
            self.adjustSize()
        super().move(point)   

    def resizeEvent(self, a0):
        if self.shrinkToFit:
            self.adjustSize()
        return super().resizeEvent(a0)

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

        if self.width() > _max_width or self.height() > _max_height:
            self.setMaximumSize(_max_width, _max_height)

        if self.pos() != _position:
            self.move(_position)