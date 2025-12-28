"""UI widget for a single brush preset in a grid.

Each instance owns one Krita brush preset and is responsible for:
  - showing the preset's thumbnail
  - handling selection (single, multi, range)
  - starting drag operations so presets can be reordered or moved between grids
  - optionally displaying the brush name below the icon
"""

from copy import deepcopy
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from touchify_quick_actions.dialogs.SettingsDialog import SettingsDialog
from jemlib.alib_widgets.widget.DropIndicatorOverlay import DropIndicatorOverlay
from touchify_quick_actions.utils.styles import DRAGGABLE_GRID_BUTTON_BACKGROUND_COLOR, DRAGGABLE_GRID_BUTTON_ICON_STYLE, DRAGGABLE_GRID_BUTTON_LABEL_STYLE

from ..utils.config_utils import (
    get_brush_icon_size,
    get_display_brush_names,
    get_brush_name_font_size,
    get_list_mode
)
from ..utils.drag_utils import encode_single, encode_multi

if TYPE_CHECKING:
    from touchify_quick_actions.QuickActionsDocker import QuickActionsDocker
    from touchify_quick_actions.dataclasses.GridConfig import GridInfo
    from touchify_quick_actions.dataclasses.GridPresetItem import GridPresetItem

class DraggableGridButton(QWidget):
    """A draggable widget for brush presets with optional name display."""

    def __init__(self, preset: "GridPresetItem", grid_info: "GridInfo", parent_docker: "QuickActionsDocker"):
        super().__init__()

        self.preset = preset
        self.editDialog = None
        self.grid_info = grid_info
        self.parent_docker = parent_docker
        self.grid_index = -1
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.has_dragged = False
        self._context_menu = None
        self._name_label_height = 0

        self.__isSelected = False
        self.__isPressed = False
        self.__isHovered = False
        self.__isToggled = False

        self.__edgeHighlight = None

        """Setup the widget layout with icon button and name label."""
        #region
        layout = QVBoxLayout() if not get_list_mode(self.grid_info) else QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Icon button
        self.icon_button = self._create_icon_button()
        layout.addWidget(self.icon_button)
        
        # Name label (initially hidden, shown based on config)
        self.name_label = DraggableGridButtonLabel(self)
        self.name_label.setVisible(False)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        #endregion

        """Configure button size and icon."""
        #region
        icon_size = get_brush_icon_size(self.grid_info)
        show_names = get_display_brush_names(self.grid_info)
        
        self.setToolTip(self.getItemLabelText())
        
        # Set icon button size
        self.icon_button.setFixedSize(icon_size, icon_size)
        self.icon_button.setIconSize(self.icon_button.size())
        self.icon_button.setText(self.getItemLabelText()[:2])
        
        # Update name label
        self.updateNameLabel(show_names)
        #endregion
        
        self._drop_overlay = DropIndicatorOverlay(self)

        # Calculate total widget size
        self.updateWidgetSize()
        
        # Enable mouse tracking for hover detection
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)

        self.updateStyles()

    def _create_icon_button(self):
        manager = self.parent_docker.actions_manager
        if not manager:
            result = DraggableGridButtonIcon(self)
            return result
        
        preview: DraggableGridButtonIcon = manager.Create_Button(self, self.preset.trigger_data, DraggableGridButtonIcon)
        if not preview:
            result = DraggableGridButtonIcon(self)
            return result
        
        return preview

    #region Event Handlers

    def enterEvent(self, event: QEnterEvent):
        """Handle mouse entering the widget - apply hover darkening."""
        self.__isHovered = True
        self.updateStyles()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        """Handle mouse leaving the widget - remove hover darkening."""
        self.__isHovered = False
        self.updateStyles()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent, nested: bool = False):
        """Handle mouse press events on the widget itself."""
        self.__isPressed = True
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePressLeftEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.mousePressRightEvent(event)
        self.updateStyles()
        if not nested: super().mousePressEvent(event)

    def mousePressLeftEvent(self, event: QMouseEvent):
        """Handle left mouse press events from child widgets."""
        self.drag_start_position = event.pos()
        self.is_dragging = False
        self.has_dragged = False
        if isinstance(self.icon_button, TriggerButton): self.icon_button.onPressed()

    def mousePressRightEvent(self, event: QMouseEvent):
        """Handle mouse press events from child widgets."""
        mods = QApplication.keyboardModifiers()
        if mods & Qt.ShiftModifier:
            self.mousePressRightShiftEvent(event)
            return
        elif mods & Qt.ControlModifier:
            self.mousePressRightCtrlEvent(event)
            return
        else:
            self.showContextMenu(event.globalPos())
            return

    def mousePressRightShiftEvent(self, event: QMouseEvent):
        """Handle right-click with Shift modifier for range selection.
        
        Includes error handling to prevent crashes during rapid clicking.
        """
        try:
            self.parent_docker.select_button(self, range_selection=True)
            self.showContextMenu(event.globalPos())
        except (RuntimeError, AttributeError):
            # Widget or parent may be in invalid state during rapid operations
            pass

    def mousePressRightCtrlEvent(self, event: QMouseEvent):
        """Handle right-click with Ctrl modifier for toggle selection.
        
        Includes error handling to prevent crashes during rapid clicking.
        """
        try:
            self.parent_docker.select_button(self, add_to_selection=True)
            self.showContextMenu(event.globalPos())
        except (RuntimeError, AttributeError):
            # Widget or parent may be in invalid state during rapid operations
            pass
    
    def mouseMoveEvent(self, event: QMouseEvent, nested: bool = False):
        """Handle mouse press events on the widget itself."""
        if (event.buttons() & Qt.LeftButton):
            self.mouseMoveLeftEvent(event)
            
    def mouseMoveLeftEvent(self, event: QMouseEvent):
        """Handle mouse move events for dragging."""
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
            self.dragStart()

    def mouseReleaseEvent(self, event: QMouseEvent, nested: bool = False):
        """Handle mouse release events."""
        self.__isPressed = False
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            if hasattr(self.parent_docker, 'stop_drag_tracking'):
                self.parent_docker.dragStopTracking()
            
            # Handle click if not dragged
            if not self.has_dragged:
                self.mouseReleaseClickEvent()
            self.has_dragged = False
        self.updateStyles()
        if not nested: super().mouseReleaseEvent(event)

    def mouseReleaseClickEvent(self):
        """Handle button click - only if not dragging."""
        mods = QApplication.keyboardModifiers()
        
        if mods & Qt.ShiftModifier:
            self.parent_docker.select_button(self, range_selection=True)
        elif mods & Qt.ControlModifier:
            self.parent_docker.select_button(self, add_to_selection=True)
        else:
            self.parent_docker.select_button(self, add_to_selection=False)
            if isinstance(self.icon_button, TriggerButton): self.icon_button.onReleased()
            if isinstance(self.icon_button, TriggerButton): self.icon_button.onClicked()

    def eventFilter(self, obj: QObject, event: QEvent):
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
                        self.closeContextMenu()
                        return True
                except (RuntimeError, AttributeError):
                    # Widget became invalid during check
                    self._context_menu = None
        except Exception:
            # Catch-all for any unexpected errors to prevent crashes
            pass
        
        return super().eventFilter(obj, event)

    def resizeEvent(self, a0: QResizeEvent):
        """Resize overlay when widget resizes."""
        super().resizeEvent(a0)
        self._drop_overlay.setGeometry(0, 0, self.width(), self.height())


    #endregion

    #region Drag Functions

    def dragStart(self):
        """Start drag operation."""

        def _create_drag_mime_data():
            """Create mime data for drag operation."""

            def _get_selected_preset_names():
                """Get preset names from selected buttons in grid order."""
                layout = self.grid_info.ui.layout
                if not layout:
                    return [self.preset.itemUUID()]

                all_buttons = self._get_buttons_in_grid_order()
                selected = self.parent_docker.selected_buttons
                return [btn.preset.itemUUID() for btn in all_buttons if btn in selected]

            mime_data = QMimeData()
            selected = self.parent_docker.selected_buttons
            
            if len(selected) >= 2 and self in selected:
                mime_data.setText(encode_multi(_get_selected_preset_names()))
            else:
                mime_data.setText(encode_single(self.preset.itemUUID()))
            
            return mime_data


        self.parent_docker.dragStartTracking(self)
        
        drag = QDrag(self)
        drag.setMimeData(_create_drag_mime_data())
        drag.setPixmap(self.icon_button.icon().pixmap(32, 32))
        drag.setHotSpot(QPoint(16, 16))
        drag.exec_(Qt.MoveAction)
        
        self.parent_docker.dragStopTracking()

    #endregion

    #region Get / Set

    def getSelected(self):
        return self.__isSelected
        
    def setSelected(self, isSelected: bool):
        if self.__isSelected == isSelected: 
            self.updateSelectionView()
            return
        self.__isSelected = isSelected
        self.updateSelectionView()
        self.update()

    def getHighlightEdge(self):
        return self.__edgeHighlight

    def setHighlightEdge(self, edge):
        """Set the Highlight edge of the button's icon."""
        if self.__edgeHighlight == edge: return
        self.__edgeHighlight = edge
        self._drop_overlay.set_position(edge)
        self.update()

    def getNameLabelHeight(self):
        return self._name_label_height

    def setNameLabelHeight(self, height: int):
        """Set the name label height (called by grid for consistency across row)."""
        self._name_label_height = height
        if get_display_brush_names(self.grid_info) and height > 0:
            if get_list_mode(self.grid_info):
                self.name_label.setMinimumHeight(height)
            else:
                self.name_label.setFixedHeight(height)
            self.name_label.setVisible(True)
        else:
            self.name_label.setVisible(False)
        self.updateWidgetSize()

    def getItemLabelText(self):
        if not self.preset or not self.preset.trigger_data or not self.parent_docker.actions_manager:
            return self.preset.itemUUID()
        
        text = self.preset.trigger_data.getDisplayName()
        
        if text == "":
            return self.preset.itemUUID()

        return text

    #endregion

    #region Update Functions

    def updateSelectionView(self):
        should_show_selection = self.__isSelected and len(self.parent_docker.selected_buttons) >= 2
        self._drop_overlay.set_selected(should_show_selection)

    def updateNameLabel(self, show_names: bool):
        """Update the name label appearance and visibility."""
        if not show_names:
            self.name_label.setVisible(False)
            return
        
        self.name_label.setVisible(True)
        self.name_label.setText(self.getItemLabelText())
        self.name_label.updateStyles()
        if get_list_mode(self.grid_info):
            self.name_label.setFixedWidth(self.parent_docker.get_column_width(self.grid_info) - get_brush_icon_size(self.grid_info))
        else:
            self.name_label.setFixedWidth(get_brush_icon_size(self.grid_info))

    def updateWidgetSize(self):
        """Update the total widget size based on icon and name label."""
        icon_size = get_brush_icon_size(self.grid_info)
        show_names = get_display_brush_names(self.grid_info)
        list_mode = get_list_mode(self.grid_info)
        
        if show_names and self._name_label_height > 0:
            total_height = icon_size + self._name_label_height if not list_mode else icon_size
            total_width = icon_size if not list_mode else self.parent_docker.get_column_width(self.grid_info)
        else:
            total_height = icon_size
            total_width = icon_size if not list_mode else self.parent_docker.get_column_width(self.grid_info)
        
        self.setFixedSize(total_width, total_height)

    def updateHighlightEdge(self, cursor_pos: QCursor = None, is_hovered: bool = False):
        def is_cursor_on_left_half(cursor_pos):
            """Check if cursor is on the left half of this button."""
            if cursor_pos is None:
                cursor_pos = QCursor.pos()
            
            button_global_pos = self.mapToGlobal(QPoint(0, 0))
            local_x = cursor_pos.x() - button_global_pos.x()
            return local_x < self.width() / 2

        if not cursor_pos: cursor_pos = QCursor.pos()

        if is_hovered:
            is_left = is_cursor_on_left_half(cursor_pos)
            if is_left: self.setHighlightEdge('left')
            else: self.setHighlightEdge('right')
        else: self.setHighlightEdge(None)

    def updateStyles(self):
        bg_color = DRAGGABLE_GRID_BUTTON_BACKGROUND_COLOR(self.__isPressed, self.__isToggled, self.__isHovered)
        if hasattr(self, "name_label"): self.name_label.updateStyles(bg_color)
        if hasattr(self, "icon_button"): self.icon_button.updateStyles(bg_color)

    #endregion

    #region Common Functions

    def editButton(self):
        """Show settings dialog and apply changes."""
        self.editDialog = SettingsDialog.Setup(self.editDialog, self.parent_docker.api_window, "Settings", deepcopy(self.preset.trigger_data))
        if not self.editDialog.exec_():
            return
        
        button_index = self._find_button_index()
        presets = self.grid_info.brush_presets

        if 0 <= button_index < len(presets):
            presets[button_index].trigger_data = self.editDialog.editableConfig

            self.parent_docker.update_grid(self.grid_info)
            self.parent_docker.save_grids()

    def removeButton(self):
        """Remove this preset from the grid."""
        button_index = self._find_button_index()
        presets = self.grid_info.brush_presets
        
        if 0 <= button_index < len(presets):
            presets.pop(button_index)
        else:
            # Fallback: remove by name (may remove wrong duplicate)
            for i, p in enumerate(presets):
                if p.itemUUID() == self.preset.itemUUID():
                    presets.pop(i)
                    break
        
        self.parent_docker.update_grid(self.grid_info)
        self.parent_docker.save_grids()

    def showContextMenu(self, global_pos):
        """Show context menu based on selection state.
        
        Includes re-entrancy protection to prevent crashes when rapidly
        clicking with modifiers.
        """
        # Re-entrancy guard to prevent crashes from rapid clicking
        if getattr(self, '_menu_operation_in_progress', False):
            return
        
        try:
            self._menu_operation_in_progress = True
            
            context_menu = QMenu()

            if len(self.parent_docker.selected_buttons) >= 2:
                context_menu.addAction("Delete", self.parent_docker.delete_selected_items)
                context_menu.exec(global_pos)
            else:
                context_menu.addAction("Edit...", self.editButton)
                context_menu.addAction("Delete", self.removeButton)
                context_menu.exec(QCursor.pos())
        finally:
            self._menu_operation_in_progress = False

    def closeContextMenu(self):
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

    #endregion

    def onToggled(self, state: bool):
        self.__isToggled = state
        self.updateStyles()

    def _get_buttons_in_grid_order(self) -> list["DraggableGridButton"]:
        """Get all preset buttons in grid layout order."""
        layout = self.grid_info.ui.layout
        if not layout:
            return []
        
        return [
            layout.itemAt(i).widget()
            for i in range(layout.count())
            if layout.itemAt(i) and hasattr(layout.itemAt(i).widget(), 'preset')
        ]

    def _find_button_index(self):
        """Find this button's index in the grid layout."""
        layout = self.grid_info.ui.layout
        if not layout:
            return -1
        
        columns = self.parent_docker.get_dynamic_columns(self.grid_info)
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget() == self:
                row, col, _, _ = layout.getItemPosition(i)
                return row * columns + col
        return -1

