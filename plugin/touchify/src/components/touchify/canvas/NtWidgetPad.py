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


from enum import Enum
from PyQt5.QtWidgets import QWidget, QToolButton, QDockWidget, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt5.QtCore import Qt, QSize, QPoint

from ....ext.KritaSettings import KritaSettings

from ....settings.TouchifyConfig import *
from .... import stylesheet

from krita import *

class NtWidgetPad(QWidget):
    """
    An on-canvas toolbox widget. I'm dubbing widgets that 'float' 
    on top of the canvas '(lily) pads' for the time being :) """
    
    
    class Alignment(Enum):
        Left = 0
        Right = 1

    def __init__(self, parent):
        super(NtWidgetPad, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint
            )
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(4,4,4,4)
        self.alignment = NtWidgetPad.Alignment.Left

        self.offset_x_left = 0
        self.offset_x_right = 0

        # Members to hold a borrowed widget and it's original parent docker for returning
        self.widget = None
        self.widgetDocker = None

         # Visibility toggle
        self.btnHide = Nt_ToggleVisibleButton()
        self.btnHide.clicked.connect(self.toggleWidgetVisible)
        self.layout().addWidget(self.btnHide)
        
        self.gripSize = QSize(10, 10)
        self.oldResizePoint = QPoint()
        self.resizing = False
        
    def getResizeGripArea(self):
        if self.alignment == NtWidgetPad.Alignment.Left:
            x = self.width() - self.gripSize.width()
            y = self.height() - self.gripSize.height()
            width = self.gripSize.width()
            height = self.gripSize.height()
        elif self.alignment == NtWidgetPad.Alignment.Right:
            x = 0
            y = self.height() - self.gripSize.height()
            width = self.gripSize.width()
            height = self.gripSize.height()
        else:
            x = 0
            y = 0
            width = 0
            height = 0
        
        return (x, y, width, height)
        
    def mouseInGrip(self, mousePos: QPoint):
        x, y, width, height = self.getResizeGripArea()
        return QRect(x, y, width, height).contains(mousePos)

        
    def mousePressEvent(self, e: QMouseEvent):
        if self.mouseInGrip(e.pos()):
            self.oldResizePoint = QPoint(e.pos())
            self.resizing = True
        else:
            self.resizing = False
    
    def mouseMoveEvent(self, e: QMouseEvent):
        if self.resizing and self.widget:
            #adapt the widget size based on mouse movement
            delta: QPoint = e.pos() - self.oldResizePoint
            self.oldResizePoint = QPoint(e.pos())
        
            if self.alignment == NtWidgetPad.Alignment.Left:
                x = delta.x()
            elif self.alignment == NtWidgetPad.Alignment.Right:
                x = -delta.x()
            
            y = delta.y()   
            
            self.resizeToView(x, y)
        
            qApp.instance().processEvents()
            self.resizeToView()

            
    def fitToView(self, sizeToFit: QSize):
        def height_scale(input):
            return input + self.btnHide.height() + 14 + self.scrollBarMargin() + self.rulerMargin()
        
        def height_offset(input):
            return input - self.btnHide.height() - 14 - self.scrollBarMargin() - self.rulerMargin()
        
        def width_offset(input):
            return input - 8 - self.scrollBarMargin()
        
        def width_scale(input):
            return input + 8 + self.scrollBarMargin()
        
        view = self.activeView()
        
        result = QSize(sizeToFit)

        if view:   
            if view.height() < height_scale(result.height()):
                result.setHeight(height_offset(view.height()))
        
            if view.width() < width_scale(result.width()):
                result.setWidth(width_offset(view.width()))
                
        return result

    def fitSize(self, sourceSize: QSize, targetSize: QSize):
        """
        Resize the target size to fit the source size"""
        
        result: QSize = QSize(targetSize)
        
        if sourceSize.width() > result.width():
            result.setWidth(sourceSize.width())
                
        if sourceSize.height() > result.height():
            result.setHeight(sourceSize.height())
            
        return result
    
    def widgetSize(self) -> QSize:
        if self.widget:
            return self.widget.size()
        return QSize(0,0)
    
    def widgetSizeHint(self) -> QSize:
        if self.widget:
            return self.widget.sizeHint()
        return QSize(0,0)    



    def activeView(self) -> QWidget:
        """
        Get the View widget of the active subwindow."""
        if not self.parentWidget():
            return None 
        
        subWin = self.parentWidget().activeSubWindow()
        
        if not subWin:
            return None

        for child in subWin.children(): 
            if 'view' in child.objectName(): # Grab the View from the active tab/sub-window
                return child
        
        return None 

    def adjustToView(self):
        """
        Adjust the position and size of the Pad to that of the active View."""
        
        view = self.activeView()

        if view:          
            self.resizeToView()

            globalTargetPos = QPoint()
            if self.alignment == NtWidgetPad.Alignment.Left:
                globalTargetPos = view.mapToGlobal(QPoint(self.rulerMargin() + self.offset_x_left, self.rulerMargin()))
            elif self.alignment == NtWidgetPad.Alignment.Right:
                globalTargetPos = view.mapToGlobal(QPoint(view.width() - self.width() - self.scrollBarMargin() - self.offset_x_right, self.rulerMargin()))

            newPos = self.parentWidget().mapFromGlobal(globalTargetPos)
            if self.pos() != newPos:
                self.move(newPos)

    def borrowDocker(self, docker):
        """
        Borrow a docker widget from Krita's existing list of dockers and 
        returns True. Returns False if invalid widget was passed."""

        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():
            # Return any previous widget to its original docker
            self.returnDocker()
           
            self.widgetDocker = docker

            if isinstance(docker.widget(), QScrollArea):
                self.widget = Nt_ScrollAreaContainer(docker.widget())
            else:
                self.widget = docker.widget()

            self.layout().addWidget(self.widget) 
            self.adjustToView()        
            self.widgetDocker.hide()

            return True
            
        return False

    def closeEvent(self, e):
        """
        Since the plugins works by borrowing the actual docker 
        widget we need to ensure its returned upon closing the pad"""
        self.returnDocker()
        return super().closeEvent(e)

    def paintEvent(self, e):
        """
        Needed to resize the Pad if the user decides to 
        change the icon size of the toolbox"""
        self.adjustToView()
        super().paintEvent(e)
        p = QPainter(self)
        
        x, y, width, height = self.getResizeGripArea()
        p.setPen(Qt.GlobalColor.red)
        p.drawRect(x, y, width, height)


    def resizeToView(self, delta_x: int = 0, delta_y: int = 0):
        """
        Resize the Pad to an appropriate size that fits within the subwindow."""
        
        view = self.activeView()
        
        if view:
            widgetSize = self.widgetSize()
            widgetSizeHint = self.widgetSizeHint()
            widgetNewSize = QSize(widgetSize.width() + delta_x, widgetSize.height() + delta_y)
                              
            widgetNewSize = self.fitToView(self.fitSize(widgetSizeHint, widgetNewSize))                   
            if widgetSize != widgetNewSize:
                self.widget.setFixedSize(widgetNewSize)
                
            padSizeHint = self.sizeHint()
            if view.height() < padSizeHint.height():
                padSizeHint.setHeight(view.height())

            if view.width() < padSizeHint.width():
                padSizeHint.setWidth(view.width())
            
            if self.size() != padSizeHint:
                self.resize(padSizeHint)

    def returnDocker(self):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if self.widgetDocker and self.widget:
            if isinstance(self.widget, Nt_ScrollAreaContainer):
                self.widgetDocker.setWidget(self.widget.scrollArea())
            else:
                self.widgetDocker.setWidget(self.widget)

            self.widgetDocker.show()
            self.widget = None
            self.widgetDocker = None

    def rulerMargin(self):
        if KritaSettings.showRulers():
            return 20 # Canvas ruler pixel width on Windows
        return 0

    def setWidget(self, e):
        self.widget = e
        self.layout().addWidget(self.widget) 
        self.adjustToView()        

    def scrollBarMargin(self):
        if KritaSettings.hideScrollbars():
            return 0

        return 14 # Canvas crollbar pixel width/height on Windows 

    def setViewAlignment(self, newAlignment: Alignment):
        """
        Set the Pad's alignment to the view to either 'left' or 'right'. 
        Returns False if the argument is an invalid value."""
        self.btnHide.setArrow(self.alignment)
        if self.alignment != newAlignment:
            self.alignment = newAlignment
            return True
    
        return False

    def toggleWidgetVisible(self, value=None):
        if not value:
            value = not self.widget.isVisible()
        
        self.widget.setVisible(value)
        self.adjustToView()  
        self.updateHideButtonIcon(value)

    def updateHideButtonIcon(self, isVisible): 
        """
        Flip the direction of the arrow to fit the Pads current visibility"""
        if self.alignment == NtWidgetPad.Alignment.Left:
            if isVisible:
                self.btnHide.setArrowType(Qt.ArrowType.LeftArrow)
            else:
                self.btnHide.setArrowType(Qt.ArrowType.RightArrow)
        elif self.alignment == NtWidgetPad.Alignment.Right:
            if isVisible:
                self.btnHide.setArrowType(Qt.ArrowType.RightArrow)
            else:
                self.btnHide.setArrowType(Qt.ArrowType.LeftArrow)
    

