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

from .NtScrollAreaContainer import NtScrollAreaContainer
from .NtTogglePadButton import NtTogglePadButton

from ....ext.KritaSettings import KritaSettings
from .NtWidgetPadAlignment import NtWidgetPadAlignment

from ....settings.TouchifyConfig import *
from ....ext.extensions_pyqt import PyQtExtensions as Ext

from krita import *

class NtWidgetPad(QWidget):
    """
    An on-canvas toolbox widget. I'm dubbing widgets that 'float' 
    on top of the canvas '(lily) pads' for the time being :) """


    def __init__(self, parent, allowResizing: bool = False):
        super(NtWidgetPad, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint
            )
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(4,4,4,4)
        self.alignment = NtWidgetPadAlignment.Left

        self.offset_x_left = 0
        self.offset_x_right = 0
        
        self.setMouseTracking(True)
        

        # Members to hold a borrowed widget and it's original parent docker for returning
        self.widget = None
        self.widgetDocker = None
        

         # Visibility toggle
        self.btnHide = NtTogglePadButton()
        self.btnHide.clicked.connect(self.toggleWidgetVisible)
        self.layout().addWidget(self.btnHide)
        
        
        #region Auto Sizing Toggle
        self.allowResizing = allowResizing
        self.resizingEnabled = False
        self.resizingToggleAction = QAction(self)
        self.resizingToggleAction.setText("Allow resizing")
        self.resizingToggleAction.setCheckable(True)
        self.resizingToggleAction.changed.connect(self.allowResizingChanged)
        self.resizingToggleAction.setEnabled(self.allowResizing)
        
        if self.allowResizing:
            self.contextMenu = QMenu(self.btnHide)
            self.contextMenu.addAction(self.resizingToggleAction)
            self.btnHide.setMenu(self.contextMenu)
        
        self.gripSize = QSize(10, 10)
        self.resizeStart = QPoint()
        self.resizeCorner: Qt.Corner | None = None
        self.resizing = False
        
    #region States
    def mouseInGrip(self, mousePos: QPoint):
        gripAreas = self.gripAreas()
            
        if gripAreas["bottom_left"].contains(mousePos):
            return (True, Qt.Corner.BottomLeftCorner)
        elif gripAreas["bottom_right"].contains(mousePos):
            return (True, Qt.Corner.BottomRightCorner)
        else:
            return (False, None)
            
        
    #endregion

    #region Getters     
    def gripAreas(self):
        bottom_right = QRect(
            self.width() - self.gripSize.width(),
            self.height() - self.gripSize.height(),
            self.gripSize.width(),
            self.gripSize.height()
        )
        
        bottom_left = QRect(
            int(0),
            self.height() - self.gripSize.height(),
            self.gripSize.width(),
            self.gripSize.height(),
        )
        
        return {
            "bottom_left": bottom_left,
            "bottom_right": bottom_right
        }
    
    def widgetSize(self) -> QSize:
        if self.widget:
            return self.widget.size()
        return QSize(0,0)
    
    def widgetSizeHint(self) -> QSize:
        if self.widget:
            return self.widget.sizeHint()
        return QSize(0,0)    
    
    def rulerMargin(self):
        if KritaSettings.showRulers():
            return 20 # Canvas ruler pixel width on Windows
        return 0

    def scrollBarMargin(self):
        if KritaSettings.hideScrollbars():
            return 0

        return 14 # Canvas crollbar pixel width/height on Windows 
    
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
    #endregion

    #region Widget / Docker
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
                self.widget = NtScrollAreaContainer(docker.widget())
            else:
                self.widget = docker.widget()

            self.layout().addWidget(self.widget) 
            self.adjustToView()        
            self.widgetDocker.hide()

            return True
            
        return False
    
    def returnDocker(self):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if self.widgetDocker and self.widget:
            if isinstance(self.widget, NtScrollAreaContainer):
                self.widgetDocker.setWidget(self.widget.scrollArea())
            else:
                self.widgetDocker.setWidget(self.widget)

            self.widgetDocker.show()
            self.widget = None
            self.widgetDocker = None
    #endregion

    #region View / Rendering
    def adjustToView(self, delta_x: int = 0, delta_y: int = 0):
        """
        Adjust the position and size of the Pad to that of the active View."""
        
        
        def fitToView(_view: QWidget, _sizeToFit: QSize):
            def height_scale(input):
                return input + self.btnHide.height() + 14 + self.scrollBarMargin() + self.rulerMargin()
            
            def height_offset(input):
                return input - self.btnHide.height() - 14 - self.scrollBarMargin() - self.rulerMargin()
            
            def width_offset(input):
                return input - 8 - self.scrollBarMargin()
            
            def width_scale(input):
                return input + 8 + self.scrollBarMargin()
            
            result = QSize(_sizeToFit)

            if _view.height() < height_scale(result.height()):
                result.setHeight(height_offset(_view.height()))
        
            if _view.width() < width_scale(result.width()):
                result.setWidth(width_offset(_view.width()))
                    
            return result
        
        
        view = self.activeView()

        if view:          
            widgetSize = self.widgetSize()
            widgetSizeHint = self.widgetSizeHint()
            widgetNewSize = QSize(widgetSize.width() + delta_x, widgetSize.height() + delta_y)
            
            if self.resizingEnabled == False:
                widgetNewSize = QSize(widgetSizeHint)
            
            
                              
            widgetNewSize = fitToView(view, Ext.QSize.fitToSource(widgetSizeHint, widgetNewSize))                   
            if widgetSize != widgetNewSize:
                self.widget.setFixedSize(widgetNewSize)
                
            padSizeHint = self.sizeHint()
            padSizeHint = Ext.QSize.fitToTarget(padSizeHint, view.size())

            if self.size() != padSizeHint:
                self.resize(padSizeHint)

            globalTargetPos = QPoint()
            if self.alignment == NtWidgetPadAlignment.Left:
                globalTargetPos = view.mapToGlobal(QPoint(self.rulerMargin() + self.offset_x_left, self.rulerMargin()))
            elif self.alignment == NtWidgetPadAlignment.Right:
                globalTargetPos = view.mapToGlobal(QPoint(view.width() - self.width() - self.scrollBarMargin() - self.offset_x_right, self.rulerMargin()))

            newPos = self.parentWidget().mapFromGlobal(globalTargetPos)
            if self.pos() != newPos:
                self.move(newPos)

    def updateCursor(self, pos: QPoint):
        
        if self.resizingEnabled == False:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return
             
        result = self.resizing
        corner = self.resizeCorner
         
        if not result:
            (result, corner) = self.mouseInGrip(pos)
            
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
            
    #endregion

    #region Functions

    def toggleResizing(self):
        if self.allowResizing:
            self.resizingToggleAction.trigger()


    def setViewAlignment(self, newAlignment: NtWidgetPadAlignment):
        """
        Set the Pad's alignment to the view to either 'left' or 'right'. 
        Returns False if the argument is an invalid value."""
        self.btnHide.setArrow(self.alignment)
        if self.alignment != newAlignment:
            self.alignment = newAlignment
            return True
    
        return False

    def toggleWidgetVisible(self, value=None):
        if self.widget:
            if not value:
                value = not self.widget.isVisible()   
            self.widget.setVisible(value)
        
        self.btnHide.setArrow(self.alignment)
        self.adjustToView()  
    #endregion
    
    #region Signals
    
    def allowResizingChanged(self):
        if self.allowResizing:
            self.resizingEnabled = self.resizingToggleAction.isChecked()
        self.adjustToView()
        self.updateCursor(self.cursor().pos())
        
    
    #endregion
  
    #region Events
    
    def mouseReleaseEvent(self, e: QMouseEvent):
        self.resizing = False
        self.updateCursor(e.pos())
    
    def mousePressEvent(self, e: QMouseEvent):
        if self.resizingEnabled == True:
            (result, corner) = self.mouseInGrip(e.pos())
            if result:
                self.resizeStart = QPoint(e.pos())
                self.resizeCorner = corner 
                self.resizing = True
            else:
                self.resizing = False
        self.updateCursor(e.pos())
    
    def mouseMoveEvent(self, e: QMouseEvent):
        if self.resizing and self.widget and self.resizeCorner != None:
            #adapt the widget size based on mouse movement
            delta: QPoint = e.pos() - self.resizeStart
            self.resizeStart = QPoint(e.pos())
            
            
            match self.resizeCorner:
                case Qt.Corner.BottomLeftCorner:
                    x = -delta.x()
                    y = delta.y()   
                case Qt.Corner.BottomRightCorner:
                    x = delta.x()
                    y = delta.y()      
            
            self.adjustToView(x, y)
            #qApp.instance().processEvents()
        self.updateCursor(e.pos())
            
    
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
        #p = QPainter(self)
        
        #if self.autoSize == False:
            #gripAreas = self.gripAreas()
            #p.setPen(Qt.GlobalColor.red)
            #for area in gripAreas:      
                #p.drawRect(gripAreas[area])
    #endregion
    