class DraggableGridButtonLabel(QLabel):
    """A clickable label for displaying the brush preset name."""


    
    def __init__(self, parent_widget: "DraggableGridButton"):
        super().__init__()
        self.parent_widget = parent_widget
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)
        self.updateStyles()

    def updateStyles(self, bg_color: str = "transparent"):
        """Update the name label background to reflect hover state."""
        font_size = get_brush_name_font_size(self.parent_widget.grid_info)
        self.setStyleSheet(DRAGGABLE_GRID_BUTTON_LABEL_STYLE(font_size, bg_color))
        
    def mousePressEvent(self, event):
        self.parent_widget.mousePressEvent(event, True)
        
    def mouseMoveEvent(self, event):
        self.parent_widget.mouseMoveEvent(event, True)
        
    def mouseReleaseEvent(self, event):
        self.parent_widget.mouseReleaseEvent(event, True)

class DraggableGridButtonIcon(TriggerButton):

    def __init__(self, parent_widget: "DraggableGridButton | None" = None):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.current_edge_highlight = None
        self.triggerToggled.connect(self.onTriggerToggled)
        self.updateStyles()

    def onTriggerToggled(self, state: bool):
        if self.parent_widget: self.parent_widget.onToggled(state)
        
    def updateStyles(self, bg_color: str = "transparent"):
        self.setStyleSheet(DRAGGABLE_GRID_BUTTON_ICON_STYLE(bg_color))

    def setParent(self, obj):
        super().setParent(obj)
        self.parent_widget: "DraggableGridButton" = obj
        if self.parent_widget: 
            self.parent_widget.onToggled(self.toggled)
            self.parent_widget.updateStyles()

    def paintEvent(self, e: QPaintEvent):
        TriggerButton.paintEvent(self, e)
        
    def mousePressEvent(self, event):
        self.parent_widget.mousePressEvent(event, True)
        
    def mouseMoveEvent(self, event):
        self.parent_widget.mouseMoveEvent(event, True)
        
    def mouseReleaseEvent(self, event):
        self.parent_widget.mouseReleaseEvent(event, True)

