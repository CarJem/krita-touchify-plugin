from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor

# Visual constants for drop zone highlighting
_DROP_HIGHLIGHT_COLOR = QColor(70, 200, 255, 255)  # Bright cyan, fully opaque
_DROP_HIGHLIGHT_HEIGHT = 4  # Thicker highlight line for better visibility

if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridInfo import GridInfo

class DropIndicatorOverlay(QWidget):
    """Overlay widget that draws drop indicator on top of all other widgets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.position = None  # 'top' or 'bottom'
        self.selected = False
        self.hide()

    def set_selected(self, selected):
        if selected != self.selected:
            self.selected = selected
            self.check_visibility()
    
    def set_position(self, position):
        """Set the indicator position ('top', 'bottom', or None to hide)."""
        if position != self.position:
            self.position = position
            self.check_visibility()

    def check_visibility(self):
        if self.position or self.selected:
            self.show()
            self.raise_()
        else:
            self.hide()
        self.update()

    
    def paintEvent(self, event):
        """Paint the drop indicator overlay."""
        if not self.position and not self.selected:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(_DROP_HIGHLIGHT_COLOR)
        painter.setPen(Qt.NoPen)
        
        width = self.width()
        height = self.height()


        
        if self.position == 'top' or self.selected == True:
            rect = QRect(0, 0, width, _DROP_HIGHLIGHT_HEIGHT)
            painter.drawRect(rect)

        if self.position == 'left' or self.selected == True:
            rect = QRect(0, 0, _DROP_HIGHLIGHT_HEIGHT, height)
            painter.drawRect(rect)

        if self.position == 'right' or self.selected == True:
            rect = QRect(width - _DROP_HIGHLIGHT_HEIGHT, 0, _DROP_HIGHLIGHT_HEIGHT, height)
            painter.drawRect(rect)

        if self.position == 'bottom' or self.selected == True:
            rect = QRect(0, height - _DROP_HIGHLIGHT_HEIGHT, width, _DROP_HIGHLIGHT_HEIGHT)
            painter.drawRect(rect)
        
        painter.end()
