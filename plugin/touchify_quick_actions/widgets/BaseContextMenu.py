"""Context menu widgets for brush buttons.

Provides popup menus for single and multi-selection brush actions.
"""

from PyQt5.QtWidgets import QFrame, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


# Shared stylesheet for context menu popups
_CONTEXT_MENU_STYLE = """
    QFrame {
        background-color: #2b2b2b;
        border: 1px solid #555;
        border-radius: 4px;
    }
    QPushButton {
        background-color: #3c3c3c;
        color: #e0e0e0;
        border: none;
        border-radius: 2px;
        padding: 8px 16px;
        text-align: left;
        min-width: 100px;
    }
    QPushButton:hover { background-color: #4a4a4a; }
    QPushButton:pressed { background-color: #2a2a2a; }
"""


class _BaseContextMenu(QFrame):
    """Base class for context menus with common setup."""
    
    def __init__(self, on_remove):
        super().__init__()
        self._on_remove = on_remove
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure the menu appearance and buttons."""
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setStyleSheet(_CONTEXT_MENU_STYLE)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._handle_remove)
        layout.addWidget(remove_btn)
        
        self.setLayout(layout)
        self.adjustSize()
    
    def _handle_remove(self):
        """Execute remove callback and close menu."""
        self._on_remove()
        self.close()
    
    def show_at(self, position):
        """Display the menu at the given position."""
        self.move(position)
        self.show()
        self.raise_()
    
    def show_at_cursor(self):
        """Display the menu at the current cursor position."""
        self.show_at(QCursor.pos())


class BrushContextMenu(_BaseContextMenu):
    """Context menu for single brush button actions."""
    pass


class MultiSelectContextMenu(_BaseContextMenu):
    """Context menu for multiple selected brush buttons."""
    pass
