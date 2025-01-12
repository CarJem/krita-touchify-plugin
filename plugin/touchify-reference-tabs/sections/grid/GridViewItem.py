# Photobash Images is a Krita plugin to get CC0 images based on a search,
# straight from the Krita Interface. Useful for textures and concept art!
# Copyright (C) 2020  Pedro Reis.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from krita import *
from PyQt5 import QtCore

DRAG_DELTA = 30
TRIANGLE_SIZE = 20

FAVOURITE_TRIANGLE = QPolygon([
    QPoint(0, 0),
    QPoint(0, TRIANGLE_SIZE),
    QPoint(TRIANGLE_SIZE, 0)
])

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .GridView import GridView

class GridViewItem(QWidget):
    SIGNAL_HOVER = QtCore.pyqtSignal(str)
    SIGNAL_LMB = QtCore.pyqtSignal(int)
    SIGNAL_LMB_DOUBLE = QtCore.pyqtSignal(int)
    SIGNAL_WUP = QtCore.pyqtSignal(int)
    SIGNAL_WDN = QtCore.pyqtSignal(int)
    SIGNAL_PREVIEW = QtCore.pyqtSignal(str)
    SIGNAL_FAVOURITE = QtCore.pyqtSignal(str)
    SIGNAL_UN_FAVOURITE = QtCore.pyqtSignal(str)
    SIGNAL_OPEN_NEW = QtCore.pyqtSignal(str)
    SIGNAL_REFERENCE = QtCore.pyqtSignal(str)
    SIGNAL_DRAG = QtCore.pyqtSignal(int)
    SIGNAL_IMAGE_CHANGED = QtCore.pyqtSignal(str)

    PREVIOUS_DRAG_X = None


    isFavourite = False
    dragExportScale = 100
    dragExportFitCanvas = False

    def __init__(self, parent: "GridView"):
        super(GridViewItem, self).__init__(parent)
        self.SIGNAL_IMAGE_CHANGED.connect(self.onImageChanged)

        self.GridView = parent
        self.GridIndex = -1

        self.display_image: QImage = None
        self.setImage("")

    def setExportOptions(self, fit_canvas: bool, scale: int):
        self.dragExportFitCanvas = fit_canvas
        self.dragExportScale = scale

    def setFavourite(self, newFavourite):
        self.isFavourite = newFavourite

    def setGridIndex(self, number):
        self.GridIndex = number

    def sizeHint(self):
        return QtCore.QSize(2000,2000)

    def enterEvent(self, event):
        self.SIGNAL_HOVER.emit(str(self.GridIndex))

    def leaveEvent(self, event):
        self.SIGNAL_HOVER.emit("None")

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton:
            self.SIGNAL_LMB.emit(self.GridIndex)
        if event.modifiers() == QtCore.Qt.AltModifier:
            self.PREVIOUS_DRAG_X = event.x()

    def mouseDoubleClickEvent(self, event):
        if event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton:
            self.SIGNAL_LMB_DOUBLE.emit(self.GridIndex)

    def mouseMoveEvent(self, event):
        if event.modifiers() != QtCore.Qt.ShiftModifier and event.modifiers() != QtCore.Qt.AltModifier:
            self.PREVIOUS_DRAG_X = None
            return 

        # alt modifier is reserved for scrolling through
        if self.PREVIOUS_DRAG_X and event.modifiers() == QtCore.Qt.AltModifier:
            if self.PREVIOUS_DRAG_X < event.x() - DRAG_DELTA:
                self.SIGNAL_WUP.emit(0)
                self.PREVIOUS_DRAG_X = event.x()
            elif self.PREVIOUS_DRAG_X > event.x() + DRAG_DELTA:
                self.SIGNAL_WDN.emit(0)
                self.PREVIOUS_DRAG_X = event.x()

            return 

        self.GridView.GridSection.NativeFn.dragToDocument(self, self.path, self.display_image, QPixmap(50, 50).fromImage(self.display_image), self.dragExportScale, self.dragExportFitCanvas)

    def wheelEvent(self,event):
        delta = event.angleDelta()
        if delta.y() > 20:
            self.SIGNAL_WUP.emit(0)
        elif delta.y() < -20:
            self.SIGNAL_WDN.emit(0)

    # menu opened with right click
    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        cmenuDisplay = cmenu.addAction("Preview in Docker")
        favouriteString = "Unpin" if self.isFavourite else "Pin to Beginning"
        cmenuFavourite = cmenu.addAction(favouriteString)
        cmenuOpenNew = cmenu.addAction("Open as New Document")
        cmenuReference = cmenu.addAction("Place as Reference")

        background = qApp.palette().color(QPalette.Window).name().split("#")[1]
        cmenuStyleSheet = f"""QMenu {{ background-color: #AA{background}; border: 1px solid #{background}; }}"""
        cmenu.setStyleSheet(cmenuStyleSheet)

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == cmenuDisplay:
            self.SIGNAL_PREVIEW.emit(self.path)
        if action == cmenuFavourite:
            if self.isFavourite:
                self.SIGNAL_UN_FAVOURITE.emit(self.path)
            else:
                self.SIGNAL_FAVOURITE.emit(self.path)
        if action == cmenuOpenNew:
            self.SIGNAL_OPEN_NEW.emit(self.path)
        if action == cmenuReference:
            self.SIGNAL_REFERENCE.emit(self.path)

    def setImage(self, path: str):
        self.path = path
        self.SIGNAL_IMAGE_CHANGED.emit(path)

    def onImageChanged(self, path: str):

        # checks if image is cached, and if it isn't, create it and cache it
        if not path in self.GridView.Cache_Paths:
            # need to remove from cache
            if len(self.GridView.Cache_Images) > self.GridView.max_items:
                removedPath = self.GridView.Cache_Paths.pop()
                self.GridView.Cache_Images.pop(removedPath)
            
            self.GridView.Cache_Paths = [path] + self.GridView.Cache_Paths
            self.GridView.Cache_Images[path] = QImage(path)
            #self.GridView.Cache_Images[path].scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)

        self.display_image = self.GridView.Cache_Images[path]


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))

        # Calculations
        total_width = event.rect().width()
        total_height = event.rect().height()
        image_width = self.display_image.width()
        image_height = self.display_image.height()

        try:
            var_w = total_width / image_width
            var_h = total_height / image_height
        except:
            var_w = 1
            var_h = 1

        size = 0

        if var_w <= var_h:
            size = var_w
        if var_w > var_h:
            size = var_h

        wt2 = total_width * 0.5
        ht2 = total_height * 0.5

        scaled_width = image_width * size
        scaled_height = image_height * size

        offset_x = wt2 - (scaled_width * 0.5)
        offset_y = ht2 - (scaled_height * 0.5)

        # Save State for Painter
        painter.save()
        painter.translate(offset_x, offset_y)
        painter.scale(size, size)
        painter.drawImage(0,0,self.display_image)
        # paint something if it is a favourite
        if hasattr(self, 'isFavourite'):
            if self.isFavourite: 
                # reset scale to draw favourite triangle
                painter.scale(1/size, 1/size)
                painter.drawPolygon(FAVOURITE_TRIANGLE)

        # Restore Space
        painter.restore()