class Nt_ToggleVisibleButton(QToolButton):
    def __init__(self, parent = None):
        super(Nt_ToggleVisibleButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setIconSize(QSize(11, 11))
        self.setStyleSheet(stylesheet.touchify_toggle_button)
        
    def setArrow(self, alignment):
        if alignment == NtWidgetPad.Alignment.Right:
            self.setArrowType(Qt.ArrowType.RightArrow)
        else:
            self.setArrowType(Qt.ArrowType.LeftArrow)

class Nt_ScrollAreaContainer(QWidget):

    def __init__(self, scrollArea = None, parent=None):
        super(Nt_ScrollAreaContainer, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.sa = None
        
        self.setScrollArea(scrollArea)





    def sizeHint(self):
        """
        Reimplemented function. If a QScrollArea as been set
        the size hint of it's widget will be returned."""
        if self.sa and self.sa.widget():
            return self.sa.widget().sizeHint()

        return super().sizeHint()


    def setScrollArea(self, scrollArea):
        """
        Set the QScrollArea for the container to hold.

        True will be returned upon success and if no prior QScrollArea was set. 
        If another QScrollArea was already set it will be returned so that 
        it can be disposed of properly.
        
        If an invalid arguement (i.e. not a QScrollArea) or the same QScrollArea
        as the currently set one is passed, nothing happens and False is returned."""
        if (isinstance(scrollArea, QScrollArea) and
            scrollArea is not self.sa):
            ret = True

            if not self.sa:
                self.layout().addWidget(scrollArea)
            else:
                self.layout().replaceWidget(self.sa, scrollArea)
                ret = self.sa # set the old QScrollArea to be returned
            
            self.sa = scrollArea
            return ret
        
        return False

    def scrollArea(self):
        return self.sa