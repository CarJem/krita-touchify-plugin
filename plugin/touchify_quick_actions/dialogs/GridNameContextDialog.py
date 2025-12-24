"""Context dialog for grid name right-click menu.

Provides rename and delete options for grids, appearing as a popup
near the cursor position.
"""

from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent




if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridConfig import GridInfo

class GridNameContextDialog(QDialog):
    """Dialog that appears on right-click of grid name with delete and rename options"""
    
    def __init__(self, parent: "QuickActionsDocker", grid_info: "GridInfo", rename_callback, delete_callback):
        super().__init__(parent)
        self.grid_info = grid_info
        self.rename_callback = rename_callback
        self.delete_callback = delete_callback
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.WindowStaysOnTopHint)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #555;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555;
                padding: 4px 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #777;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        
        # Rename button
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_grid)
        layout.addWidget(rename_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_grid)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
        self.adjustSize()
        
    def rename_grid(self):
        """Rename the grid and close dialog"""
        # Pass None if grid_info is None (indicates multiple grids selected)
        self.rename_callback(self.grid_info if self.grid_info else None)
        self.accept()
    
    def delete_grid(self):
        """Delete the grid and close dialog"""
        # Pass None if grid_info is None (indicates multiple grids selected)
        self.delete_callback(self.grid_info if self.grid_info else None)
        self.accept()
    
    def _is_click_outside_dialog(self, event):
        """Check if click is outside the dialog"""
        if not isinstance(event, QMouseEvent):
            return False
        return not self.rect().contains(event.pos())

    def event(self, event):
        """Handle events to close dialog when clicking outside"""
        if event.type() == QEvent.MouseButtonPress:
            if self._is_click_outside_dialog(event):
                self.reject()
                return True
        return super().event(event)
