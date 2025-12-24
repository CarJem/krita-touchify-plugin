"""Krita 'Preset Groups' docker.

Entry point for the docker widget that manages brush preset grids.
The docker inherits from multiple mixins to organize functionality:

- BrushManagerMixin: Brush size control and preset selection
- GridManagerMixin: Grid CRUD and reordering operations  
- SelectionManagerMixin: Button and grid selection handling
- ThumbnailManagerMixin: Thumbnail caching and change detection
- ShortcutHandlerMixin: Keyboard shortcut handling
- DragManagerMixin: Drag & drop and auto-scroll
- IconButtonFactoryMixin: Icon button creation
- GridUpdateMixin: Grid layout updates
- NameButtonEventsMixin: Grid name button events
"""
import re
import os
from typing import TYPE_CHECKING
import uuid
from jemlib.api_touchify.env import TouchifyEnv
from krita import DockWidgetFactory, DockWidgetFactoryBase  # type: ignore
from krita import Krita  # type: ignore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify_quick_actions.dataclasses.GridInfo import GridInfo
from touchify_quick_actions.dataclasses.GridPresetItem import GridPresetItem
from touchify_quick_actions.dialogs.GridNameContextDialog import GridNameContextDialog
from touchify_quick_actions.dialogs.SettingsDialog import SettingsDialog


from .widgets.DraggableGridContainer import DraggableGridContainer
from .widgets.ClickableGridWidget import ClickableGridWidget
from .widgets.DraggableGridRow import DraggableGridRow
from .widgets.DraggableBrushButton import DraggableBrushButton

from .utils.styles import *
from .utils.data_manager import load_grids_data, save_grids_data
from .utils.config_utils import (
    get_common_config,
    get_spacing_between_grids,
    get_brush_icon_size,
    reload_config,
    get_spacing_between_buttons,
    get_display_brush_names,
    get_brush_name_label_height
)




_UI_DIR = os.path.join(os.path.dirname(__file__), 'resources')

# Pattern for auto-generated group names
_GROUP_NAME_PATTERN = re.compile(r"^Group\s+(\d+)$")



# Timer intervals (ms)
_RESIZE_DEBOUNCE = 50
_SAVE_DEBOUNCE = 100  # Debounce for save operations

# Slider stylesheet
_SLIDER_STYLE = """
    QSlider { margin-top: -2px; margin-bottom: 2px; }
    QSlider::groove:horizontal {
        border: none; height: 3px; background: #555; border-radius: 3px;
    }
    QSlider::sub-page:horizontal, QSlider::add-page:horizontal {
        background: #636363; border: none; border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #ccc; width: 12px; border: none; border-radius: 2px; margin: -5px 0;
    }
"""

