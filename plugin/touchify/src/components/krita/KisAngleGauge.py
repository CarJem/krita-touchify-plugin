import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPalette
from PyQt5.QtCore import Qt, QPointF, pyqtSignal

class KisAngleGauge(QWidget):
    angleChanged = pyqtSignal(float)

    class IncreasingDirection:
        CounterClockwise = 0
        Clockwise = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.snapAngle = 15.0
        self.resetAngle = 0.0
        self.increasingDirection = self.IncreasingDirection.CounterClockwise
        self.isPressed = False
        self.isMouseHover = False
        self.minimumSnapDistance = 40.0
        
        self.setFocusPolicy(Qt.WheelFocus)

    def getAngle(self):
        return self.angle

    def getSnapAngle(self):
        return self.snapAngle

    def getResetAngle(self):
        return self.resetAngle

    def getIncreasingDirection(self):
        return self.increasingDirection

    def setAngle(self, newAngle):
        if math.isclose(newAngle, self.angle):
            return

        self.angle = newAngle
        self.update()
        self.angleChanged.emit(newAngle)

    def setSnapAngle(self, newSnapAngle):
        self.snapAngle = newSnapAngle

    def setResetAngle(self, newResetAngle):
        self.resetAngle = newResetAngle

    def setIncreasingDirection(self, newIncreasingDirection):
        self.increasingDirection = newIncreasingDirection
        self.update()

    def reset(self):
        self.setAngle(self.getResetAngle())

    def paintEvent(self, e):
        painter = QPainter(self)
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        minSide = min(center.x(), center.y())
        radius = minSide * 0.9
        lineMarkerRadius = minSide * 0.1
        angleInRadians = self.angle * math.pi / 180.0
        d = QPointF(
            center.x() + math.cos(angleInRadians) * radius,
            center.y() - math.sin(angleInRadians) * radius if self.increasingDirection == self.IncreasingDirection.CounterClockwise
            else center.y() + math.sin(angleInRadians) * radius
        )

        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.palette().color(QPalette.Window).lightness() < 128:
            circleColor = self.palette().color(QPalette.Light)
            axesColor = QColor(self.palette().color(QPalette.Light))
            axesColor.setAlpha(200)
            if self.isEnabled():
                backgroundColor = self.palette().color(QPalette.Dark)
                angleLineColor = QColor(255, 255, 255, 128)
                angleLineMarkerColor = QColor(255, 255, 255, 200)
            else:
                backgroundColor = self.palette().color(QPalette.Window)
                angleLineColor = self.palette().color(QPalette.Light)
                angleLineMarkerColor = self.palette().color(QPalette.Light)
        else:
            circleColor = self.palette().color(QPalette.Dark)
            axesColor = QColor(self.palette().color(QPalette.Dark))
            axesColor.setAlpha(200)
            if self.isEnabled():
                backgroundColor = self.palette().color(QPalette.Light)
                angleLineColor = QColor(0, 0, 0, 128)
                angleLineMarkerColor = QColor(0, 0, 0, 200)
            else:
                backgroundColor = self.palette().color(QPalette.Window)
                angleLineColor = self.palette().color(QPalette.Dark)
                angleLineMarkerColor = self.palette().color(QPalette.Dark)

        # Background
        painter.setPen(Qt.transparent)
        painter.setBrush(backgroundColor)
        painter.drawEllipse(center, radius, radius)

        # Axes lines
        painter.setPen(QPen(axesColor, 1.0, Qt.DotLine))
        painter.drawLine(int(center.x()), int(center.y() - radius + 1.0), int(center.x()), int(center.y() + radius - 1.0))
        painter.drawLine(int(center.x() - radius + 1.0), int(center.y()), int(center.x() + radius - 1.0), int(center.y()))

        # Outer circle
        if self.hasFocus():
            painter.setPen(QPen(self.palette().color(QPalette.Highlight), 2.0))
        else:
            if self.isMouseHover and self.isEnabled():
                painter.setPen(QPen(self.palette().color(QPalette.Highlight), 1.0))
            else:
                painter.setPen(QPen(circleColor, 1.0))
        painter.setBrush(Qt.transparent)
        painter.drawEllipse(center, radius, radius)

        # Angle line
        painter.setPen(QPen(angleLineColor, 1.0))
        painter.drawLine(center.toPoint(), d.toPoint())

        # Inner line marker
        painter.setPen(Qt.transparent)
        painter.setBrush(angleLineMarkerColor)
        painter.drawEllipse(center, lineMarkerRadius, lineMarkerRadius)

        # Outer line marker
        painter.setBrush(angleLineMarkerColor)
        painter.drawEllipse(d, lineMarkerRadius, lineMarkerRadius)

        e.accept()

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            e.ignore()
            return

        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        radius = min(center.x(), center.y())
        radiusSquared = radius * radius
        delta = QPointF(e.x() - center.x(), e.y() - center.y())
        distanceSquared = delta.x() * delta.x() + delta.y() * delta.y()

        if distanceSquared > radiusSquared:
            e.ignore()
            return

        angle = math.atan2(
            -delta.y() if self.increasingDirection == self.IncreasingDirection.CounterClockwise else delta.y(),
            delta.x()
        )
    
        if e.modifiers() & Qt.ControlModifier:
            sa = self.snapAngle * math.pi / 180.0
            angle = round(angle / sa) * sa

        self.setAngle(angle * 180.0 / math.pi)

        self.isPressed = True
    
        e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.isPressed:
            self.isPressed = False
            e.accept()
            return
        e.ignore()

    def mouseMoveEvent(self, e):
        if not (e.buttons() & Qt.LeftButton) or not self.isPressed:
            e.ignore()
            return

        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        radius = min(center.x(), center.y())
        radiusSquared = radius * radius
        delta = QPointF(e.x() - center.x(), e.y() - center.y())
        distanceSquared = delta.x() * delta.x() + delta.y() * delta.y()
        angle = math.atan2(
            -delta.y() if self.increasingDirection == self.IncreasingDirection.CounterClockwise else delta.y(),
            delta.x()
        ) * 180.0 / math.pi

        snapDistance = max(self.minimumSnapDistance * self.minimumSnapDistance, radiusSquared * 4.0)
        controlPressed = e.modifiers() & Qt.ControlModifier
        shiftPressed = e.modifiers() & Qt.ShiftModifier

        if controlPressed and shiftPressed:
            angle = round(angle)
        elif not shiftPressed and (controlPressed or distanceSquared < snapDistance):
            angle = round(angle / self.snapAngle) * self.snapAngle

        self.setAngle(angle)
    
        e.accept()

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.reset()
            e.accept()
        else:
            e.ignore()

    def wheelEvent(self, e):
        if e.angleDelta().y() > 0:
            if e.modifiers() & Qt.ControlModifier:
                self.setAngle(math.floor((self.angle + self.snapAngle) / self.snapAngle) * self.snapAngle)
            else:
                self.setAngle(self.angle + 1.0)
        elif e.angleDelta().y() < 0:
            if e.modifiers() & Qt.ControlModifier:
                self.setAngle(math.ceil((self.angle - self.snapAngle) / self.snapAngle) * self.snapAngle)
            else:
                self.setAngle(self.angle - 1.0)
        e.accept()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Up, Qt.Key_Right):
            if e.modifiers() & Qt.ControlModifier:
                self.setAngle(math.floor((self.angle + self.snapAngle) / self.snapAngle) * self.snapAngle)
            else:
                self.setAngle(self.angle + 1.0)
            e.accept()
        elif e.key() in (Qt.Key_Down, Qt.Key_Left):
            if e.modifiers() & Qt.ControlModifier:
                self.setAngle(math.ceil((self.angle - self.snapAngle) / self.snapAngle) * self.snapAngle)
            else:
                self.setAngle(self.angle - 1.0)
            e.accept()
        else:
            e.ignore()

    def enterEvent(self, e):
        self.isMouseHover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.isMouseHover = False
        self.update()
        super().leaveEvent(e)

