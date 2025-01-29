
from krita import *
from PyQt5.QtCore import *

from touchify.__env__ import *


from typing import TYPE_CHECKING

from touchify.src.managers.shared.resources import ResourceManager
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow


class CanvasDualColorButton(QWidget):
    

    def __init__(self, parent: QWidget | None = None):
        super(CanvasDualColorButton, self).__init__(parent)

        size_policy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        size_policy.setWidthForHeight(True)
        self.setContentsMargins(0,0,0,0)
        self.updateIcons()
        self.__background_color: QColor = self.palette().color(self.backgroundRole())
        self.__foreground_color: QColor = self.palette().color(self.backgroundRole())

    def updateIcons(self):
        self.__resetIcon: QIcon = ResourceManager.kritaIcon("color-to-alpha")

    def metrics(self):
        PADDING = 4

        width = self.width() - PADDING
        half_width = int(width / 3)

        foreground_rect = QRect(0, 0, width - half_width, width - half_width)
        background_rect = QRect(half_width, half_width, width - half_width, width - half_width)

        widget_region = QRegion(QRect(0,0,width, width))
        widget_region -= QRegion(foreground_rect)
        widget_region -= QRegion(background_rect)

        if widget_region.rectCount() == 2:
            rect_list = widget_region.rects()
            swap_rect = rect_list[0]
            reset_rect = rect_list[1]
        else:
            swap_rect = None
            reset_rect = None

        foreground_rect.setTopLeft(foreground_rect.topLeft() + QPoint(PADDING, PADDING))
        background_rect.setTopLeft(background_rect.topLeft() + QPoint(PADDING, PADDING))
        if swap_rect: swap_rect.setTopLeft(swap_rect.topLeft() + QPoint(PADDING, PADDING))
        if reset_rect: reset_rect.setTopLeft(reset_rect.topLeft() + QPoint(PADDING, PADDING))

        return foreground_rect, background_rect, swap_rect, reset_rect
    
    def drawBorder(self, painter: QPainter, rect: QRect):
        x = rect.x()
        y = rect.y()

        width = rect.width()
        height = rect.height()

        border_width = 1

        light_color = QColor(64,64,64)
        dark_color = QColor(23,23,23)


        painter.setPen(QPen(light_color, border_width))
        painter.drawLine(x, y, x + width, y)

        painter.setPen(QPen(light_color, border_width))
        painter.drawLine(x, y + height, x, y)

        painter.setPen(QPen(dark_color, border_width))
        painter.drawLine(x + width, y, x + width, y + height)

        painter.setPen(QPen(dark_color, border_width))
        painter.drawLine(x + width, y + height, x, y + height)

    def drawArrows(self, painter: QPainter, rect: QRect):
        border_width = 1
        arrow_size = int(rect.width() / 4)

        x = rect.x() + arrow_size
        y = rect.y() + arrow_size
        
        width = rect.width() - arrow_size * 2
        height = rect.height() - arrow_size * 2

        color = self.palette().color(self.foregroundRole())

        painter.setPen(QPen(color, border_width))
        painter.drawLine(x, y, x + width, y)
        painter.drawLine(x, y, x + arrow_size, y + arrow_size)
        painter.drawLine(x, y, x + arrow_size, y - arrow_size)

        painter.setPen(QPen(color, border_width))
        painter.drawLine(x + width, y, x + width, y + height)
        painter.drawLine(x + width, y + height, x + width - arrow_size, y + height - arrow_size)
        painter.drawLine(x + width, y + height, x + width + arrow_size, y + height - arrow_size)

    def drawResetIcon(self, painter: QPainter, rect: QRect):

        x = rect.x()
        y = rect.y()

        width = rect.width() 

        pos = QPoint(x, y)
        half_size = int(width / 2)

        foreground_rect = QRect(pos.x(), pos.y(), width - half_size, width - half_size)
        background_rect = QRect(pos.x() + half_size, pos.y() + half_size, width - half_size, width - half_size)

        painter.fillRect(foreground_rect, QBrush(Qt.GlobalColor.black))
        painter.fillRect(background_rect, QBrush(Qt.GlobalColor.white))


    def paintEvent(self, event):
        foreground_rect, background_rect, swap_rect, reset_rect = self.metrics()

        painter = QPainter(self)

        foreground_brush = QBrush(self.__foreground_color, Qt.SolidPattern)
        painter.fillRect(foreground_rect, foreground_brush)
        self.drawBorder(painter, foreground_rect)

        background_brush = QBrush(self.__background_color, Qt.SolidPattern)
        painter.fillRect(background_rect, background_brush)
        self.drawBorder(painter, background_rect)

    
        if swap_rect: self.drawArrows(painter, swap_rect)
        if reset_rect: self.drawResetIcon(painter, reset_rect)

        painter.end()

    def mousePressEvent(self, a0):
        foreground_rect, background_rect, swap_rect, reset_rect = self.metrics()

        if a0.button() != Qt.MouseButton.LeftButton: return

        if foreground_rect.contains(a0.pos()):
            Krita.instance().action("chooseForegroundColor").trigger()
        elif background_rect.contains(a0.pos()):
            Krita.instance().action("chooseBackgroundColor").trigger()
        elif swap_rect and swap_rect.contains(a0.pos()):
            Krita.instance().action("toggle_fg_bg").trigger()
        elif reset_rect and reset_rect.contains(a0.pos()):
            Krita.instance().action("reset_fg_bg").trigger()

    def onFGColorChanged(self, managed_color: ManagedColor):
        self.__foreground_color = self.krita_to_qcolor(managed_color)
        self.update()

    def onBGColorChanged(self, managed_color: ManagedColor):
        self.__background_color = self.krita_to_qcolor(managed_color)
        self.update()

    def krita_to_qcolor(self, source: ManagedColor):
        if self.canvas == None or source == None: return QColor()
        return source.colorForCanvas(self.canvas)
    
    def onCanvasChanged(self, canvas: Canvas):
        self.canvas = canvas

    def setInstance(self, window: "TouchifyWindow"):
        self.appEngine = window

        self.appEngine.mgr_actions.canvasChanged.connect(self.onCanvasChanged)
        self.onCanvasChanged(self.appEngine.mgr_actions.getCurrentCanvas())

        self.appEngine.mgr_actions.foregroundColorChanged.connect(self.onFGColorChanged)
        self.onFGColorChanged(self.appEngine.mgr_actions.getCanvasColor(False))
        
        self.appEngine.mgr_actions.backgroundColorChanged.connect(self.onBGColorChanged)
        self.onBGColorChanged(self.appEngine.mgr_actions.getCanvasColor(True))