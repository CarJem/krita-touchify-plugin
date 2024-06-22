from PyQt5 import QtWidgets, QtGui, QtSvg, QtCore
import os

import xml


from ..config import *
from zipfile import ZipFile

from krita import *

import xml.etree.ElementTree as ET


class QSvgIconEngine(QIconEngine):
    def __init__(self, svgData: bytes, autoColorMode: bool = True):
        super().__init__()
        self.svgData = ET.fromstring(svgData)
        self.autoColorMode = autoColorMode

        if self.autoColorMode:
            for child in self.svgData:
                if child.get("style"):
                    child.set("ignore-krita-style", "true")
                else:
                    child.set("ignore-krita-style", "false")

        self.currentColor = None
        self.renderer = QtSvg.QSvgRenderer()
 
    def updateData(self):
        if self.autoColorMode:
            color = qApp.palette().color(QPalette.ColorRole.ButtonText).name().split("#")[1]
            for child in self.svgData:
                if child.get("ignore-krita-style") == "false":
                    child.set("style", f"fill:#{color};fill-opacity:1")
        self.renderer.load(ET.tostring(self.svgData))


    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State):
        img = QPixmap(size)
        img.fill(Qt.GlobalColor.transparent)
        painter = QPainter(img)
        painter.begin(img)
        self.updateData()
        self.renderer.render(painter, QRectF(img.rect()))
        painter.end()
        return img

    def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
        self.updateData()
        self.renderer.render(painter, QRectF(rect))