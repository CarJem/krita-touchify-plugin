from krita import QColor
from PyQt5.QtGui import QColor



class KisColor:
    def __init__(self, r = 0, g = 0, b = 0):
        self.r = r if  0 <= r <= 255 else 0
        self.g =  g if  0 <=  g <= 255 else 0
        self.b = b if  0 <= b <= 255 else 0


    def setOpacityFloat(self, value: float):
        return KisAlphaColor(self.r, self.g, self.b, int(value * 255))

    def fromQt(color: QColor):
        return KisColor(color.red(), color.green(), color.blue())

    def toQt(self):
        return QColor(self.r, self.g, self.b, 255)

    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b}"
    
class KisAlphaColor(KisColor):
    def __init__(self, r = 0, g = 0, b = 0, a = 0):
        super().__init__(r, g, b)
        self.a = a if 0 <= a <= 255 else 0

    def getOpacityFloat(self) -> float:
        return self.a / 255

    def noAlpha(self):
        return KisColor(self.r, self.g, self.b)

    def fromQt(color: QColor):
        return KisAlphaColor(color.red(), color.green(), color.blue(), color.alpha())

    def toQt(self):
        return QColor(self.r, self.g, self.b, self.a)

    def __str__(self) -> str:
        return f"{self.r},{self.g},{self.b},{self.a}"