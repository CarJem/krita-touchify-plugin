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

from PyQt5.QtCore import Qt, QPointF, QRectF, QEvent, qDebug, qWarning, qCritical, QLineF
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter, QWheelEvent, QNativeGestureEvent, QTouchEvent, QTransform
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, \
                            QSpinBox, QToolButton, QPushButton, \
                            QColorDialog, QDialog, QSizePolicy, \
                            QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QScroller, \
                            qApp
from math import radians, sin, cos
from krita import *
 
# Zoom percent constants
MAX_ZOOM = 800
MIN_ZOOM = 10
ZOOM_STEP = 10

useAngleSelector = True

from ....krita.KisAngleSelector import KisAngleSelector as AngleSelector
from .ReferenceView import ReferenceView


from krita import ManagedColor


class ReferenceTabView(QWidget):

    def __init__(self, parent=None, flags=None):

        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # variables
        self.previous_scale_factor = 1.0
        self.zoomMode = False
        self.panMode = False
        self.rotateMode = False
        self.prevMousePos = False
        self.fitSetting = 1
        self.scalingMode = 1
        self.isSamplingColor = False

        # Layout init:
        # - image
        # Custom class for a hacky way to make sure input events are sent to the right place
        self.view = ReferenceView(self) #QGraphicsView()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # Disabling interactive mode prevents it from taking the drop events
        self.view.setInteractive(False)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.imageItem = QGraphicsPixmapItem()
        self.scene.addItem(self.imageItem)

        # For consistency with previous plugin behavior;
        # otherwise defaults to the base color.
        self.setBackgroundColor(qApp.palette().window().color())

        # - zoom level
        self.zoomSpinBox = QSpinBox()
        self.zoomSpinBox.setRange(MIN_ZOOM, MAX_ZOOM)
        self.zoomSpinBox.setSingleStep(ZOOM_STEP)
        self.zoomSpinBox.setSuffix("%")
        self.zoomSpinBox.setValue(99) # workaround to make sure 100% mode gets initialized properly
        self.zoomSpinBox.setToolTip("Zoom")
        self.zoomSpinBox.valueChanged.connect(self.reloadTransforms)

        # - page fit status
        self.fitButton = QToolButton()
        self.fitButton.setIcon(Krita.instance().icon("zoom-fit"))
        self.fitButton.setToolTip("Fit to page")
        self.fitButton.setCheckable(True)
        self.fitButton.setChecked(False)
        self.fitButton.toggled.connect(self.enactFit)

        # - hmirrored status
        self.hMirrorButton = QToolButton()
        self.hMirrorButton.setIcon(Krita.instance().icon("transform_icons_mirror_x"))
        self.hMirrorButton.setToolTip("Horizontal mirroring")
        self.hMirrorButton.setCheckable(True)
        self.hMirrorButton.setChecked(False)
        self.hMirrorButton.toggled.connect(self.reloadTransforms)

        # - vmirrored status
        self.vMirrorButton = QToolButton()
        self.vMirrorButton.setIcon(Krita.instance().icon("transform_icons_mirror_y"))
        self.vMirrorButton.setToolTip("Vertical mirroring")
        self.vMirrorButton.setCheckable(True)
        self.vMirrorButton.setChecked(False)
        self.vMirrorButton.toggled.connect(self.reloadTransforms)

        # - rotate status
        self.rotateSelector = AngleSelector()
        self.rotateSelector.setFlipOptionsMode("ContextMenu")
        self.rotateSelector.angleChanged.connect(self.reloadTransforms)


        self.centerButton = QPushButton()
        self.centerButton.setToolTip("Center view")
        self.centerButton.pressed.connect(self.action_centerView)
        self.view.horizontalScrollBar().rangeChanged.connect(self.action_toggleEnableCenterScroll)
        self.view.verticalScrollBar().rangeChanged.connect(self.action_toggleEnableCenterScroll)
        self.centerButton.setEnabled(False)

        # - color picker
        self.colorSamplerButton = QToolButton()
        self.colorSamplerButton.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        self.colorSamplerButton.setToolTip("Sample color from image")
        self.colorSamplerButton.setCheckable(True)
        self.colorSamplerButton.setChecked(False)
        self.colorSamplerButton.toggled.connect(self.action_toggleSampleColor)
        self.colorSamplerButton.setEnabled(False)

        # add to layout
        self.view.setCornerWidget(self.centerButton)
        layout.addWidget(self.view)
        self.view.setVisible(True)
        #
        toolLayout = QHBoxLayout()
        toolLayout.addWidget(self.zoomSpinBox, stretch=1)
        toolLayout.addWidget(self.fitButton)
        toolLayout.addWidget(self.hMirrorButton)
        toolLayout.addWidget(self.vMirrorButton)
        toolLayout.addWidget(self.rotateSelector, stretch=0)
        toolLayout.addWidget(self.colorSamplerButton)
        layout.addLayout(toolLayout)

        self.toggleButtonsEnabled(False)


    #region UI Functions
    
    def toggleButtonsEnabled(self, value):
        self.zoomSpinBox.setEnabled(value)
        self.fitButton.setEnabled(value)
        self.hMirrorButton.setEnabled(value)
        self.vMirrorButton.setEnabled(value)
        self.rotateSelector.setEnabled(value)
        self.colorSamplerButton.setEnabled(value)
    
    #endregion

    #region Transform Functions
    def zoomBy(self, deltaX, deltaY):
        currentZoom = self.zoomSpinBox.value()
        viewSize = self.view.maximumViewportSize()
        zoomX = 100 * deltaX / viewSize.width()
        zoomY = 100 * deltaY / viewSize.height()
        # Inverted: Mouse up/left zooms in, down/right zooms out
        self.setZoom(currentZoom - int(zoomX + zoomY))
        
    def viewPos(self):
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        return QPoint(hBar.value(), vBar.value())
        
    
    def panBy(self, deltaX, deltaY):
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        viewSize = self.view.maximumViewportSize()
        # Inverted: Mouse up/left moves scrollbar to the bottom/right
        hBar.setValue(hBar.value() - int(deltaX / viewSize.width() * hBar.maximum()))
        vBar.setValue(vBar.value() - int(deltaY / viewSize.height() * vBar.maximum()))
    
    def rotateBy(self, deltaX, deltaY):
        currentRotation = self.getRotation()
        # From 90 to 270, increasing = left instead of right
        if 90 <= currentRotation < 270:
            deltaX *= -1
        # From 180 to 360, increasing = up instead of down
        if 180 <= currentRotation < 360:
            deltaY *= -1
        self.setRotation(currentRotation + deltaX + deltaY)
        
    def updateScale(self, value):
        factor = value * 100
        self.zoomSpinBox.setValue(self.zoomSpinBox.value() + factor)
    
    def scaleToFit(self):
        """ get the available size and scale it to fit"""
        if not self.imageItem.pixmap():
            return

        max_x = self.view.maximumViewportSize().width()
        max_y = self.view.maximumViewportSize().height()
        # Need to account for the rotated dimensions
        rotatedRect = self.rotateRect()
        image_x = rotatedRect.width()
        image_y = rotatedRect.height()

        scale_x = max_x/image_x
        scale_y = max_y/image_y
        
        scale = 1
        if self.fitSetting == 1:
            scale = scale_x
            if scale_y < scale_x:
                scale = scale_y
        elif self.fitSetting == 2:
            scale = scale_x
        elif self.fitSetting == 3:
            scale = scale_y

        self.setZoom(int(scale*100))
    
    def enactFit(self):
        if self.fitButton.isChecked():
            if self.fitSetting == 4:
                self.setZoom(100)
            else:
                self.scaleToFit()
                # ...we flag that it is set to fit afterward
                self.setFit(True)
    
    def reloadPan(self, old_x: int, old_y: int, old_x_max: int, old_y_max: int):
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        
        x_diff = hBar.maximum() - old_x_max
        new_x = old_x + int(x_diff / 2)
        
        y_diff = vBar.maximum() - old_y_max
        new_y = old_y + int(y_diff / 2)
        
        hBar.setValue(new_x)
        vBar.setValue(new_y)  
    
    def reloadTransforms(self):
        
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        
        x_pos, y_pos, x_max, y_max = (hBar.value(), vBar.value(), hBar.maximum(), vBar.maximum())
        
        self.view.resetTransform()        
        scale = self.zoomSpinBox.value() / 100
        scaleX = scale if not self.hMirrorButton.isChecked() else -scale
        scaleY = scale if not self.vMirrorButton.isChecked() else -scale
        self.view.rotate(self.getRotation())
        self.view.scale(scaleX, scaleY)
        self.reloadPan(x_pos, y_pos, x_max, y_max)
        # we don't know if it's fitting the window, unless...
        self.setFit(False)
    
    #endregion

    #region Events
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self.panMode = True
            elif event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.zoomMode = True
            elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.rotateMode = True

        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Space:
            self.zoomMode = False
            self.panMode = False
            self.rotateMode = False
            self.prevMousePos = False

        return super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.zoomMode or self.panMode or self.rotateMode:
            if self.prevMousePos:
                deltaMousePosX = event.pos().x() - self.prevMousePos.x()
                deltaMousePosY = event.pos().y() - self.prevMousePos.y()
                if self.zoomMode:
                    self.zoomBy(deltaMousePosX, deltaMousePosY)
                elif self.panMode:
                    self.panBy(deltaMousePosX, deltaMousePosY)
                elif self.rotateMode:
                    self.rotateBy(deltaMousePosX, deltaMousePosY)
            self.prevMousePos = event.pos()
        elif self.isSamplingColor:
            self.selectColor(self.getColorAt(event.pos()))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if (self.isSamplingColor):
            self.colorSamplerButton.setChecked(False)
            self.selectColor(self.getColorAt(event.pos()))
            
    def resizeEvent(self, event):
        # if it should fit, resize it
        if not self.fitSetting == 4:
            self.enactFit()
    
    #endregion
    
    #region Color Functions
    
    def getColorAt(self, pos):
        return self.view.getColorAt(pos)

    def selectColor(self, color):
        color = ManagedColor.fromQColor(color)
        Krita.instance().activeWindow().activeView().setForeGroundColor(color)

    #endregion

    #region Calculation Functions
    
    def rotateRect(self):
        rads = radians(self.getRotation())
        c = cos(rads)
        s = sin(rads)
        def rotatePt(x, y):
            x2 = x * c - y * s
            y2 = x * s + y * c
            return QPointF(x2, y2)
        # Put 0,0 as the center
        halfWidth = self.imageItem.pixmap().width() / 2
        halfHeight = self.imageItem.pixmap().height() / 2
        pts = [rotatePt(-halfWidth, -halfHeight), rotatePt(halfWidth, -halfHeight),
               rotatePt(-halfWidth, halfHeight), rotatePt(halfWidth, halfHeight)]
        # Make a copy, not a reference...
        smallPt = QPointF(pts[0])
        largePt = QPointF(pts[0])
        for pt in pts[1:]:
            if pt.x() < smallPt.x():
                smallPt.setX(pt.x())
            if pt.y() < smallPt.y():
                smallPt.setY(pt.y())
            if pt.x() > largePt.x():
                largePt.setX(pt.x())
            if pt.y() > largePt.y():
                largePt.setY(pt.y())
        rotatedRect = QRectF(smallPt, largePt)
        # Put back to 0,0 as topleft
        # (unneeded as we are only using the width/height)
        #rotatedRect.translate(-smallPt)

        return rotatedRect

    #endregion
    
    #region Get / Set
    
    def getZoom(self):
        return self.zoomSpinBox.value()
    
    def setZoom(self, value):
        self.zoomSpinBox.setValue(value)

    def setFit(self, value):
        self.fitButton.setChecked(value)

    def setImage(self,image=QImage()):
        self.imageItem.setPixmap(QPixmap.fromImage(image))
        self.toggleButtonsEnabled(image != QImage())
        
    def setRotation(self, angle):
        self.rotateSelector.setAngle(angle)
        
    def getRotation(self):
        return self.rotateSelector.angle()

    def getBackgroundColor(self):
        return self.view.palette().base().color()

    def setBackgroundColor(self, color):
        palette = self.view.palette()
        palette.setColor(QPalette.ColorRole.Base, color)
        self.view.setPalette(palette)
    
    #endregion
    
    #region Action Functions

    def action_changeFitSetting(self, setting):
        self.fitSetting = setting
    
    def action_changeScaleSetting(self, setting):
        self.scalingMode = setting
        if setting == 1:
            self.imageItem.setTransformationMode(Qt.SmoothTransformation)
        elif setting == 2:
            self.imageItem.setTransformationMode(Qt.FastTransformation)

    def action_toggleEnableCenterScroll(self, min, max):
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        if hBar.maximum() == 0 and vBar.maximum() == 0:
            self.centerButton.setEnabled(False)
        else:
            self.centerButton.setEnabled(True)
    
    def action_toggleSampleColor(self, value):
        self.isSamplingColor = value
    
    def action_centerView(self):
        hBar = self.view.horizontalScrollBar()
        vBar = self.view.verticalScrollBar()
        hBar.setValue(int(hBar.maximum()/2))
        vBar.setValue(int(vBar.maximum()/2))
        
    def action_changeBackgroundColor(self):
        oldColor = self.getBackgroundColor()
        colorPicker = QColorDialog(oldColor)
        colorPicker.currentColorChanged.connect(self.setBackgroundColor)
        result = colorPicker.exec()
        if result == QDialog.DialogCode.Rejected:
            self.setBackgroundColor(oldColor)
    
    #endregion







