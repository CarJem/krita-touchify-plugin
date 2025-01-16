"""
    Plugin for Krita UI Redesign, Copyright (C) 2020 Kapyia, Pedro Reis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""



from PyQt5.QtWidgets import QWidget, QDockWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QSize, QPoint

from touchify.src.components.touchify.canvas.NtScrollAreaContainer import NtScrollAreaContainer


from touchify.src.settings import *
from touchify.src.components.pyqt.extensions import PyQtExtensions as Ext

from krita import *

from typing import TYPE_CHECKING

from touchify.src.stylesheet import Stylesheet
if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

class NtWidgetPad(QWidget):
    """
    An on-canvas toolbox widget. I'm dubbing widgets that 'float' 
    on top of the canvas '(lily) pads' for the time being :) """


    def __init__(self, window: Window, canvas: "NtCanvas", allow_resizing: bool = False):
        super(NtWidgetPad, self).__init__(canvas.mdiArea)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        self.padLayout = QVBoxLayout(self)
        self.padLayout.setContentsMargins(4,4,4,4)
        self.setLayout(self.padLayout)

        self.source_window = window.qwindow()
        self.source_canvas = canvas

        self.source_mdi_area = self.source_window.findChild(QMdiArea)
        self.source_mdi_area.subWindowActivated.connect(self.subWindowActivatedEvent)        

        self.docker_widget = None
        self.docker_source = None

        self.canvas_x = 0
        self.canvas_y = 0
        self.canvas_alignment_x = Qt.AlignmentFlag.AlignLeft
        self.canvas_alignment_y = Qt.AlignmentFlag.AlignTop

        self.state_collapsed = True
        self.state_resizing = False

        self.option_returnDockerOnClose = True
        self.option_allow_resizing = allow_resizing
        self.option_resizing_enabled = False

        self.resizing_point_start = QPoint()
        self.resizing_grip_size = QSize(10, 10)
        self.resizing_corner: Qt.Corner | None = None

        self.collapseBtn = NtTogglePadButton(self)
        self.collapseBtn.clicked.connect(self.setCollapsed)
        self.padLayout.addWidget(self.collapseBtn)

        self.adjustArrow()
        
    #region States

    def widgetGrip(self, mousePos: QPoint):
        bottom_right = QRect(
            self.width() - self.resizing_grip_size.width(),
            self.height() - self.resizing_grip_size.height(),
            self.resizing_grip_size.width(),
            self.resizing_grip_size.height()
        )
        
        bottom_left = QRect(
            int(0),
            self.height() - self.resizing_grip_size.height(),
            self.resizing_grip_size.width(),
            self.resizing_grip_size.height(),
        )
            
        if bottom_left.contains(mousePos):
            return (True, Qt.Corner.BottomLeftCorner)
        elif bottom_right.contains(mousePos):
            return (True, Qt.Corner.BottomRightCorner)
        else:
            return (False, None)
     
    def widgetSize(self) -> QSize:
        if self.docker_widget:
            return self.docker_widget.size()
        return QSize(0,0)
    
    def widgetSizeHint(self) -> QSize:
        if self.docker_widget:
            return self.docker_widget.sizeHint()
        return QSize(0,0)    
    
    #endregion

    #region Setters

    def setCanvasData(self, x: int, y: int, align_x: Qt.AlignmentFlag, align_y: Qt.AlignmentFlag):
        self.canvas_x = x
        self.canvas_y = y

        match align_x:
            case Qt.AlignmentFlag.AlignLeft: self.canvas_alignment_x = align_x
            case Qt.AlignmentFlag.AlignHCenter: self.canvas_alignment_x = align_x
            case Qt.AlignmentFlag.AlignRight: self.canvas_alignment_x = align_x

        match align_y:
            case Qt.AlignmentFlag.AlignTop: self.canvas_alignment_y = align_y
            case Qt.AlignmentFlag.AlignVCenter: self.canvas_alignment_y = align_y
            case Qt.AlignmentFlag.AlignBottom: self.canvas_alignment_y = align_y
        
        self.adjustArrow()

    def setCollapsed(self, value: bool):
        if self.docker_widget: self.docker_widget.setVisible(value)
        self.state_collapsed = value

        self.adjustArrow()
        self.adjustToView()  

    def setResizable(self, value: bool):
        if self.option_allow_resizing: self.option_resizing_enabled = value
        self.adjustToView()
        self.adjustCursor(self.cursor().pos())
    
    #endregion

    #region Functions

    def borrowDocker(self, docker):
        """
        Borrow a docker widget from Krita's existing list of dockers and 
        returns True. Returns False if invalid widget was passed."""

        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():
            # Return any previous widget to its original docker
            self.returnDocker()
           
            self.docker_source = docker

            if isinstance(docker.widget(), QScrollArea):
                self.docker_widget = NtScrollAreaContainer(docker.widget())
            else:
                self.docker_widget = docker.widget()

            self.layout().addWidget(self.docker_widget) 
            self.adjustToView()        
            self.docker_source.hide()

            if self.state_collapsed: self.docker_widget.setVisible(False)

            return True
            
        return False
    
    def returnDocker(self):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if self.docker_source and self.docker_widget:
            if isinstance(self.docker_widget, NtScrollAreaContainer):
                self.docker_source.setWidget(self.docker_widget.scrollArea())
            else:
                self.docker_source.setWidget(self.docker_widget)

            if self.option_returnDockerOnClose:
                self.docker_source.show()
            self.docker_widget = None
            self.docker_source = None

    def adjustToView(self, delta_x: int = 0, delta_y: int = 0):
        """
        Adjust the position and size of the Pad to that of the active View."""
        if self.source_canvas == None: return
        if self.docker_widget == None: return

        geometry = self.source_canvas.geometry()
        local_geometry = self.source_canvas.localGeometry(self.canvas_x, self.canvas_y)
        target_pos = local_geometry.topLeft()

        center_x = int(local_geometry.center().x() - self.width() / 2)
        center_y = int(local_geometry.center().y() - self.height() / 2)
        
        if self.canvas_alignment_x == Qt.AlignmentFlag.AlignLeft:
            if self.canvas_alignment_y == Qt.AlignmentFlag.AlignTop: target_pos = local_geometry.topLeft()
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignBottom: target_pos = local_geometry.bottomLeft()
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignVCenter: target_pos = QPoint(local_geometry.left(), center_y)
        elif self.canvas_alignment_x == Qt.AlignmentFlag.AlignRight:
            if self.canvas_alignment_y == Qt.AlignmentFlag.AlignTop: target_pos = local_geometry.topRight()
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignBottom: target_pos = local_geometry.bottomRight()
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignVCenter: target_pos = QPoint(local_geometry.right(), center_y)
        elif self.canvas_alignment_x == Qt.AlignmentFlag.AlignHCenter:
            if self.canvas_alignment_y == Qt.AlignmentFlag.AlignTop: target_pos = QPoint(center_x, local_geometry.top())
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignBottom: target_pos = QPoint(center_x, local_geometry.bottom())
            elif self.canvas_alignment_y == Qt.AlignmentFlag.AlignVCenter: target_pos = QPoint(center_x, center_y)

        if target_pos.x() + self.width() >= geometry.right():
            target_pos.setX(geometry.right() - self.width())

        if target_pos.y() + self.height() >= geometry.bottom():
            target_pos.setY(geometry.bottom() - self.height())

        self.move(target_pos)

        cellSize = self.source_canvas.size()

        widgetSize = self.widgetSize()
        widgetSizeHint = self.widgetSizeHint()
        widgetNewSize = QSize(widgetSize.width() + delta_x, widgetSize.height() + delta_y)
        
        if self.option_resizing_enabled == False:
            widgetNewSize = QSize(widgetSizeHint)

        widgetNewSize = QSize(Ext.Geometry.fitToSource(widgetSizeHint, widgetNewSize))

        if cellSize.height() < widgetNewSize.height():
            widgetNewSize.setHeight(cellSize.height())
    
        if cellSize.width() < widgetNewSize.width():
            widgetNewSize.setWidth(cellSize.width())         
            
        if widgetSize != widgetNewSize:
            self.docker_widget.setFixedSize(widgetNewSize)
            
        padSizeHint = self.sizeHint()
        padSizeHint = Ext.Geometry.fitToTarget(padSizeHint, cellSize)

        if self.size() != padSizeHint: self.setFixedSize(padSizeHint)
        
    def adjustCursor(self, pos: QPoint):
        
        if self.option_resizing_enabled == False:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return
             
        result = self.state_resizing
        corner = self.resizing_corner
         
        if not result:
            (result, corner) = self.widgetGrip(pos)
            
        if result:
            match corner:
                case Qt.Corner.BottomLeftCorner:
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                case Qt.Corner.BottomRightCorner:
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor) 
                case _:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def adjustArrow(self):
        self.collapseBtn.setArrow(self.canvas_alignment_x, self.canvas_alignment_y, self.state_collapsed)

    #endregion

    #region Events

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.state_resizing = False
        self.adjustCursor(e.pos())
    
    def mousePressEvent(self, e: QMouseEvent):
        if self.option_resizing_enabled == True:
            (result, corner) = self.widgetGrip(e.pos())
            if result:
                self.resizing_point_start = QPoint(e.pos())
                self.resizing_corner = corner 
                self.state_resizing = True
            else:
                self.state_resizing = False
        self.adjustCursor(e.pos())
    
    def mouseMoveEvent(self, e: QMouseEvent):
        if self.state_resizing and self.docker_widget and self.resizing_corner != None:
            #adapt the widget size based on mouse movement
            delta: QPoint = e.pos() - self.resizing_point_start
            self.resizing_point_start = QPoint(e.pos())
            
            
            match self.resizing_corner:
                case Qt.Corner.BottomLeftCorner:
                    x = -delta.x()
                    y = delta.y()   
                case Qt.Corner.BottomRightCorner:
                    x = delta.x()
                    y = delta.y()      
            
            self.adjustToView(x, y)
        self.adjustCursor(e.pos())

    def subWindowActivatedEvent(self, subWin):
        self.source_canvas.updateView()

    def subWindowEvent(self):
        self.source_canvas.updateView()

    def closeEvent(self, e):
        """
        Since the plugins works by borrowing the actual docker 
        widget we need to ensure its returned upon closing the pad"""
        self.source_mdi_area.subWindowActivated.disconnect(self.subWindowActivatedEvent)        
        self.returnDocker()
        return super().closeEvent(e)

    def paintEvent(self, e):
        """
        Needed to resize the Pad if the user decides to 
        change the icon size of the toolbox"""
        self.adjustToView()
        super().paintEvent(e)
        #p = QPainter(self)
        
        #if self.autoSize == False:
            #gripAreas = self.gripAreas()
            #p.setPen(Qt.GlobalColor.red)
            #for area in gripAreas:      
                #p.drawRect(gripAreas[area])

    #endregion
    
class NtTogglePadButton(QToolButton):
    def __init__(self, parent: "NtWidgetPad"):
        super(NtTogglePadButton, self).__init__(parent)
        self.widget_pad = parent
        self.krita_window = self.widget_pad.source_canvas.app_engine.windowSource.qwindow()
        self.krita_window.themeChanged.connect(self.themeChangedEvent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        qApp.paletteChanged.connect(self.themeChangedEvent)
        self.themeChangedEvent()

    def setArrow(self, alignment_x: Qt.AlignmentFlag, alignment_y: Qt.AlignmentFlag, enabled: bool = True):
        if alignment_x == Qt.AlignmentFlag.AlignLeft:
            self.setArrowType(Qt.ArrowType.RightArrow if not enabled else Qt.ArrowType.LeftArrow)
        elif alignment_x == Qt.AlignmentFlag.AlignRight:
            self.setArrowType(Qt.ArrowType.LeftArrow if not enabled else Qt.ArrowType.RightArrow)
        elif alignment_x == Qt.AlignmentFlag.AlignHCenter:
            if alignment_y == Qt.AlignmentFlag.AlignTop:
                self.setArrowType(Qt.ArrowType.DownArrow if not enabled else Qt.ArrowType.UpArrow)
            elif alignment_y == Qt.AlignmentFlag.AlignBottom:
                self.setArrowType(Qt.ArrowType.UpArrow if not enabled else Qt.ArrowType.DownArrow)
            else:
                self.setArrowType(Qt.ArrowType.DownArrow if not enabled else Qt.ArrowType.UpArrow)
        else:
            self.setArrowType(Qt.ArrowType.RightArrow if not enabled else Qt.ArrowType.LeftArrow)

    def themeChangedEvent(self):
        iconSize: int = int(11 * TouchifySettings.instance().preferences().Interface_CanvasToggleScale)
        self.setIconSize(QSize(iconSize, iconSize))
        self.setStyleSheet(Stylesheet.instance().touchify_toggle_button)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.showMenu()
        else:
            return super().mousePressEvent(e)
