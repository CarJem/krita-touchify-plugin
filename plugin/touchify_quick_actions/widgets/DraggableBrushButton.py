"""UI widget for a single brush preset in a grid.

Each instance owns one Krita brush preset and is responsible for:
  - showing the preset's thumbnail
  - handling selection (single, multi, range)
  - starting drag operations so presets can be reordered or moved between grids
  - optionally displaying the brush name below the icon
"""

from typing import TYPE_CHECKING
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QPoint, QMimeData, QEvent
from PyQt5.QtGui import QDrag, QIcon, QPixmap, QPainter, QColor, QPen, QCursor

from ..utils.config_utils import (
    get_brush_icon_size,
    get_display_brush_names,
    get_brush_name_font_size,
)
from ..utils.drag_utils import encode_single, encode_multi
from .BaseContextMenu import BrushContextMenu, MultiSelectContextMenu

if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridConfig import GridInfo, GridPresetItem

# Visual constants
_HIGHLIGHT_COLOR = QColor(70, 170, 255, 255)
_HIGHLIGHT_BORDER_WIDTH = 12
_LEFT_EDGE_WIDTH = 17
_RIGHT_EDGE_WIDTH = 12

# Brush name label colors
_NAME_LABEL_BG_COLOR = "#383838"
_NAME_LABEL_TEXT_COLOR = "#d2d2d2"
_NAME_LABEL_BG_HOVER_COLOR = "#282828"  # Darker version for hover

# Hover darkening overlay
_HOVER_OVERLAY_COLOR = QColor(0, 0, 0, 70)  # Semi-transparent black overlay


class BrushIconButton(QPushButton):
    """The icon/thumbnail portion of the brush button."""
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.original_pixmap = None
        self.current_edge_highlight = None
        
    def mousePressEvent(self, event):
        self.parent_widget.handle_mouse_press(event)
        
    def mouseMoveEvent(self, event):
        self.parent_widget.handle_mouse_move(event)
        
    def mouseReleaseEvent(self, event):
        self.parent_widget.handle_mouse_release(event)

class ClickableNameLabel(QLabel):
    """A clickable label for displaying the brush preset name."""
    
    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        
    def mousePressEvent(self, event):
        self.parent_widget.handle_mouse_press(event)
        
    def mouseMoveEvent(self, event):
        self.parent_widget.handle_mouse_move(event)
        
    def mouseReleaseEvent(self, event):
        self.parent_widget.handle_mouse_release(event)

