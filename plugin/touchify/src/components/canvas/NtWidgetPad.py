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



from dataclasses import dataclass
from enum import Enum
from PyQt5.QtWidgets import QWidget, QDockWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QSize, QPoint

from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.canvas.NtScrollAreaContainer import NtScrollAreaContainer


from touchify.src.managers.shared.settings import *
import touchify.src.extensions.pyqt_extensions as Ext

from krita import *

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .NtCanvas import NtCanvas

DEBUG_DRAW=False

class NtWidgetPad(QWidget):
    """
    An on-canvas toolbox widget. I'm dubbing widgets that 'float' 
    on top of the canvas '(lily) pads' for the time being :) """

    class HandleLocation(Enum):
        Invalid=0
        Top=1
        TopRight=2
        Right=3
        BottomRight=4
        Bottom=5
        BottomLeft=6
        Left=7
        TopLeft=8
    
    @dataclass
    class HandleDragData:
        x: int
        y: int
        width: int
        height: int


    SIGNAL_RESIZED = pyqtSignal(QWidget)

    def __init__(self, window: WindowAPI, canvas: "NtCanvas", allow_resizing: bool = False):
        super(NtWidgetPad, self).__init__(canvas.MdiArea())
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        self.padLayout = QVBoxLayout(self)
        self.padLayout.setContentsMargins(6,6,6,6)
        self.setLayout(self.padLayout)

        self.source_window = window.qwindow()
        self.source_canvas = canvas

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
        self.resizing_handle: NtWidgetPad.HandleLocation = NtWidgetPad.HandleLocation.Invalid

        self.collapseBtn = NtTogglePadButton(self)
        self.collapseBtn.clicked.connect(self.setCollapsed)
        self.padLayout.addWidget(self.collapseBtn)

        self.adjustArrow()
        
    #region States

    def currentOffset(self, mousePos: QPoint):
        delta: QPoint = mousePos - self.resizing_point_start
        self.resizing_point_start = mousePos
    
        match self.resizing_handle:
            case NtWidgetPad.HandleLocation.BottomLeft:
                x = 0
                y = 0
                width = -delta.x()
                height = delta.y()   
            case NtWidgetPad.HandleLocation.BottomRight:
                x = 0
                y = 0
                width = delta.x()
                height = delta.y()      
            case NtWidgetPad.HandleLocation.TopLeft:
                x = 0
                y = 0
                width = -delta.x()
                height = -delta.y()   
            case NtWidgetPad.HandleLocation.TopRight:
                x = 0
                y = 0
                width = delta.x()
                height = -delta.y()      
            case NtWidgetPad.HandleLocation.Left:
                x = 0
                y = 0
                width = -delta.x()
                height = 0
            case NtWidgetPad.HandleLocation.Right:
                x = 0
                y = 0
                width = delta.x()
                height = 0     
            case NtWidgetPad.HandleLocation.Top:
                x = 0
                y = 0
                width = 0
                height = -delta.y()
            case NtWidgetPad.HandleLocation.Bottom:
                x = 0
                y = 0
                width = 0
                height = delta.y()     
            case _:
                x = 0
                y = 0
                width = 0
                height = 0

        

        return NtWidgetPad.HandleDragData(x,y,width,height)
    
    def currentGrip(self, mousePos: QPoint):
        areas = self.widgetGrips()

        if areas["corner_bottom_left_a"].contains(mousePos) or areas["corner_bottom_left_b"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.BottomLeft)
        if areas["corner_bottom_right_a"].contains(mousePos) or areas["corner_bottom_right_b"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.BottomRight)
        if areas["corner_top_left_a"].contains(mousePos) or areas["corner_top_left_b"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.TopLeft)
        if areas["corner_top_right_a"].contains(mousePos) or areas["corner_top_right_b"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.TopRight)
        
        if areas["border_left"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.Left)
        if areas["border_right"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.Right)
        if areas["border_top"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.Top)
        if areas["border_bottom"].contains(mousePos):
            return (True, NtWidgetPad.HandleLocation.Bottom)
        
        return (False, None)
    
    def widgetGrips(self):
        actual_size = self.size().grownBy(QMargins(1,1,1,1))

        grip_width = 4
        grip_height = 4
        grip_offset_width = 6
        grip_offset_height = 6

        result = {}

        result["border_left"] = QRect(0, 0, grip_width, grip_height + actual_size.height())
        result["border_right"] = QRect(actual_size.width() - grip_offset_width, 0, grip_width, grip_height + actual_size.height())
        result["border_top"] = QRect(0, 0, actual_size.width(), grip_height)
        result["border_bottom"] = QRect(0, actual_size.height() - grip_offset_height, grip_width + actual_size.width(), grip_height)

        result["corner_bottom_left_a"] = QRect(0, actual_size.height() - grip_offset_height * 2, grip_width, grip_height * 2)
        result["corner_bottom_left_b"] = QRect(0, actual_size.height() - grip_offset_height, grip_width * 2, grip_height)

        result["corner_top_left_a"] = QRect(0, 0, grip_width, grip_height * 2)
        result["corner_top_left_b"] = QRect(0, 0, grip_width * 2, grip_height)

        result["corner_bottom_right_a"] = QRect(actual_size.width() - grip_offset_width, actual_size.height() - grip_offset_height * 2, grip_width, grip_height * 2)
        result["corner_bottom_right_b"] = QRect(actual_size.width() - grip_offset_width * 2, actual_size.height() - grip_offset_height, grip_width * 2, grip_height)

        result["corner_top_right_a"] = QRect(actual_size.width() - grip_offset_width, 0, grip_width, grip_height * 2)
        result["corner_top_right_b"] = QRect(actual_size.width() - grip_offset_width * 2, 0, grip_width * 2, grip_height)

        return result

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

    def setCanvasData(self, align_x: Qt.AlignmentFlag, align_y: Qt.AlignmentFlag):
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
        self.repaint()

    def setResizable(self, value: bool):
        if self.option_allow_resizing: self.option_resizing_enabled = value
        self.adjustToView()
        self.adjustCursor(self.cursor().pos())
        self.repaint()
    
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

    def adjustToView(self, drag_data: HandleDragData = None):
        """
        Adjust the position and size of the Pad to that of the active View."""
        
        if drag_data:
            offset_x = drag_data.x
            offset_y = drag_data.y
            offset_width = drag_data.width
            offset_height = drag_data.height
        else:
            offset_x = 0
            offset_y = 0
            offset_width = 0
            offset_height = 0
        
        
        def fitToView(_view: QWidget, _sizeToFit: QSize):
            def height_scale(input):
                return input + self.collapseBtn.height() + 14
            
            def height_offset(input):
                return input - self.collapseBtn.height() - 14
            
            def width_offset(input):
                return input
            
            def width_scale(input):
                return input
            
            result = QSize(_sizeToFit)

            if _view.height() < height_scale(result.height()):
                result.setHeight(height_offset(_view.height()))
        
            if _view.width() < width_scale(result.width()):
                result.setWidth(width_offset(_view.width()))
                    
            return result
        
        


        if self.source_canvas and self.docker_widget != None:          
            widgetSize = self.widgetSize()
            widgetSizeHint = self.widgetSizeHint()
            widgetNewSize = QSize(widgetSize.width() + offset_width, widgetSize.height() + offset_height)
            
            if self.option_resizing_enabled == False:
                widgetNewSize = QSize(widgetSizeHint)
                                           
            widgetNewSize = fitToView(self.source_canvas, Ext.GeometryHelpers.fitToSource(widgetSizeHint, widgetNewSize))                   
            if widgetSize != widgetNewSize:
                self.docker_widget.setFixedSize(widgetNewSize)
                
            padSizeHint = self.sizeHint()
            padSizeHint = Ext.GeometryHelpers.fitToTarget(padSizeHint, self.source_canvas.size())

            if self.size() != padSizeHint:
                self.resize(padSizeHint)
                

    def resizeEvent(self, a0: QResizeEvent):
        self.SIGNAL_RESIZED.emit(self)
        return super().resizeEvent(a0)

    def adjustCursor(self, pos: QPoint):
        
        if self.option_resizing_enabled == False:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return
             
        (result, handle) = self.currentGrip(pos)
        
        match handle:
            case NtWidgetPad.HandleLocation.BottomLeft | NtWidgetPad.HandleLocation.TopRight:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            case NtWidgetPad.HandleLocation.BottomRight | NtWidgetPad.HandleLocation.TopLeft:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor) 
            case NtWidgetPad.HandleLocation.Left | NtWidgetPad.HandleLocation.Right:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            case NtWidgetPad.HandleLocation.Top | NtWidgetPad.HandleLocation.Bottom:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            case _:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            
    def adjustArrow(self):
        self.collapseBtn.setArrow(self.canvas_alignment_x, self.canvas_alignment_y, self.state_collapsed)

    #endregion
  
    #region Events

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.state_resizing = False
        self.adjustCursor(e.pos())
    
    def leaveEvent(self, a0):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().leaveEvent(a0)

    def mousePressEvent(self, e: QMouseEvent):
        if self.option_resizing_enabled == True:
            (result, corner) = self.currentGrip(e.pos())
            if result:
                self.resizing_point_start = QPoint(e.pos())
                self.resizing_handle = corner 
                self.state_resizing = True
            else:
                self.state_resizing = False
        self.adjustCursor(e.pos())
    
    def mouseMoveEvent(self, e: QMouseEvent):
        if self.state_resizing and self.docker_widget and self.resizing_handle != None:
            #adapt the widget size based on mouse movement
            self.adjustToView(self.currentOffset(e.pos()))
        self.adjustCursor(e.pos())
    
    def closeEvent(self, e):
        """
        Since the plugins works by borrowing the actual docker 
        widget we need to ensure its returned upon closing the pad"""
        self.returnDocker()
        return super().closeEvent(e)

    def paintEvent(self, e: QPaintEvent):
        """
        Needed to resize the Pad if the user decides to 
        change the icon size of the toolbox"""
        self.adjustToView()
        super().paintEvent(e)

        if DEBUG_DRAW: self.paintDebugEvent(e)

    def paintDebugEvent(self, e: QPaintEvent):
        if self.option_resizing_enabled == True:
            p = QPainter(self)
            gripAreas = self.widgetGrips()

            for area in sorted(gripAreas):      
                rect = gripAreas[area]

                is_border = str(area).startswith("border_")

                if is_border: 
                    p.setBrush(Qt.GlobalColor.magenta)
                    p.setPen(Qt.GlobalColor.magenta)
                else: 
                    p.setBrush(Qt.GlobalColor.white)
                    p.setPen(Qt.GlobalColor.white)

                p.drawRect(rect)
    
    #endregion
    
class NtTogglePadButton(QToolButton):
    def __init__(self, parent: "NtWidgetPad"):
        super(NtTogglePadButton, self).__init__(parent)
        self.widget_pad = parent
        self.krita_window = self.widget_pad.source_canvas.app_engine.krita_window.qwindow()
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
        stylesheet = f"""
            QToolButton, QPushButton {{
                background-color: palette(window);
                border: none;
                border-radius: 4px;
            }}
            
            QToolButton:hover, QPushButton:hover {{
                background-color: palette(highlight);
            }}
            
            QToolButton:pressed, QPushButton:pressed {{
                background-color: palette(alternate-base);
            }}
            
            QToolButton::menu-indicator, QPushButton::menu-indicator {{ image: none; }}
        """

        self.setIconSize(QSize(iconSize, iconSize))
        self.setStyleSheet(stylesheet)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.MouseButton.RightButton:
            self.showMenu()
        else:
            return super().mousePressEvent(e)
