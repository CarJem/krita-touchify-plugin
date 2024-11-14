# Reference Tabs
# Copyright (C) 2022 Freya Lupen <penguinflyer2222@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import Qt, QEvent, QLineF
from PyQt5.QtGui import QImage, QPainter, QWheelEvent, QTouchEvent
from PyQt5.QtWidgets import QSizePolicy, \
                            QGraphicsView
                            
from touchify.src.ext.KritaExtensions import *
from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ReferenceTabView import ReferenceTabView


class ReferenceView(QGraphicsView):
    
    def __init__(self, parent: "ReferenceTabView" = None):
        super().__init__(parent)
        self.totalScaleFactor = 1
        self.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def parent(self) -> "ReferenceTabView":
        return super().parent()
        
    def updateScale(self, factor: float):
        self.parent().updateScale(int(factor))
        
    def viewportOnPinch(self, event: QTouchEvent):
        touchPoints = event.touchPoints()
        
        if event.type() == QEvent.Type.TouchCancel or event.type() == QEvent.Type.TouchEnd:
            self.pinching = False
        
        if len(touchPoints) == 2:
            pinchPos1 = touchPoints[0]
            pinchPos2 = touchPoints[1]
            
            oldLine = QLineF(pinchPos1.lastPos(), pinchPos2.lastPos())
            newLine = QLineF(pinchPos1.pos(), pinchPos2.pos())
            
            oldScale = oldLine.length()
            newScale = newLine.length()
            
            
            if oldScale > newScale:
                currentScaleFactor = -1
            elif oldScale < newScale:
                currentScaleFactor = 1
            else:
                currentScaleFactor = 0
            
            newValue = self.parent().getZoom() + (currentScaleFactor * 1)
            self.parent().setZoom(newValue)
        else:
            self.pinching = False
     
    def viewportEvent(self, event: QEvent):
        match event.type():
            case QEvent.Type.TouchBegin:
                self.viewportOnPinch(event)
            case QEvent.Type.TouchUpdate:
                self.viewportOnPinch(event)
            case QEvent.Type.TouchCancel:
                self.viewportOnPinch(event)
            case QEvent.Type.TouchEnd:
                self.viewportOnPinch(event)
                    
                    
        return super().viewportEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        result = (delta and delta // abs(delta))         
        newValue = self.parent().getZoom() + (result * 10)
        self.parent().setZoom(newValue)

    def keyReleaseEvent(self, event):
        self.parent().keyReleaseEvent(event)
        super().keyReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        self.parent().mouseMoveEvent(event)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.parent().mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def getColorAt(self, pos):
        paintDevice = QImage(self.size(), QImage.Format_ARGB32)
        painter = QPainter(paintDevice)
        self.render(painter)

        # End painter, otherwise:
        # "QPaintDevice: Cannot destroy paint device that is being painted"
        painter.end()

        return paintDevice.pixelColor(pos)