class DraggableBrushButton(QWidget):
    """A draggable widget for brush presets with optional name display."""

    def __init__(self, preset: "GridPresetItem", grid_info: "GridInfo", parent_docker: "QuickActionsDocker"):
        super().__init__()
        self.preset = preset
        self.grid_info = grid_info
        self.parent_docker = parent_docker
        self.grid_index = -1
        
        # Drag state
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.has_dragged = False
        
        # Context menu
        self._context_menu = None
        
        # Pixmap cache for edge highlighting
        self.original_pixmap = None
        self.current_edge_highlight = None
        
        # Hover state
        self._is_hovered = False
        
        # Name label height tracking (set by grid for consistency)
        self._name_label_height = 0

        self._setup_ui()
        self._setup_appearance()
        
        # Enable mouse tracking for hover detection
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)

    def _setup_ui(self):
        """Setup the widget layout with icon button and name label."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Icon button
        self.icon_button = BrushIconButton(self)
        self.icon_button.setStyleSheet("border: none; padding: 0px;")
        layout.addWidget(self.icon_button)
        
        # Name label (initially hidden, shown based on config)
        self.name_label = ClickableNameLabel(self)
        self.name_label.setVisible(False)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)

    def _setup_appearance(self, is_selected=False):
        """Configure button size and icon."""
        icon_size = get_brush_icon_size()
        show_names = get_display_brush_names()
        
        self.setToolTip(self.preset.name())
        
        # Set icon button size
        self.icon_button.setFixedSize(icon_size, icon_size)
        
        if self.preset.image():
            pixmap = QPixmap.fromImage(self.preset.image())
            self.original_pixmap = QPixmap(pixmap)
            if is_selected:
                pixmap = self._add_highlight_border(pixmap)
            self.icon_button.setIcon(QIcon(pixmap))
            self.icon_button.setIconSize(self.icon_button.size())
        else:
            self.icon_button.setText(self.preset.name()[:2])
        
        # Update name label
        self._update_name_label(show_names)
        
        # Calculate total widget size
        self._update_widget_size()

    def _update_name_label(self, show_names):
        """Update the name label appearance and visibility."""
        if not show_names:
            self.name_label.setVisible(False)
            return
        
        self.name_label.setVisible(True)
        self.name_label.setText(self.preset.name())
        
        font_size = get_brush_name_font_size()
        icon_size = get_brush_icon_size()
        
        self.name_label.setStyleSheet(f"""
            QLabel {{
                background-color: {_NAME_LABEL_BG_COLOR};
                color: {_NAME_LABEL_TEXT_COLOR};
                font-size: {font_size}px;
                padding: 2px 1px;
                border: none;
            }}
        """)
        self.name_label.setFixedWidth(icon_size)

    def set_name_label_height(self, height: int):
        """Set the name label height (called by grid for consistency across row)."""
        self._name_label_height = height
        if get_display_brush_names() and height > 0:
            self.name_label.setFixedHeight(height)
            self.name_label.setVisible(True)
        else:
            self.name_label.setVisible(False)
        self._update_widget_size()

    def resize_to_icon_size(self, icon_size, name_label_height):
        """Resize the button in-place to a new icon size without recreating it.
        
        Args:
            icon_size: The new icon size in pixels
            name_label_height: The height for the name label area (0 if hidden)
        """
        # Update icon button size
        self.icon_button.setFixedSize(icon_size, icon_size)
        
        # Update icon pixmap to match new size
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                icon_size, icon_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            # Preserve selection state
            if self._is_button_selected():
                scaled_pixmap = self._add_highlight_border(scaled_pixmap)
            # Preserve hover state
            if self._is_hovered:
                scaled_pixmap = self._apply_hover_darkening(scaled_pixmap)
            self.icon_button.setIcon(QIcon(scaled_pixmap))
            self.icon_button.setIconSize(self.icon_button.size())
        
        # Update name label if visible
        show_names = get_display_brush_names()
        if show_names and name_label_height > 0:
            font_size = get_brush_name_font_size()
            bg_color = _NAME_LABEL_BG_HOVER_COLOR if self._is_hovered else _NAME_LABEL_BG_COLOR
            self.name_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {_NAME_LABEL_TEXT_COLOR};
                    font-size: {font_size}px;
                    padding: 2px 1px;
                    border: none;
                }}
            """)
            self.name_label.setFixedWidth(icon_size)
            self.name_label.setFixedHeight(name_label_height)
            self.name_label.setVisible(True)
            self._name_label_height = name_label_height
        else:
            self.name_label.setVisible(False)
            self._name_label_height = 0
        
        # Update total widget size
        if show_names and name_label_height > 0:
            total_height = icon_size + name_label_height
        else:
            total_height = icon_size
        self.setFixedSize(icon_size, total_height)

    def _update_widget_size(self):
        """Update the total widget size based on icon and name label."""
        icon_size = get_brush_icon_size()
        show_names = get_display_brush_names()
        
        if show_names and self._name_label_height > 0:
            total_height = icon_size + self._name_label_height
        else:
            total_height = icon_size
        
        self.setFixedSize(icon_size, total_height)

    def get_required_name_lines(self) -> int:
        """Calculate how many lines this brush name needs.
        
        Returns:
            1 or 2 based on the text length relative to available width
        """
        if not get_display_brush_names():
            return 0
            
        icon_size = get_brush_icon_size()
        font_size = get_brush_name_font_size()
        
        # Approximate characters per line based on icon width and font size
        # Average character width is roughly 0.6 * font_size for sans-serif
        avg_char_width = font_size * 0.55
        chars_per_line = max(1, int((icon_size - 4) / avg_char_width))  # -4 for padding
        
        name_length = len(self.preset.name())
        
        if name_length <= chars_per_line:
            return 1
        else:
            return 2

    def refresh_appearance(self):
        """Refresh the button appearance after config changes."""
        is_selected = self._is_button_selected()
        self._setup_appearance(is_selected)

    def _add_highlight_border(self, pixmap):
        """Draw a highlight border on the pixmap."""
        result = QPixmap(pixmap)
        painter = QPainter(result)
        pen = QPen(_HIGHLIGHT_COLOR)
        pen.setWidth(_HIGHLIGHT_BORDER_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(result.rect().adjusted(1, 1, -2, -2))
        painter.end()
        return result

    def _get_base_pixmap(self):
        """Get the base pixmap, creating from preset if needed."""
        if self.original_pixmap:
            return QPixmap(self.original_pixmap)
        if self.preset.image():
            pixmap = QPixmap.fromImage(self.preset.image())
            self.original_pixmap = QPixmap(pixmap)
            return pixmap
        return None

    def _apply_hover_darkening(self, pixmap):
        """Apply a dark overlay to the pixmap for hover effect."""
        result = QPixmap(pixmap)
        painter = QPainter(result)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.fillRect(result.rect(), _HOVER_OVERLAY_COLOR)
        painter.end()
        return result

    def _update_icon_for_hover(self):
        """Update the icon button to reflect hover state."""
        pixmap = self._get_base_pixmap()
        if not pixmap:
            return
        
        is_selected = self._is_button_selected()
        
        # Apply hover darkening FIRST (to base pixmap only)
        if self._is_hovered:
            pixmap = self._apply_hover_darkening(pixmap)
        
        # Apply selection highlight ON TOP (so it's not darkened)
        if is_selected:
            pixmap = self._add_highlight_border(pixmap)
        
        # Apply edge highlight on top
        if self.current_edge_highlight:
            pixmap = self._apply_edge_to_pixmap(pixmap, self.current_edge_highlight)
        
        self.icon_button.setIcon(QIcon(pixmap))
        self.icon_button.setIconSize(self.icon_button.size())

    def _apply_edge_to_pixmap(self, pixmap, edge):
        """Apply edge highlight to a pixmap."""
        result = QPixmap(pixmap)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        pen = QPen(_HIGHLIGHT_COLOR)
        pen.setWidth(_LEFT_EDGE_WIDTH if edge == 'left' else _RIGHT_EDGE_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        rect = result.rect().adjusted(1, 1, -2, -2)
        x = rect.left() if edge == 'left' else rect.right()
        painter.drawLine(x, rect.top(), x, rect.bottom())
        painter.end()
        
        return result

    def _update_name_label_for_hover(self):
        """Update the name label background to reflect hover state."""
        if not get_display_brush_names() or not self.name_label.isVisible():
            return
        
        font_size = get_brush_name_font_size()
        bg_color = _NAME_LABEL_BG_HOVER_COLOR if self._is_hovered else _NAME_LABEL_BG_COLOR
        
        self.name_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {_NAME_LABEL_TEXT_COLOR};
                font-size: {font_size}px;
                padding: 2px 1px;
                border: none;
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse entering the widget - apply hover darkening."""
        self._is_hovered = True
        self._update_icon_for_hover()
        self._update_name_label_for_hover()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leaving the widget - remove hover darkening."""
        self._is_hovered = False
        self._update_icon_for_hover()
        self._update_name_label_for_hover()
        super().leaveEvent(event)

    def update_highlight(self, is_selected):
        """Update the button's highlight state (for current brush preset)."""
        pixmap = self._get_base_pixmap()
        if pixmap:
            # Apply hover darkening FIRST (to base pixmap only)
            if self._is_hovered:
                pixmap = self._apply_hover_darkening(pixmap)
            # Apply selection highlight ON TOP (so it's not darkened)
            if is_selected:
                pixmap = self._add_highlight_border(pixmap)
            self.icon_button.setIcon(QIcon(pixmap))
            self.icon_button.setIconSize(self.icon_button.size())
    
    def update_selection_highlight(self, is_selected):
        """Update the button's selection highlight state (for multi-selection)."""
        self.update_highlight(is_selected)

    def handle_mouse_press(self, event):
        """Handle mouse press events from child widgets."""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.is_dragging = False
            self.has_dragged = False
        elif event.button() == Qt.RightButton:
            mods = QApplication.keyboardModifiers()
            if mods & Qt.ShiftModifier:
                self._handle_right_click_with_shift(event)
                return
            elif mods & Qt.ControlModifier:
                self._handle_right_click_with_ctrl(event)
                return
            else:
                self._show_appropriate_context_menu(event.globalPos())
                return

    def handle_mouse_move(self, event):
        """Handle mouse move events for dragging."""
        if not (event.buttons() & Qt.LeftButton):
            return

        distance = (event.pos() - self.drag_start_position).manhattanLength()
        if distance < QApplication.startDragDistance():
            return

        # Multi-select: only allow dragging selected buttons
        if len(self.parent_docker.selected_buttons) >= 2:
            if self not in self.parent_docker.selected_buttons:
                return

        if not self.is_dragging:
            self.is_dragging = True
            self.has_dragged = True
            self._start_drag()

    def handle_mouse_release(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            if hasattr(self.parent_docker, 'stop_drag_tracking'):
                self.parent_docker.stop_drag_tracking()
            
            # Handle click if not dragged
            if not self.has_dragged:
                self._on_clicked()
            self.has_dragged = False

    def _on_clicked(self):
        """Handle button click - only if not dragging."""
        mods = QApplication.keyboardModifiers()
        
        if mods & Qt.ShiftModifier:
            self.parent_docker.select_button(self, range_selection=True)
        elif mods & Qt.ControlModifier:
            self.parent_docker.select_button(self, add_to_selection=True)
        else:
            self.parent_docker.select_button(self, add_to_selection=False)
            #self.parent_docker.select_brush_preset(self.preset, source_button=self)

    def mousePressEvent(self, event):
        """Handle mouse press events on the widget itself."""
        self.handle_mouse_press(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events on the widget itself."""
        self.handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events on the widget itself."""
        self.handle_mouse_release(event)
        super().mouseReleaseEvent(event)

    def _handle_right_click_with_shift(self, event):
        """Handle right-click with Shift modifier for range selection.
        
        Includes error handling to prevent crashes during rapid clicking.
        """
        try:
            self.parent_docker.select_button(self, range_selection=True)
            self._show_appropriate_context_menu(event.globalPos())
        except (RuntimeError, AttributeError):
            # Widget or parent may be in invalid state during rapid operations
            pass

    def _handle_right_click_with_ctrl(self, event):
        """Handle right-click with Ctrl modifier for toggle selection.
        
        Includes error handling to prevent crashes during rapid clicking.
        """
        try:
            self.parent_docker.select_button(self, add_to_selection=True)
            self._show_appropriate_context_menu(event.globalPos())
        except (RuntimeError, AttributeError):
            # Widget or parent may be in invalid state during rapid operations
            pass

    def _show_appropriate_context_menu(self, global_pos):
        """Show context menu based on selection state.
        
        Includes re-entrancy protection to prevent crashes when rapidly
        clicking with modifiers.
        """
        # Re-entrancy guard to prevent crashes from rapid clicking
        if getattr(self, '_menu_operation_in_progress', False):
            return
        
        try:
            self._menu_operation_in_progress = True
            self._close_context_menu()
            
            if len(self.parent_docker.selected_buttons) >= 2:
                self._context_menu = MultiSelectContextMenu(
                    self.parent_docker.remove_selected_brushes
                )
                self._context_menu.show_at(global_pos)
            else:
                self._context_menu = BrushContextMenu(self._remove_from_grid)
                self._context_menu.show_at_cursor()
            
            try:
                QApplication.instance().installEventFilter(self)
            except (RuntimeError, AttributeError):
                pass
        finally:
            self._menu_operation_in_progress = False

    def _close_context_menu(self):
        """Close any open context menu safely.
        
        Handles edge cases where widget may be deleted or in inconsistent state.
        """
        # Remove event filter first, before touching the menu
        try:
            app = QApplication.instance()
            if app:
                app.removeEventFilter(self)
        except (RuntimeError, AttributeError):
            pass
        
        # Now close and cleanup the menu
        if self._context_menu:
            try:
                menu = self._context_menu
                self._context_menu = None  # Clear reference first
                menu.hide()
                menu.close()
                menu.deleteLater()
            except (RuntimeError, AttributeError):
                # Widget already deleted or in invalid state
                self._context_menu = None

    def eventFilter(self, obj, event):
        """Close context menu when clicking outside.
        
        Includes safety checks to prevent crashes from rapid clicking.
        """
        try:
            # Safety check: ensure context menu exists and is valid
            menu = self._context_menu
            if menu is None:
                return super().eventFilter(obj, event)
            
            # Check if menu widget is still valid (not deleted)
            try:
                is_visible = menu.isVisible()
            except (RuntimeError, AttributeError):
                # Widget was deleted, clean up reference
                self._context_menu = None
                return super().eventFilter(obj, event)
            
            if is_visible and event.type() == QEvent.MouseButtonPress:
                try:
                    click_pos = QCursor.pos()
                    menu_geometry = menu.geometry()
                    if not menu_geometry.contains(click_pos):
                        self._close_context_menu()
                        return True
                except (RuntimeError, AttributeError):
                    # Widget became invalid during check
                    self._context_menu = None
        except Exception:
            # Catch-all for any unexpected errors to prevent crashes
            pass
        
        return super().eventFilter(obj, event)

    def _get_buttons_in_grid_order(self):
        """Get all preset buttons in grid layout order."""
        layout = self.grid_info.layout
        if not layout:
            return []
        
        return [
            layout.itemAt(i).widget()
            for i in range(layout.count())
            if layout.itemAt(i) and hasattr(layout.itemAt(i).widget(), 'preset')
        ]

    def _get_selected_preset_names(self):
        """Get preset names from selected buttons in grid order."""
        layout = self.grid_info.layout
        if not layout:
            return [self.preset.name()]

        all_buttons = self._get_buttons_in_grid_order()
        selected = self.parent_docker.selected_buttons
        return [btn.preset.name() for btn in all_buttons if btn in selected]

    def _create_drag_mime_data(self):
        """Create mime data for drag operation."""
        mime_data = QMimeData()
        selected = self.parent_docker.selected_buttons
        
        if len(selected) >= 2 and self in selected:
            mime_data.setText(encode_multi(self._get_selected_preset_names()))
        else:
            mime_data.setText(encode_single(self.preset.name()))
        
        return mime_data

    def _start_drag(self):
        """Start drag operation."""
        self.parent_docker.start_drag_tracking(self)
        
        drag = QDrag(self)
        drag.setMimeData(self._create_drag_mime_data())
        drag.setPixmap(self.icon_button.icon().pixmap(32, 32))
        drag.setHotSpot(QPoint(16, 16))
        drag.exec_(Qt.MoveAction)
        
        self.parent_docker.stop_drag_tracking()

    def _find_button_index(self):
        """Find this button's index in the grid layout."""
        layout = self.grid_info.layout
        if not layout:
            return -1
        
        columns = self.parent_docker.get_dynamic_columns()
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() == self:
                row, col, _, _ = layout.getItemPosition(i)
                return row * columns + col
        return -1

    def _remove_from_grid(self):
        """Remove this preset from the grid."""
        button_index = self._find_button_index()
        presets = self.grid_info.brush_presets
        
        if 0 <= button_index < len(presets):
            presets.pop(button_index)
        else:
            # Fallback: remove by name (may remove wrong duplicate)
            for i, p in enumerate(presets):
                if p.name() == self.preset.name():
                    presets.pop(i)
                    break
        
        self.parent_docker.update_grid(self.grid_info)
        self.parent_docker.save_grids_data()

    def is_cursor_on_left_half(self, cursor_pos=None):
        """Check if cursor is on the left half of this button."""
        if cursor_pos is None:
            cursor_pos = QCursor.pos()
        
        button_global_pos = self.mapToGlobal(QPoint(0, 0))
        local_x = cursor_pos.x() - button_global_pos.x()
        return local_x < self.width() / 2

    def _is_button_selected(self):
        """Check if this button is currently selected (brush or multi-select)."""
        docker = self.parent_docker
        
        is_current_brush = (
            docker.current_selected_preset is not None
            and self.preset.name() == docker.current_selected_preset.name()
            and (docker.current_selected_button is None or docker.current_selected_button == self)
        )
        is_multi_selected = self in docker.selected_buttons
        
        return is_current_brush or is_multi_selected

    def highlight_edge(self, edge):
        """Highlight the left or right edge of the button's icon."""
        if not self.original_pixmap or self.current_edge_highlight == edge:
            return
        
        pixmap = QPixmap(self.original_pixmap)
        
        # Apply hover darkening FIRST (to base pixmap only)
        if self._is_hovered:
            pixmap = self._apply_hover_darkening(pixmap)
        
        # Apply selection highlight ON TOP (so it's not darkened)
        if self._is_button_selected():
            pixmap = self._add_highlight_border(pixmap)
        
        # Apply edge highlight on top
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        pen = QPen(_HIGHLIGHT_COLOR)
        pen.setWidth(_LEFT_EDGE_WIDTH if edge == 'left' else _RIGHT_EDGE_WIDTH)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        rect = pixmap.rect().adjusted(1, 1, -2, -2)
        x = rect.left() if edge == 'left' else rect.right()
        painter.drawLine(x, rect.top(), x, rect.bottom())
        painter.end()
        
        self.icon_button.setIcon(QIcon(pixmap))
        self.icon_button.setIconSize(self.icon_button.size())
        self.current_edge_highlight = edge
    
    def clear_edge_highlight(self):
        """Clear edge highlight and restore original icon."""
        if self.current_edge_highlight is None or not self.original_pixmap:
            return
        
        pixmap = QPixmap(self.original_pixmap)
        
        # Apply hover darkening FIRST (to base pixmap only)
        if self._is_hovered:
            pixmap = self._apply_hover_darkening(pixmap)
        
        # Apply selection highlight ON TOP (so it's not darkened)
        if self._is_button_selected():
            pixmap = self._add_highlight_border(pixmap)
        
        self.icon_button.setIcon(QIcon(pixmap))
        self.icon_button.setIconSize(self.icon_button.size())
        self.current_edge_highlight = None