if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class QuickActionsDocker(QDockWidget):
    """Main docker for managing brush preset grids."""

    DOCKER_TITLE=f"{TouchifyEnv.Title.ADDON_DOCKERS_PREFIX} Quick Actions"

    def __init__(self):
        super().__init__()
        self.setWindowTitle(QuickActionsDocker.DOCKER_TITLE)
        
        """Initialize all instance state variables."""
        #region
        self.grids: list[GridInfo] = []
        self.active_grid: GridInfo = None
        self.main_widget = None
        self.main_grid_layout = None
        self.grid_counter = 0
        self.current_selected_preset = None
        self.current_selected_button = None
        self.brush_buttons = []
        self.selected_buttons = []
        self.last_selected_button = None
        self.selected_grids: list[GridInfo] = []
        self.last_selected_grid: GridInfo = None
        self._add_brush_qt_key = Qt.Key_W
        self.preset_thumbnail_cache = {}
        self._save_pending = False
        self._grids_pending_update = set()
        self.dlg = None
        #endregion

        """Initialize the docker UI layout."""
        #region
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        #endregion

        """Create top controls row with brush size slider and settings."""
        #region
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(4)
        top_row_layout.setContentsMargins(4, 2, 4, 2)

        top_row_layout.addSpacerItem(QSpacerItem(27, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        top_row_layout.addStretch()

        self.setting_btn = self.create_icon_button(
            "settings-button", self.show_settings_dialog
        )
        top_row_layout.addWidget(self.setting_btn, 0, Qt.AlignRight)

        top_row_widget = QWidget()
        top_row_widget.setLayout(top_row_layout)
        top_row_widget.setFixedHeight(self.setting_btn.sizeHint().height() + 6)
        main_layout.addWidget(top_row_widget)
        #endregion

        """Create the scrollable grids section."""
        #region
        self.main_widget = QWidget()
        self.main_widget.mousePressEvent = self.gridMousePressEvent
        self.main_grid_layout = QVBoxLayout()
        self.main_grid_layout.setAlignment(Qt.AlignTop)
        self.main_grid_layout.setSpacing(get_spacing_between_grids())
        self.main_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget.setLayout(self.main_grid_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.main_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.mousePressEvent = self.scroll_area_click_handler

        main_layout.addWidget(self.scroll_area, 1)
        #endregion

        """Create bottom button row with icon size slider and action buttons"""
        #region
        button_layout = QHBoxLayout()
        button_layout.setSpacing(1)

        # Icon size slider
        self.icon_size_slider = QSlider(Qt.Horizontal)
        self.icon_size_slider.setMinimum(30)
        self.icon_size_slider.setMaximum(170)
        self.icon_size_slider.setValue(get_brush_icon_size())
        self.icon_size_slider.setMinimumWidth(100)
        self.icon_size_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.icon_size_slider.setStyleSheet(_SLIDER_STYLE)
        #self.icon_size_slider.valueChanged.connect(self.on_brush_size_changed)
        button_layout.addWidget(self.icon_size_slider, 1)

        # Spacer
        button_layout.addSpacerItem(QSpacerItem(45, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Add Brush button
        self.add_brush_button = self.create_icon_button("addbrushicon", self.add_new_button)
        button_layout.addWidget(self.add_brush_button)
        button_layout.addSpacerItem(QSpacerItem(2, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Add Grid button
        add_grid_button = self.create_icon_button("folder", self.add_new_grid)
        button_layout.addWidget(add_grid_button)
        button_layout.addSpacerItem(QSpacerItem(2, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Delete button
        self.delete_button = self.create_icon_button("deletelayer", self.handle_delete_button_click)
        button_layout.addWidget(self.delete_button)
        button_layout.addSpacerItem(QSpacerItem(2, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Refresh Grid button
        refresh_grid_button = self.create_icon_button("refresh", self.load_grids)
        button_layout.addWidget(refresh_grid_button)
        button_layout.addSpacerItem(QSpacerItem(2, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        main_layout.addLayout(button_layout)
        #endregion

        """Initialize drag tracking state and timers"""
        #region
        self.dragging_button = None
        self.drag_highlight_timer = QTimer()
        self.drag_highlight_timer.timeout.connect(self.update_drag_highlights)
        self.drag_highlight_timer.setInterval(16)  # ~60fps
        
        # Auto-scroll tracking
        self.auto_scroll_timer = QTimer()
        self.auto_scroll_timer.timeout.connect(self.perform_auto_scroll)
        self.auto_scroll_timer.setInterval(16)  # ~60fps for smooth scrolling
        self.edge_scroll_distance = 0
        self.edge_scroll_direction = 0
        self.edge_touch_start_time = None
        self.base_scroll_speed = 6.0
        
        # Scroll position preservation after autoscroll
        self._autoscroll_used = False
        self._preserved_scroll_position = None
        
        # Scroll position monitoring timer for robust restoration
        self._scroll_monitor_timer = QTimer()
        self._scroll_monitor_timer.timeout.connect(self._monitor_scroll_position)
        self._scroll_monitor_timer.setInterval(16)  # Check frequently
        self._scroll_monitor_start_time = None
        self._scroll_monitor_duration = 600  # Monitor for 600ms after drop
        #endregion

        """Throw Everything Together"""
        #region
        central_widget.setLayout(main_layout)
        self.setWidget(central_widget)
        #endregion
        
        """Schedule initial layout update"""
        #region
        QTimer.singleShot(100, self._update_all_grids_on_resize)
        self.load_grids()
        #endregion

    def setup(self, instance: "TouchifyWindow"):
        self.__mgr_instance = instance
        self.api_window = instance.api_window

    def refresh_styles(self):

        def _refresh_icon_button_styles():
            """Refresh styles for icon buttons (settings, add, delete, etc.)."""
            icon_button_style = """
                QPushButton {
                    background-color: #474747;
                    border: none;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.3);
                }
            """
            for btn in self.findChildren(QPushButton):
                # Skip collapse buttons - they have their own style (#383838)
                if btn.objectName() == "collapse_button":
                    continue
                if btn.text() == "" and btn.icon() and not btn.icon().isNull():
                    btn.setStyleSheet(icon_button_style)

        def _refresh_grid_button_styles(grid: GridInfo):
            """Refresh styles for buttons within a grid."""
            layout = grid.layout
            if not layout:
                return
            for i in range(layout.count()):
                btn = layout.itemAt(i).widget()
                if btn:
                    btn.setStyleSheet(docker_btn_style())

        """Reapply button and grid styles."""
        for grid in self.grids:
            self.update_grid_style(grid)
            _refresh_grid_button_styles(grid)
        _refresh_icon_button_styles()
    
    def show_settings_dialog(self):
        """Show settings dialog and apply changes."""

        def _apply_grid_spacing():
            """Update grid spacing after settings change."""
            for grid_info in self.grids:
                container = grid_info.container
                if container and container.layout():
                    container.layout().setSpacing(1)
                layout = grid_info.layout
                if layout:
                    layout.setSpacing(get_spacing_between_buttons())
                self.update_grid(grid_info)


        self.dlg = SettingsDialog.Setup(self.dlg, self.api_window)
        if not self.dlg.exec_():
            return

        reload_config()
        _apply_grid_spacing()
        self.refresh_styles()

    def load_grids(self):
        """Load preset resources and grid data."""
        self._clear_grid_buttons(self.main_grid_layout)
        self._cleanup_grid_buttons(self.main_grid_layout)


        self.grids, self.grid_counter = load_grids_data()
        if not self.grids: self.add_new_grid(); return
        for grid_info in self.grids: self._add_grid_ui(grid_info)
        if self.grids: self.set_active_grid(self.grids[0])

    def save_grids_data(self):
        """Schedule grids data save with debouncing to avoid excessive file writes."""
        if self._save_pending:
            return
        self._save_pending = True
        QTimer.singleShot(_SAVE_DEBOUNCE, self.onSaveGridsRequested)

    #region Event Handlers

    def resizeEvent(self, event):
        """Handle docker resize with debouncing."""
        super().resizeEvent(event)
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self.onResizeCompleted)
        self._resize_timer.stop()
        self._resize_timer.start(_RESIZE_DEBOUNCE)

    def gridMousePressEvent(self, event):
        """Handle clicks on main widget to deselect"""
        from PyQt5.QtCore import Qt
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            widget_under_mouse = self.main_widget.childAt(event.pos())
            if not widget_under_mouse or not hasattr(widget_under_mouse, "preset"):
                self.clear_selection()
        QWidget.mousePressEvent(self.main_widget, event)

    #endregion

    #region Signal Recievers

    def onSaveGridsRequested(self):
        """Actually perform the save operation."""
        self._save_pending = False
        save_grids_data(self.grids)

    def onResizeCompleted(self):
        """Called after resize events have stopped."""
        self._update_all_grids_on_resize()

    def onGridRowDragStarted(self, grids):
        """Called when a grid drag operation starts."""
        self._init_grid_drag_state()
        self._grids_being_dragged = list(grids)
    
    def onGridRowDragEnded(self):
        """Called when a grid drag operation ends."""
        self._init_grid_drag_state()
        self._grids_being_dragged = []
        
        # Stop drag tracking for autoscroll
        if hasattr(self, 'stop_drag_tracking'):
            self.stop_drag_tracking()
        
        # Clear any remaining drop indicators
        for grid in self.grids:
            header_row = grid.header_row
            if header_row and hasattr(header_row, 'drop_position'):
                header_row.drop_position = None
                header_row.update()
    
    #endregion





    def _load_custom_icon(self, icon_name):
        """Load a custom PNG icon from the ui folder"""
        icon_path = os.path.join(_UI_DIR, f"{icon_name}.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                return pixmap
        return None

    def _load_and_set_icon(self, button, icon_name, button_size, icon_size):
        """Load icon from custom file or Krita and set it on the button"""
        try:
            # Try loading custom icon first
            custom_pixmap = self._load_custom_icon(icon_name)
            if custom_pixmap:
                scaled_pixmap = custom_pixmap.scaled(
                    icon_size,
                    icon_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                button.setIcon(QIcon(scaled_pixmap))
                button.setIconSize(QSize(icon_size, icon_size))
                return

            # Fall back to Krita's built-in icons
            app = Krita.instance()
            icon = app.icon(icon_name)
            if not icon or icon.isNull():
                return

            high_res_size = icon_size * 2
            pixmap = icon.pixmap(high_res_size, high_res_size)
            if pixmap.isNull():
                button.setIcon(icon)
                button.setIconSize(QSize(icon_size, icon_size))
                return

            scaled_pixmap = pixmap.scaled(
                icon_size,
                icon_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            high_res_icon = QIcon(scaled_pixmap)
            button.setIcon(high_res_icon)
            button.setIconSize(QSize(icon_size, icon_size))
        except Exception as e:
            print(f"Error loading icon '{icon_name}': {e}")
    






    def _create_collapse_button(self,  grid_info: GridInfo, name_button_height):
        """Create and configure the collapse button for a grid."""
        collapse_button = QPushButton()
        collapse_button.setObjectName("collapse_button")
        collapse_button.setFixedSize(name_button_height, name_button_height)
        collapse_button.setStyleSheet(COLLAPSE_BUTTON_STYLE)
        collapse_button.clicked.connect(lambda: self.toggle_grid_collapse(grid_info))
        
        icon_size = name_button_height - 8
        collapse_button.setIconSize(QSize(icon_size, icon_size))
        self._set_collapse_button_icon(
            collapse_button, 
            grid_info.is_collapsed,
            icon_size
        )
        
        return collapse_button

    def _create_name_button(self, grid_info: GridInfo):
        """Create and configure the name button for a grid."""
        name_button = QPushButton(grid_info.name)
        name_button.setStyleSheet(NAME_BUTTON_STYLE)
        name_button.drag_start_pos = None
        name_button.is_dragging_grid = False
        self._setup_name_button_events(name_button, grid_info)
        return name_button

    def _create_empty_grid_info(self, name) -> GridInfo:
        """Create a new empty grid info dictionary."""
        return GridInfo.createEmpty(name)

    def _create_inline_editor(self, parent, text):
        """Create a styled line editor for inline renaming."""
        editor = QLineEdit(parent)
        editor.setObjectName("grid_name_editor")
        editor.setText(text)
        editor.setStyleSheet(f"""
            QLineEdit {{
                background-color: #383838;
                color: {GRID_NAME_COLOR};
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-radius: 2px;
                padding: 2px 4px;
            }}
        """)
        return editor

    def create_icon_button(self, icon_name, callback):
        """Create an icon button with hover effects"""
        button = QPushButton()
        button.setText("")

        self._apply_button_style(button, icon_name)
        button_size = self._calculate_button_size()
        button.setFixedSize(QSize(button_size, button_size))

        icon_size = self._calculate_icon_size(icon_name, button_size)
        self._load_and_set_icon(button, icon_name, button_size, icon_size)

        button.clicked.connect(callback)
        return button

    def _create_name_button_mousePressEvent(self, name_button: QPushButton, grid_info: "GridInfo"):
        """Create mousePressEvent handler for name button.
        
        Note: Drag initiation is handled by the parent DraggableGridRow widget.
        """
        def handler(event):
            if event.button() == Qt.RightButton:
                self._handle_name_button_right_click(event, name_button, grid_info)
            elif event.button() == Qt.LeftButton:
                # Track click start for detecting clicks vs. drags
                name_button.click_pos = event.globalPos()
                # Let the event propagate to the parent DraggableGridRow for drag handling
            QPushButton.mousePressEvent(name_button, event)
        return handler

    def _create_name_button_mouseReleaseEvent(self, name_button: QPushButton, grid_info: "GridInfo"):
        """Create mouseReleaseEvent handler for name button"""
        def handler(event):
            if event.button() == Qt.LeftButton:
                # Only handle click if it wasn't a drag
                click_pos = getattr(name_button, 'click_pos', None)
                if click_pos:
                    drag_distance = (event.globalPos() - click_pos).manhattanLength()
                    # If this was a click (not a drag), handle selection
                    if drag_distance < QApplication.startDragDistance():
                        mods = QApplication.keyboardModifiers()
                        if mods == Qt.ShiftModifier:
                            self.select_grid_range(grid_info)
                        elif mods == Qt.ControlModifier:
                            self.toggle_grid_selection(grid_info)
                        else:
                            self.select_single_grid(grid_info)
                name_button.click_pos = None
            QPushButton.mouseReleaseEvent(name_button, event)
        return handler

    def _create_name_button_mouseDoubleClickEvent(self, name_button: QPushButton, grid_info: "GridInfo"):
        """Create mouseDoubleClickEvent handler for name button"""
        def handler(event):
            if event.button() == Qt.LeftButton:
                self.start_inline_grid_rename(grid_info)
            QPushButton.mouseDoubleClickEvent(name_button, event)
        return handler
    
    def _add_grid_ui(self, grid_info: GridInfo):
        """Add UI elements for a grid."""
        grid_container = DraggableGridContainer(grid_info, self)
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignTop)
        container_layout.setSpacing(1)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create draggable header row containing collapse button and name button
        header_row = DraggableGridRow(grid_info, self)
        grid_info.header_row = header_row
        grid_info.is_collapsed = grid_info.is_collapsed
        
        # Create name button first to get its height
        name_button = self._create_name_button(grid_info)
        name_button.adjustSize()
        name_button_height = name_button.sizeHint().height()
        
        # Create collapse button sized to match
        collapse_button = self._create_collapse_button(grid_info, name_button_height)
        grid_info.collapse_button = collapse_button
        
        # Add buttons to the draggable header row
        header_row.add_collapse_button(collapse_button)
        header_row.add_name_button(name_button)
        container_layout.addWidget(header_row)
        
        grid_info.container = grid_container
        grid_info.name_label = name_button
        grid_info.name_button = name_button
        # Keep header_layout reference for compatibility with inline rename
        grid_info.header_layout = header_row.layout()

        # Create grid widget for brush buttons
        grid_widget = ClickableGridWidget(grid_info, self)
        initial_height = get_brush_icon_size() + 4
        grid_widget.setFixedHeight(initial_height)
        grid_widget.setMinimumHeight(initial_height)

        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        grid_layout.setSpacing(get_spacing_between_buttons())
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_widget.setLayout(grid_layout)
        container_layout.addWidget(grid_widget)

        grid_container.setLayout(container_layout)
        grid_info.widget = grid_widget
        grid_info.layout = grid_layout
        self.main_grid_layout.addWidget(grid_container)
        self.update_grid(grid_info)

    def add_new_grid(self):
        """Add a new grid with auto-generated name."""
        next_num = self._get_next_group_number()
        self.grid_counter = max(self.grid_counter, next_num)
        
        grid_info = self._create_empty_grid_info(f"Group {next_num}")
        self.grids.append(grid_info)
        self._add_grid_ui(grid_info)
        
        if len(self.grids) == 1:
            self.set_active_grid(grid_info)
        self.save_grids_data()
    
    def add_new_button(self):
        self.active_grid.brush_presets.append(GridPresetItem(displayName=str(uuid.uuid4())))
        self.update_grid(self.active_grid)
        self.save_grids_data()

    def _add_preset_button(self, preset: GridPresetItem, grid_info: GridInfo, layout: QGridLayout, columns: int, index: int, name_label_height: int):
        """Add a single preset button to the grid"""
        row = index // columns
        col = index % columns
        brush_button = DraggableBrushButton(preset, grid_info, self)
        # Store the 1-based visual index for keyboard navigation
        brush_button.grid_index = index + 1
        
        # Set the name label height for consistency across the grid
        brush_button.set_name_label_height(name_label_height)
        
        self.brush_buttons.append(brush_button)
        layout.addWidget(brush_button, row, col)
        
        is_selected = self._is_preset_selected(preset)
        brush_button.update_highlight(is_selected)
        
        return brush_button




    def clear_selection(self):
        """Clear selection of both brush buttons and grids"""
        self.selected_buttons = []
        self.last_selected_button = None
        self.selected_grids = []
        self.last_selected_grid = None
        self.update_selection_highlights()
        self.update_grid_selection_highlights()
        # Clear the active grid highlight as well when clicking outside
        self._clear_active_grid_highlight()
    
    def _clear_active_grid_highlight(self):
        """Clear the active grid highlight state.
        
        If only one grid exists, keep it as the active grid instead of clearing.
        """
        # When only one grid exists, it should always remain active
        if len(self.grids) == 1:
            if not self.active_grid or self.active_grid != self.grids[0]:
                self.set_active_grid(self.grids[0])
            return
        
        if self.active_grid:
            # Reset the active grid's highlight to inactive style
            self.active_grid.is_active = False
            self.update_grid_style(self.active_grid)
        self.active_grid = None
    

    def _rename_grids_sequentially(self, grids_to_rename):
        """Rename multiple grids sequentially, one dialog at a time.
        
        Grids are sorted by their visual order (top to bottom) before renaming.
        """
        if not grids_to_rename:
            self.selected_grids = []
            self.last_selected_grid = None
            self.update_grid_selection_highlights()
            return
        
        # Sort grids by their visual order (top to bottom)
        sorted_grids = sorted(
            grids_to_rename,
            key=lambda g: self.grids.index(g) if g in self.grids else float('inf')
        )
        
        self._rename_next_grid(sorted_grids)
    
    def _rename_next_grid(self, grids_remaining):
        """Rename the next grid in the sequence."""
        if not grids_remaining:
            self.selected_grids = []
            self.last_selected_grid = None
            self.update_grid_selection_highlights()
            return
        
        grid_info = grids_remaining[0]
        new_name, ok = QInputDialog.getText(
            self, "Rename Grid", "Enter new grid name:", text=grid_info.name
        )
        
        if ok and new_name.strip():
            self._update_grid_name_ui(grid_info, new_name.strip())
            self.save_grids_data()
        
        remaining = grids_remaining[1:]
        if remaining:
            QTimer.singleShot(100, lambda: self._rename_next_grid(remaining))
        else:
            self.selected_grids = []
            self.last_selected_grid = None
            self.update_grid_selection_highlights()

    def rename_grid(self, grid_info: GridInfo=None):
        """Rename grid(s) - handles both single and multiple selection."""
        if grid_info is None and self.selected_grids:
            self._rename_grids_sequentially(self.selected_grids.copy())
            return
        
        if grid_info is None:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "Rename Group", "Enter new grid name:", text=grid_info.name
        )
        if ok and new_name.strip():
            self._update_grid_name_ui(grid_info, new_name.strip())
            self.save_grids_data()


    def _calculate_button_size(self):
        """Calculate button size based on reference button height"""
        temp_button = QPushButton("Test")
        temp_button.setStyleSheet(docker_btn_style())
        temp_button.adjustSize()
        button_height = temp_button.sizeHint().height()
        temp_button.deleteLater()
        return button_height + 7

    def _calculate_icon_size(self, icon_name, button_size):
        """Calculate icon size with special adjustments for specific icons"""
        base_icon_size = button_size - 4
        if icon_name == "addbrushicon":
            return max(8, base_icon_size - 8)  # Smaller icon for Add Brush button
        if icon_name == "folder":
            return max(8, base_icon_size - 2)
        if icon_name == "deletelayer":
            return max(8, base_icon_size - 5)
        return base_icon_size

    def _calculate_max_name_lines_for_grid(self, presets: list[GridPresetItem]):
        """Calculate the maximum number of lines needed for brush names in a grid.
        
        Args:
            presets: List of brush presets in the grid
            
        Returns:
            1 or 2 based on the longest name in the grid
        """
        if not get_display_brush_names() or not presets:
            return 0
        
        max_lines = 1
        icon_size = get_brush_icon_size()
        
        # Import here to get font size calculation
        from .utils.config_utils import get_brush_name_font_size
        font_size = get_brush_name_font_size()
        
        # Calculate chars per line
        avg_char_width = font_size * 0.55
        chars_per_line = max(1, int((icon_size - 4) / avg_char_width))
        
        for preset in presets:
            name_length = len(preset.name())
            if name_length > chars_per_line:
                max_lines = 2
                break  # No need to check further
        
        return max_lines

    def _calculate_grid_height(self, preset_count: int, columns: int, name_label_height: int=0):
        """Calculate required height for grid based on preset count and name labels"""
        required_rows = (preset_count + columns - 1) // columns if preset_count > 0 else 1
        icon_size = get_brush_icon_size()
        button_height = icon_size + name_label_height
        spacing = get_spacing_between_buttons()
        return required_rows * button_height + (required_rows - 1) * spacing + 4


    def remove_grid(self, grid_info: GridInfo=None):
        """Remove grid(s) - handles both single and multiple selection."""
        if grid_info is None and self.selected_grids:
            for grid in self.selected_grids.copy():
                self._remove_single_grid(grid)
            self.selected_grids = []
            self.last_selected_grid = None
            self.update_grid_selection_highlights()
            return
        
        if grid_info:
            self._remove_single_grid(grid_info)

    def _remove_single_grid(self, grid_info: GridInfo):
        """Remove a single grid and its UI elements."""
        if grid_info not in self.grids:
            return
        
        # Cleanup buttons
        layout = grid_info.layout
        if layout:
            self._cleanup_grid_buttons(layout)
        
        # Update selection state
        if grid_info in self.selected_grids:
            self.selected_grids.remove(grid_info)
        if self.last_selected_grid == grid_info:
            self.last_selected_grid = None
        
        # Remove container widget
        container = grid_info.container
        if container:
            self.main_grid_layout.removeWidget(container)
            container.setParent(None)
            container.deleteLater()
        
        self.grids.remove(grid_info)
        
        # Update active grid
        self.active_grid = self.grids[0] if self.grids else None
        if self.active_grid:
            self.set_active_grid(self.active_grid)
        
        self.save_grids_data()

    def remove_selected_brushes(self):
        """Remove all selected brushes from their grids"""
        if not self.selected_buttons:
            return
        
        grids_to_update = {}
        for button in self.selected_buttons:
            if hasattr(button, 'grid_info') and hasattr(button, 'preset'):
                grid_info = button.grid_info
                grid_name = grid_info.get("name", id(grid_info))
                if grid_name not in grids_to_update:
                    grids_to_update[grid_name] = {"grid_info": grid_info, "presets": []}
                grids_to_update[grid_name]["presets"].append(button.preset)
        
        for grid_data in grids_to_update.values():
            grid_info = grid_data["grid_info"]
            presets_to_remove = grid_data["presets"]
            for preset in presets_to_remove:
                for i, p in enumerate(grid_info.brush_presets):
                    if p.name() == preset.name():
                        grid_info["brush_presets"].pop(i)
                        grid_info.brush_presets
            self.widget()._mgr_grid_updater.update_grid(grid_info)
        
        self.clear_selection()
        self.save_grids_data()
    

    def _update_collapse_button_icon(self, grid_info: GridInfo):
        """Update the collapse button icon for a grid."""
        collapse_button = grid_info.collapse_button
        if collapse_button:
            button_height = collapse_button.height()
            icon_size = button_height - 8
            self._set_collapse_button_icon(collapse_button, grid_info.is_collapsed, icon_size)

    def update_grid(self, grid_info: GridInfo):
        """Update grid with current brush presets"""
        layout = grid_info.layout
        selected_indices = self._store_selected_indices(layout)
        self._clear_grid_buttons(layout)
        self._clear_last_selected_if_in_grid(grid_info)
        
        columns = self.get_dynamic_columns()
        presets = grid_info.brush_presets
        preset_count = len(presets)
        
        # Calculate consistent name label height for all buttons in this grid
        max_lines = self._calculate_max_name_lines_for_grid(presets)
        name_label_height = get_brush_name_label_height(max_lines) if max_lines > 0 else 0
        
        new_height = self._calculate_grid_height(preset_count, columns, name_label_height)
        grid_info.widget.setFixedHeight(new_height)
        
        for index, preset in enumerate(presets):
            brush_button = self._add_preset_button(
                preset, grid_info, layout, columns, index, name_label_height
            )
            self._restore_button_selection(brush_button, index, selected_indices)
        
        self.update_selection_highlights()
        self.update_grid_visibility(grid_info)

    def _update_grid_name_ui(self, grid_info: GridInfo, new_name):
        """Update grid name in UI elements."""
        grid_info.name = new_name
        if grid_info.name_label:
            grid_info.name_label.setText(new_name)
        if grid_info.name_button:
            grid_info.name_button.setText(new_name)
    
    def _update_all_grids_on_resize(self):
        """Update all grids with recalculated column count"""
        for grid_info in self.grids:
            if grid_info.layout and grid_info.brush_presets:
                self.update_grid(grid_info)

    def update_grid_visibility(self,  grid_info: GridInfo):
        """Show/hide the brush grid area based on collapse state and contents."""
        grid_widget = grid_info.widget
        if not grid_widget:
            return
        has_brushes = len(grid_info.brush_presets) > 0
        is_collapsed = grid_info.is_collapsed
        grid_widget.setVisible(has_brushes and not is_collapsed)

    def update_drag_highlights(self):
        """Update edge highlights based on cursor position during drag"""
        if not self.dragging_button:
            return
        
        cursor_pos = QCursor.pos()

        # Update auto-scroll edge detection
        self.update_auto_scroll_edge_detection(cursor_pos)
        
        # Find which button the cursor is over
        hovered_button = None
        for btn in self.brush_buttons:
            if btn == self.dragging_button:
                continue
            
            btn_global_pos = btn.mapToGlobal(QPoint(0, 0))
            btn_rect = btn.geometry()
            btn_right = btn_global_pos.x() + btn_rect.width()
            btn_bottom = btn_global_pos.y() + btn_rect.height()
            
            if (btn_global_pos.x() <= cursor_pos.x() <= btn_right and
                btn_global_pos.y() <= cursor_pos.y() <= btn_bottom):
                hovered_button = btn
                break
        
        # Update highlights for all buttons
        for btn in self.brush_buttons:
            if btn == self.dragging_button:
                continue
            
            if btn == hovered_button:
                if hasattr(btn, 'is_cursor_on_left_half'):
                    is_left = btn.is_cursor_on_left_half(cursor_pos)
                    if is_left:
                        btn.highlight_edge('left')
                    else:
                        btn.highlight_edge('right')
            else:
                if hasattr(btn, 'clear_edge_highlight'):
                    btn.clear_edge_highlight()

    def update_auto_scroll_edge_detection(self, cursor_pos):
        """Update auto-scroll edge detection based on cursor position"""
        if not hasattr(self, 'scroll_area') or not self.scroll_area:
            self.edge_scroll_direction = 0
            self.edge_scroll_distance = 0
            self.edge_touch_start_time = None
            return
        
        viewport = self.scroll_area.viewport()
        viewport_global_pos = viewport.mapToGlobal(QPoint(0, 0))
        viewport_height = viewport.height()
        
        cursor_y_relative = cursor_pos.y() - viewport_global_pos.y()
        
        distance_from_top = cursor_y_relative
        distance_from_bottom = viewport_height - cursor_y_relative
        
        SCROLL_ZONE = 30
        
        if distance_from_top <= SCROLL_ZONE:
            self.edge_scroll_direction = -1
            self.edge_scroll_distance = max(0, distance_from_top)
            
            if distance_from_top <= 1:
                if self.edge_touch_start_time is None:
                    self.edge_touch_start_time = QTime.currentTime()
            else:
                self.edge_touch_start_time = None
        elif distance_from_bottom <= SCROLL_ZONE:
            self.edge_scroll_direction = 1
            self.edge_scroll_distance = max(0, distance_from_bottom)
            
            if distance_from_bottom <= 1:
                if self.edge_touch_start_time is None:
                    self.edge_touch_start_time = QTime.currentTime()
            else:
                self.edge_touch_start_time = None
        else:
            self.edge_scroll_direction = 0
            self.edge_scroll_distance = 0
            self.edge_touch_start_time = None

    def update_selection_highlights(self):
        """Update highlight state for all buttons based on selection"""
        for button in self.brush_buttons:
            if hasattr(button, 'preset'):
                is_selected = button in self.selected_buttons
                button.update_selection_highlight(is_selected)
    
    def update_grid_selection_highlights(self):
        """Update visual highlights for selected grids."""
        for grid in self.grids:
            if grid in self.selected_grids:
                self._apply_grid_widget_styles(
                    grid,
                    SELECTED_NAME_BUTTON_STYLE,
                    SELECTED_COLLAPSE_BUTTON_STYLE,
                    SELECTED_WIDGET_STYLE
                )
            else:
                self.update_grid_style(grid)

    def update_grid_style(self, grid_info: GridInfo):
        """Update visual style based on active status and selection."""
        if grid_info in self.selected_grids:
            return  # Already handled by update_grid_selection_highlights
        
        is_active = grid_info.is_active
        
        widget_style = """
            QWidget {
                border: 1px solid #555;
                background-color: #474747;
            }
        """ if is_active else """
            QWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
        """
        
        if is_active:
            self._apply_grid_widget_styles(
                grid_info,
                ACTIVE_NAME_BUTTON_STYLE,
                ACTIVE_COLLAPSE_BUTTON_STYLE,
                widget_style
            )
        else:
            self._apply_grid_widget_styles(
                grid_info,
                INACTIVE_NAME_BUTTON_STYLE,
                INACTIVE_COLLAPSE_BUTTON_STYLE,
                widget_style
            )
        


    def _clear_grid_buttons(self, layout):
        """Clear all buttons from the grid layout"""
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if not widget:
                continue
            if widget in self.brush_buttons:
                self.brush_buttons.remove(widget)
            if widget in self.selected_buttons:
                self.selected_buttons.remove(widget)
            layout.removeWidget(widget)
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()

    def _clear_last_selected_if_in_grid(self, grid_info: GridInfo):
        """Clear last_selected_button if it was in this grid"""
        if not self.last_selected_button:
            return
        if not hasattr(self.last_selected_button, 'grid_info'):
            return
        if self.last_selected_button.grid_info == grid_info:
            self.last_selected_button = None


    def move_grids_to_position(self, source_grids, target_grid, insert_after=False):
        """Move source grids to a new position relative to target grid.
        
        Args:
            source_grids: List of grids to move
            target_grid: The grid to position relative to
            insert_after: If True, insert after target; if False, insert before
        """
        if not source_grids or not target_grid:
            return
        
        # Don't move if target is one of the source grids
        if target_grid in source_grids:
            return
        
        # Remove source grids from their current positions
        for grid in source_grids:
            if grid in self.grids:
                self.grids.remove(grid)
        
        # Find target position
        try:
            target_idx = self.grids.index(target_grid)
        except ValueError:
            # Target grid not found, append to end
            target_idx = len(self.grids)
        
        # Adjust position if inserting after
        if insert_after:
            target_idx += 1
        
        # Insert source grids at the target position
        for i, grid in enumerate(source_grids):
            self.grids.insert(target_idx + i, grid)
        
        # Clear selection after move
        self.selected_grids = []
        self.last_selected_grid = None
        
        # Rebuild the layout and save
        self.rebuild_grid_layout()
        self.update_grid_selection_highlights()

    def move_grid(self, grid_info: GridInfo, direction: int):
        """Move a grid up or down in the list"""
        idx = self.grids.index(grid_info)
        new_idx = idx + direction
        if 0 <= new_idx < len(self.grids):
            self.grids.pop(idx)
            self.grids.insert(new_idx, grid_info)
            self.rebuild_grid_layout()
            self.save_grids_data()













    def show_grid_name_context_dialog(self, name_widget: QPushButton, grid_info: "GridInfo", global_pos):
        """Show context dialog for grid name on right-click"""
        if grid_info in self.selected_grids and len(self.selected_grids) > 1:
            target_grid = None
        else:
            target_grid = grid_info
        dialog = GridNameContextDialog(
            self, 
            target_grid, 
            self.rename_grid, 
            self.remove_grid
        )
        dialog.move(global_pos)
        dialog.exec_()


    def get_grids_being_dragged(self):
        """Get the list of grids currently being dragged."""
        self._init_grid_drag_state()
        return self._grids_being_dragged

    def get_buttons_in_range(self, button1, button2, grid_info: GridInfo):
        """Get all buttons between button1 and button2 in the grid"""
        if button1 == button2:
            return [button1]
        
        layout = grid_info.get("layout")
        if not layout:
            return []
        
        buttons = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item:
                btn = item.widget()
                if btn and hasattr(btn, 'preset'):
                    buttons.append(btn)
        
        try:
            idx1 = buttons.index(button1)
            idx2 = buttons.index(button2)
        except ValueError:
            return []
        
        start_idx = min(idx1, idx2)
        end_idx = max(idx1, idx2)
        return buttons[start_idx:end_idx + 1]
    
    def get_dynamic_columns(self):
        """Calculate max_brush_per_row dynamically based on available docker width"""
        if hasattr(self, 'scroll_area') and self.scroll_area:
            available_widget = self.scroll_area.viewport()
        else:
            available_widget = self.main_widget if self.main_widget else self.widget()
        
        if not available_widget:
            max_brush = get_common_config().layout.max_brush_per_row
            return int(max_brush)
        
        available_width = available_widget.width()
        if available_width <= 0:
            max_brush = get_common_config().layout.max_brush_per_row
            return int(max_brush)
        
        button_size = get_brush_icon_size()
        spacing = get_spacing_between_buttons()
        
        margin_buffer = 4
        usable_width = available_width - margin_buffer
        
        if button_size + spacing <= 0:
            return 1
        
        max_columns = max(1, int((usable_width + spacing) / (button_size + spacing)))
        return max_columns
    
    def _get_next_group_number(self):
        """Calculate the next available group number."""
        existing_numbers = []
        for grid in self.grids:
            name = str(grid.name).strip()
            match = _GROUP_NAME_PATTERN.match(name)
            if match:
                existing_numbers.append(int(match.group(1)))
        return max(existing_numbers, default=0) + 1


    def set_active_grid(self, grid_info: GridInfo):
        """Set a grid as active"""
        for grid in self.grids:
            grid.is_active = False
            self.update_grid_style(grid)
        grid_info.is_active = True
        self.active_grid = grid_info
        self.update_grid_style(grid_info)
        self.update_grid_selection_highlights()
    
    def _set_collapse_button_icon(self, collapse_button, is_collapsed, icon_size):
        """Set the collapse button icon based on collapse state."""
        icon_name = "arrow-right" if is_collapsed else "arrow-down"
        icon = Krita.instance().icon(icon_name)
        
        if not icon or icon.isNull():
            return
        
        # Use high-res then scale down for quality
        pixmap = icon.pixmap(icon_size * 2, icon_size * 2)
        if not pixmap.isNull():
            scaled = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            collapse_button.setIcon(QIcon(scaled))
        else:
            collapse_button.setIcon(icon)
        collapse_button.setIconSize(QSize(icon_size, icon_size))


    def select_button(self, button, add_to_selection=False, range_selection=False):
        """Select a button with optional modifiers"""
        if not hasattr(button, 'preset'):
            return
        
        if range_selection and self.last_selected_button:
            grid_info = button.grid_info
            buttons_to_select = self.get_buttons_in_range(self.last_selected_button, button, grid_info)
            self.selected_buttons = list(set(self.selected_buttons + buttons_to_select))
            self.last_selected_button = button
        elif add_to_selection:
            if button in self.selected_buttons:
                self.selected_buttons.remove(button)
                if self.last_selected_button == button:
                    self.last_selected_button = None
            else:
                self.selected_buttons.append(button)
                self.last_selected_button = button
        else:
            self.selected_buttons = [button]
            self.last_selected_button = button
        
        self.update_selection_highlights()
    
    def select_single_grid(self, grid_info: GridInfo):
        """Select a single grid, deselecting all others"""
        self.selected_grids = [grid_info]
        self.last_selected_grid = grid_info
        self.set_active_grid(grid_info)
        self.update_grid_selection_highlights()

    def select_grid_range(self, grid_info: GridInfo):
        """Select a range of grids from last_selected_grid to grid_info"""
        if not self.last_selected_grid or self.last_selected_grid == grid_info:
            self.selected_grids = [grid_info]
            self.last_selected_grid = grid_info
        else:
            try:
                start_idx = self.grids.index(self.last_selected_grid)
                end_idx = self.grids.index(grid_info)
                
                if start_idx < end_idx:
                    grids_to_select = self.grids[start_idx:end_idx + 1]
                else:
                    grids_to_select = self.grids[end_idx:start_idx + 1]
                
                for grid in grids_to_select:
                    if grid not in self.selected_grids:
                        self.selected_grids.append(grid)
                
                self.last_selected_grid = grid_info
            except ValueError:
                self.selected_grids = [grid_info]
                self.last_selected_grid = grid_info
        
        self.update_grid_selection_highlights()
    

    def handle_delete_button_click(self):
        """Handle click on the delete button (deletelayer icon)"""
        if self.selected_buttons:
            self.remove_selected_brushes()
        elif self.selected_grids:
            self.remove_grid()
    
    def _handle_name_button_right_click(self, event, name_button: QPushButton, grid_info: "GridInfo"):
        """Handle right-click on grid name button"""
        mods = QApplication.keyboardModifiers()
        if mods == Qt.ShiftModifier:
            self.select_grid_range(grid_info)
            self.show_grid_name_context_dialog(name_button, grid_info, event.globalPos())
        elif mods == Qt.ControlModifier:
            self.toggle_grid_selection(grid_info)
            self.show_grid_name_context_dialog(name_button, grid_info, event.globalPos())
        elif mods == Qt.NoModifier:
            self.show_grid_name_context_dialog(name_button, grid_info, event.globalPos())
        elif mods == Qt.AltModifier:
            self.rename_grid(grid_info)
        elif (mods & (Qt.ControlModifier | Qt.AltModifier | Qt.ShiftModifier)) == (Qt.ControlModifier | Qt.AltModifier | Qt.ShiftModifier):
            self.remove_grid(grid_info)


    def _apply_grid_widget_styles(self, grid_info: GridInfo, name_style, collapse_style, widget_style):
        """Apply styles to grid widget components."""
        name_button = grid_info.name_button or grid_info.name_label
        collapse_button = grid_info.collapse_button
        
        if name_button:
            name_button.setStyleSheet(name_style)
        if collapse_button:
            collapse_button.setStyleSheet(collapse_style)
        grid_info.widget.setStyleSheet(widget_style)



    def _apply_button_style(self, button, icon_name):
        """Apply appropriate style to button based on icon name"""
        if icon_name in ("addbrushicon", "folder", "settings-button", "deletelayer"):
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #474747;
                    border: none;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.3);
                }
            """
            )
        else:
            base_style = docker_btn_style()
            enhanced_style = base_style + """
                QPushButton {
                    background-color: #474747;
                    border: 1px solid #555;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.3);
                }
            """
            button.setStyleSheet(enhanced_style)


    def toggle_grid_collapse(self,  grid_info: GridInfo):
        """Toggle collapse state of a grid.
        
        In exclusive uncollapse mode, only one grid can be uncollapsed at a time.
        The uncollapsed grid becomes the active_grid.
        """
        from .utils.config_utils import get_exclusive_uncollapse
        
        is_currently_collapsed = grid_info.is_collapsed
        new_collapsed_state = not is_currently_collapsed
        
        if get_exclusive_uncollapse():
            if new_collapsed_state:
                # Collapsing this grid
                grid_info.is_collapsed = True
                self._update_collapse_button_icon(grid_info)
                self.update_grid_visibility(grid_info)
                
                # Check if all grids are now collapsed
                all_collapsed = all(g.is_collapsed for g in self.grids)
                if all_collapsed:
                    # Deselect active_grid when all are collapsed
                    self._clear_active_grid_highlight()
            else:
                # Uncollapsing this grid - collapse all others first
                for other_grid in self.grids:
                    if other_grid != grid_info and not other_grid.is_collapsed:
                        other_grid.is_collapsed = True
                        self._update_collapse_button_icon(other_grid)
                        self.update_grid_visibility(other_grid)
                
                # Now uncollapse the target grid
                grid_info.is_collapsed = False
                self._update_collapse_button_icon(grid_info)
                self.update_grid_visibility(grid_info)
                
                # Set this grid as active
                self.set_active_grid(grid_info)
        else:
            # Normal mode - just toggle
            grid_info.is_collapsed = new_collapsed_state
            self._update_collapse_button_icon(grid_info)
            self.update_grid_visibility(grid_info)
    
    def toggle_grid_selection(self, grid_info: GridInfo):
        """Toggle selection of a grid"""
        if grid_info in self.selected_grids:
            self.selected_grids.remove(grid_info)
            if self.last_selected_grid == grid_info:
                self.last_selected_grid = None
        else:
            self.selected_grids.append(grid_info)
            self.last_selected_grid = grid_info
        self.update_grid_selection_highlights()
    




    def _finish_inline_grid_rename(self, editor, apply_change):
        """Finalize inline rename: apply or discard, then restore the button."""
        grid_info = getattr(editor, "_grid_info", None)
        original_name = getattr(editor, "_original_name", None)

        if not grid_info or original_name is None:
            return

        header_layout = grid_info.header_layout
        name_button = grid_info.name_button or grid_info.name_label

        if not header_layout or not name_button:
            return

        if apply_change:
            new_name = editor.text().strip()
            if new_name and new_name != original_name:
                self._update_grid_name_ui(grid_info, new_name)
                self.save_grids_data()

        header_layout.replaceWidget(editor, name_button)
        name_button.show()
        grid_info.name_editor = None
        editor.deleteLater()

    def _init_grid_drag_state(self):
        """Initialize grid drag tracking state."""
        if not hasattr(self, '_grids_being_dragged'):
            self._grids_being_dragged = []
    
    def start_inline_grid_rename(self, grid_info: GridInfo):
        """Turn the grid name button into an inline editable textbox."""
        if grid_info.name_editor:
            return

        container = grid_info.container
        header_layout = grid_info.header_layout
        name_button = grid_info.name_button or grid_info.name_label

        if not all([container, header_layout, name_button]):
            return

        original_name = grid_info.name
        editor = self._create_inline_editor(container, original_name)
        editor._grid_info = grid_info
        editor._original_name = original_name

        header_layout.replaceWidget(name_button, editor)
        name_button.hide()
        grid_info.name_editor = editor

        editor.setFocus()
        editor.selectAll()
        editor.returnPressed.connect(lambda: self._finish_inline_grid_rename(editor, True))
        editor.installEventFilter(self)

    def rebuild_grid_layout(self):
        """Rebuild the grid layout after reordering"""
        for i in reversed(range(self.main_grid_layout.count())):
            item = self.main_grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.main_grid_layout.removeWidget(widget)

        for grid_info in self.grids:
            self.main_grid_layout.addWidget(grid_info.container)

        for grid_info in self.grids:
            self.update_grid_style(grid_info)
        self.save_grids_data()

    def _store_selected_indices(self, layout):
        """Store indices of selected buttons before clearing"""
        selected_indices = set()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if not item:
                continue
            btn = item.widget()
            if btn and btn in self.selected_buttons:
                selected_indices.add(i)
        return selected_indices

    def _cleanup_grid_buttons(self, layout):
        """Remove all buttons from a grid layout."""
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                if widget in self.brush_buttons:
                    self.brush_buttons.remove(widget)
                layout.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()

    def _is_preset_selected(self, preset: GridPresetItem):
        """Check if preset matches currently selected preset"""
        if self.current_selected_preset is None:
            return False
        return preset.name() == self.current_selected_preset.name()

    def _restore_button_selection(self, brush_button: DraggableBrushButton, index, selected_indices):
        """Restore selection state for button if it was previously selected"""
        if index not in selected_indices:
            return
        if brush_button in self.selected_buttons:
            return
        self.selected_buttons.append(brush_button)
        if not self.last_selected_button:
            self.last_selected_button = brush_button

    def _setup_name_button_events(self, name_button: QPushButton, grid_info: "GridInfo"):
        #TODO: Reinject
        """Setup all event handlers for the grid name button.
        
        Note: mouseMoveEvent is not overridden - drag handling is done by
        the parent DraggableGridRow widget.
        """
        name_button.mousePressEvent = self._create_name_button_mousePressEvent(name_button, grid_info)
        name_button.mouseReleaseEvent = self._create_name_button_mouseReleaseEvent(name_button, grid_info)
        name_button.mouseDoubleClickEvent = self._create_name_button_mouseDoubleClickEvent(name_button, grid_info)

    def _monitor_scroll_position(self):
        """Continuously monitor and restore scroll position after drag drop.
        
        This runs at 60fps for a fixed duration after drop to catch any
        late scroll adjustments from Qt's layout system, especially for
        edge cases like dropping at first/last buttons of topmost/bottommost grids.
        """
        if self._preserved_scroll_position is None or self._scroll_monitor_start_time is None:
            self._scroll_monitor_timer.stop()
            return
        
        # Check if monitoring period has elapsed
        elapsed_ms = self._scroll_monitor_start_time.msecsTo(QTime.currentTime())
        if elapsed_ms >= self._scroll_monitor_duration:
            # Monitoring complete - clean up
            self._scroll_monitor_timer.stop()
            self._preserved_scroll_position = None
            self._autoscroll_used = False
            self._scroll_monitor_start_time = None
            return
        
        # Restore scroll position if it has drifted
        if hasattr(self, 'scroll_area') and self.scroll_area:
            scroll_bar = self.scroll_area.verticalScrollBar()
            if scroll_bar and scroll_bar.value() != self._preserved_scroll_position:
                scroll_bar.setValue(self._preserved_scroll_position)
    
    def perform_auto_scroll(self):
        """Perform auto-scrolling based on edge detection"""
        if not self.edge_scroll_direction or not hasattr(self, 'scroll_area') or not self.scroll_area:
            return
        
        SCROLL_ZONE = 30
        
        if self.edge_scroll_distance <= 1 and self.edge_touch_start_time:
            elapsed_ms = self.edge_touch_start_time.msecsTo(QTime.currentTime())
            elapsed_seconds = elapsed_ms / 300.0
            exponential_factor = min(2.0 ** elapsed_seconds, 3.0)
            scroll_speed = self.base_scroll_speed * exponential_factor
        else:
            speed_factor = (SCROLL_ZONE - self.edge_scroll_distance) / SCROLL_ZONE
            scroll_speed = self.base_scroll_speed * (0.1 + 0.9 * speed_factor)
        
        scroll_bar = self.scroll_area.verticalScrollBar()
        if scroll_bar:
            current_value = scroll_bar.value()
            new_value = current_value + (self.edge_scroll_direction * scroll_speed)
            scroll_bar.setValue(int(new_value))
            
            # Mark that autoscroll was used (for scroll position preservation)
            if scroll_bar.value() != current_value:
                self._autoscroll_used = True





    
    def scroll_area_click_handler(self, event):
        """Handle clicks on scroll area to deselect"""
        from PyQt5.QtCore import Qt
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            if event.pos().x() < self.scroll_area.viewport().width():
                self.clear_selection()
        QScrollArea.mousePressEvent(self.scroll_area, event)

    
    def start_drag_tracking(self, button):
        """Start tracking drag for edge highlighting"""
        self.dragging_button = button
        self._autoscroll_used = False
        self._preserved_scroll_position = None
        # Stop any ongoing scroll monitoring from previous drag
        self._scroll_monitor_timer.stop()
        self._scroll_monitor_start_time = None
        self.drag_highlight_timer.start()
        self.auto_scroll_timer.start()
    
    def stop_drag_tracking(self):
        """Stop tracking drag and clear highlights.
        
        If autoscroll was used during drag, preserve the current scroll position
        and start continuous monitoring to restore it. This handles edge cases where
        Qt's layout system triggers late scroll adjustments, especially when dropping
        at the first/last buttons of the topmost/bottommost grids.
        """
        # Capture scroll position before stopping, if autoscroll was used
        if self._autoscroll_used and hasattr(self, 'scroll_area') and self.scroll_area:
            scroll_bar = self.scroll_area.verticalScrollBar()
            if scroll_bar:
                self._preserved_scroll_position = scroll_bar.value()
                # Start continuous monitoring to catch and correct any scroll jumps
                self._scroll_monitor_start_time = QTime.currentTime()
                self._scroll_monitor_timer.start()
        
        self.dragging_button = None
        self.drag_highlight_timer.stop()
        self.auto_scroll_timer.stop()
        # Clear all edge highlights
        for btn in self.brush_buttons:
            if hasattr(btn, 'clear_edge_highlight'):
                btn.clear_edge_highlight()
    
    

class PresetGroupsDockerFactory(DockWidgetFactoryBase):
    """Factory for creating the Preset Groups docker widget."""

    def __init__(self):
        super().__init__(TouchifyEnv.DockerID.QUICK_ACTIONS, DockWidgetFactory.DockRight)

    def createDockWidget(self):
        return QuickActionsDocker()
