"""Draggable grid name row widget.

This widget wraps a grid's collapse button and name button together,
allowing the entire row to be dragged to reorder grids. Supports
multi-grid selection and drag with visual feedback for drop position.
"""

from typing import TYPE_CHECKING
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from krita import Krita  # type: ignore

from touchify_quick_actions.utils.styles import COLLAPSE_BUTTON_STYLE

from ..utils.drag_utils import encode_grid_single, encode_grid_multi, is_grid_drag, decode_grid_single, decode_grid_multi
from jemlib.alib_widgets.widget.DropIndicatorOverlay import DropIndicatorOverlay

if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridInfo import GridInfo


class DraggableGridWidgetHeader(QWidget):
    """A draggable widget containing the collapse button and name button for a grid."""
    
    def __init__(self, grid_info: "GridInfo", parent_docker: "QuickActionsDocker"):
        super().__init__()
        self.grid_info = grid_info
        self.parent_docker = parent_docker
        
        # Drag state
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self._child_widgets = []
        
        # Drop indicator overlay (renders on top of everything)
        self._drop_overlay = DropIndicatorOverlay(self)
        
        # For compatibility
        self.drop_position = None
        
        # Setup
        self.setAcceptDrops(True)
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup the horizontal layout for collapse button and name button."""
        self._layout = QHBoxLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
    
    def resizeEvent(self, event):
        """Resize overlay when widget resizes."""
        super().resizeEvent(event)
        self._drop_overlay.setGeometry(0, 0, self.width(), self.height())
    
    def add_collapse_button(self, collapse_button: QPushButton):
        """Add the collapse button to this row."""
        self._layout.addWidget(collapse_button, alignment=Qt.AlignLeft)
        self._child_widgets.append(collapse_button)
        collapse_button.installEventFilter(self)
    
    def add_name_button(self, name_button: QPushButton):
        """Add the name button to this row."""
        self._layout.addWidget(name_button, 1)
        self._child_widgets.append(name_button)
        name_button.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Intercept mouse events from child widgets to enable row-level dragging."""
        try:
            if obj in self._child_widgets:
                # Let double-click events pass through directly to enable inline rename
                if event.type() == QEvent.MouseButtonDblClick:
                    return False  # Don't intercept, let the widget handle it
                
                if event.type() == QEvent.MouseButtonPress:
                    if event.button() == Qt.LeftButton:
                        self.drag_start_position = self.mapFromGlobal(obj.mapToGlobal(event.pos()))
                        self.is_dragging = False
                
                elif event.type() == QEvent.MouseMove:
                    if event.buttons() & Qt.LeftButton and self.drag_start_position:
                        current_pos = self.mapFromGlobal(obj.mapToGlobal(event.pos()))
                        distance = (current_pos - self.drag_start_position).manhattanLength()
                        
                        if distance >= QApplication.startDragDistance() and not self.is_dragging:
                            self.is_dragging = True
                            self._start_grid_drag()
                            return True
                
                elif event.type() == QEvent.MouseButtonRelease:
                    if event.button() == Qt.LeftButton:
                        self.is_dragging = False
                        self.drag_start_position = QPoint()
        except Exception:
            # Catch-all for any unexpected errors to prevent crashes
            pass  
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.is_dragging = False
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag operation."""
        if not (event.buttons() & Qt.LeftButton) or not self.drag_start_position:
            return
        
        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance >= QApplication.startDragDistance() and not self.is_dragging:
            self.is_dragging = True
            self._start_grid_drag()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_start_position = QPoint()
        super().mouseReleaseEvent(event)
    
    def _get_grids_to_drag(self):
        """Get the list of grids to drag (maintaining top-to-bottom order)."""
        selected = self.parent_docker.selected_grids
        
        if len(selected) >= 2 and self.grid_info in selected:
            return sorted(selected, key=lambda g: self.parent_docker.grids.index(g))
        
        return [self.grid_info]
    
    def _create_drag_pixmap(self, grids: list["GridInfo"]):
        """Create a visual representation of the grids being dragged."""
        from PyQt5.QtGui import QPixmap
        
        height = 24 * len(grids)
        width = 150
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(60, 60, 60))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(200, 200, 200))
        for i, grid in enumerate(grids):
            painter.drawText(5, 18 + i * 24, grid.name)
        painter.end()
        
        return pixmap
    
    def _start_grid_drag(self):
        """Start the grid drag operation."""
        grids = self._get_grids_to_drag()
        self.parent_docker.onGridRowDragStarted(grids)
        
        # Start drag tracking for autoscroll (uses same mechanism as brush buttons)
        if hasattr(self.parent_docker, 'start_drag_tracking'):
            self.parent_docker.dragStartTracking(self)
        
        drag = QDrag(self)
        mime_data = QMimeData()
        
        if len(grids) == 1:
            mime_data.setText(encode_grid_single(grids[0].name))
        else:
            mime_data.setText(encode_grid_multi([g.name for g in grids]))
        
        drag.setMimeData(mime_data)
        drag.setPixmap(self._create_drag_pixmap(grids))
        drag.setHotSpot(QPoint(10, 10))
        drag.exec_(Qt.MoveAction)
        
        self.parent_docker.onGridRowDragEnded()
    
    def dragEnterEvent(self, event):
        """Handle drag enter for receiving grid drops."""
        if event.mimeData().hasText() and is_grid_drag(event.mimeData().text()):
            if self.grid_info not in self.parent_docker.dragGetGridState():
                event.acceptProposedAction()
                self._update_drop_position(event.pos())
    
    def dragMoveEvent(self, event):
        """Handle drag move to update drop position indicator."""
        if event.mimeData().hasText() and is_grid_drag(event.mimeData().text()):
            if self.grid_info not in self.parent_docker.dragGetGridState():
                event.acceptProposedAction()
                self._update_drop_position(event.pos())
    
    def dragLeaveEvent(self, event):
        """Handle drag leave to clear drop indicator."""
        self.drop_position = None
        self._drop_overlay.set_position(None)
    
    def dropEvent(self, event):
        """Handle grid drop."""
        if not event.mimeData().hasText():
            return
        
        text = event.mimeData().text()
        if not is_grid_drag(text):
            return
        
        # Parse grid names from drag data
        if text.startswith("grids_drag_multi:"):
            grid_names = decode_grid_multi(text)
        else:
            name = decode_grid_single(text)
            grid_names = [name] if name else []
        
        if not grid_names:
            return
        
        # Find source grids by name
        source_grids = []
        for name in grid_names:
            for grid in self.parent_docker.grids:
                if grid.name == name:
                    source_grids.append(grid)
                    break
        
        if source_grids:
            insert_after = self.drop_position == 'bottom'
            self.parent_docker.move_grids_to_position(source_grids, self.grid_info, insert_after)
        
        self.drop_position = None
        self._drop_overlay.set_position(None)
        event.acceptProposedAction()
    
    def _update_drop_position(self, pos):
        """Update the drop position based on cursor location."""
        new_position = 'top' if pos.y() < self.height() / 2 else 'bottom'
        
        if new_position != self.drop_position:
            self.drop_position = new_position
            self._drop_overlay.set_position(new_position)
    
    def clear_drop_indicator(self):
        """Clear the drop indicator."""
        self.drop_position = None
        self._drop_overlay.set_position(None)

class DraggableGridWidgetHeaderToggle(QPushButton):
    def __init__(self, name_button_height: int, parent: QWidget=None):
        super().__init__(parent)
        self.setObjectName("collapse_button")
        self.setFixedSize(name_button_height, name_button_height)
        self.setStyleSheet(COLLAPSE_BUTTON_STYLE())
        self.icon_size = name_button_height - 8
        self.setIconSize(QSize(self.icon_size, self.icon_size))

    def updateIconSize(self):
        button_height = self.height()
        self.icon_size = button_height - 8
    
    def set_collapse_button_icon(self, is_collapsed):
        """Set the collapse button icon based on collapse state."""
        icon_name = "arrow-right" if is_collapsed else "arrow-down"
        icon = Krita.instance().icon(icon_name)
        
        if not icon or icon.isNull():
            return
        
        # Use high-res then scale down for quality
        pixmap = icon.pixmap(self.icon_size * 2, self.icon_size * 2)
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.icon_size, self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setIcon(QIcon(scaled))
        else:
            self.setIcon(icon)
        self.setIconSize(QSize(self.icon_size, self.icon_size))