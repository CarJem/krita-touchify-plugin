from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CheckerBoardPainter:
    def __init__(self, checkerSize: int):
        self.__checkerSize = checkerSize
        self.__lightColor = Qt.GlobalColor.lightGray
        self.__darkColor = Qt.GlobalColor.darkGray
        self.createChecker()

    def setCheckerColors(self, lightColor: QColor, darkColor: QColor):
        self.__lightColor = lightColor
        self.__darkColor = darkColor
        self.createChecker()

    def setCheckerSize(self, checkerSize: int):
        self.__checkerSize = checkerSize
        self.createChecker()
        
    def paint(self, painter: QPainter, rect: QRectF, patternOrigin: QPointF = None):
        if not patternOrigin: patternOrigin = QPointF()
        brush = QBrush(self.__checker)
        brush.setTransform(QTransform.fromTranslate(patternOrigin.x(), patternOrigin.y()))
        painter.fillRect(rect, brush)



    def createChecker(self):
        self.__checker = QPixmap(2 * self.__checkerSize, 2 * self.__checkerSize)
        p = QPainter(self.__checker)
        p.fillRect(0, 0, self.__checkerSize, self.__checkerSize, self.__lightColor)
        p.fillRect(self.__checkerSize, 0, self.__checkerSize, self.__checkerSize, self.__darkColor)
        p.fillRect(0, self.__checkerSize, self.__checkerSize, self.__checkerSize, self.__darkColor)
        p.fillRect(self.__checkerSize, self.__checkerSize, self.__checkerSize, self.__checkerSize, self.__lightColor)
        p.end()

    

    