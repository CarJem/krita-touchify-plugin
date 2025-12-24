"""Settings dialog for Preset Groups plugin.

Provides a minimalistic Photoshop-style settings interface with
organized sections for shortcuts, appearance, and navigation options.
"""

import os
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDoubleSpinBox,
    QFrame,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from krita import Krita
from touchify_quick_actions.utils.data_manager import load_common_config, save_common_config

# Path to custom icons in the ui folder
_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")


# Style constants for Photoshop-like minimalistic UI
_DIALOG_STYLE = """
    QDialog {
        background-color: #474747;
        color: #d2d2d2;
    }
"""

_SECTION_LABEL_STYLE = """
    QLabel {
        color: #8a8a8a;
        font-size: 10px;
        font-weight: bold;
        padding: 0px;
        margin: 0px;
    }
"""

_FIELD_LABEL_STYLE = """
    QLabel {
        color: #d2d2d2;
        font-size: 11px;
        padding: 0px;
        background: transparent;
    }
"""

_INPUT_STYLE = """
    QLineEdit, QDoubleSpinBox {
        background-color: #383838;
        color: #d2d2d2;
        border: 1px solid #4a4a4a;
        border-radius: 3px;
        padding: 4px 6px;
        font-size: 11px;
    }
    QLineEdit:focus, QDoubleSpinBox:focus {
        border: 1px solid #5a8fd8;
    }
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
        width: 16px;
        background-color: #4a4a4a;
        border: none;
    }
    QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #5a5a5a;
    }
"""

_TOGGLE_ON_STYLE = """
    QPushButton {
        background-color: #4a7c59;
        color: white;
        border: none;
        border-radius: 3px;
        font-size: 10px;
        font-weight: bold;
        padding: 3px 8px;
    }
    QPushButton:hover {
        background-color: #5a8c69;
    }
"""

_TOGGLE_OFF_STYLE = """
    QPushButton {
        background-color: #5a5a5a;
        color: #888888;
        border: none;
        border-radius: 3px;
        font-size: 10px;
        font-weight: bold;
        padding: 3px 8px;
    }
    QPushButton:hover {
        background-color: #6a6a6a;
    }
"""

_BUTTON_STYLE = """
    QPushButton {
        background-color: #4a4a4a;
        color: #d2d2d2;
        border: none;
        border-radius: 3px;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5a5a5a;
    }
    QPushButton:pressed {
        background-color: #3a3a3a;
    }
"""

_PRIMARY_BUTTON_STYLE = """
    QPushButton {
        background-color: #5a8fd8;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #6a9fe8;
    }
    QPushButton:pressed {
        background-color: #4a7fc8;
    }
"""

_SEPARATOR_STYLE = """
    QFrame {
        background-color: #3a3a3a;
        border: none;
        max-height: 1px;
    }
"""


class CommonConfigDialog(QDialog):
    """Dialog for editing common configuration settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preset Groups")
        self.resize(325, 420)
        self.setStyleSheet(_DIALOG_STYLE)
        
        # Store original values for fallback
        self._add_brush_key_original = None
        self._choose_left_key_original = None
        self._choose_right_key_original = None

        self.load_config()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the UI elements with minimalistic Photoshop-style design"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        self.fields = {}

        # === APPEARANCE SECTION ===
        layout.addWidget(self._create_section_label("APPEARANCE"))
        
        # Max Brush Size
        layout.addLayout(self._create_spinbox_row(
            "Max Brush Size",
            "max_brush_size",
            self._calculate_max_brush_size_value(),
            100, 10000, 10, " px"
        ))
        
        # Spacing Between Buttons
        layout_config = self.config.layout
        spacing_value = layout_config.spacing_between_buttons
        layout.addLayout(self._create_input_row(
            "Button Spacing",
            "layout", "spacing_between_buttons",
            str(spacing_value),
            width=50
        ))
        
        # Display Brush Names toggle
        layout.addLayout(self._create_toggle_row(
            "Display Brush Names",
            "display_brush_names",
            self.config.get("layout", {}).get("display_brush_names", True),
            "edit-rename"
        ))
        
        layout.addWidget(self._create_separator())
        
        # === SHORTCUTS SECTION ===
        layout.addWidget(self._create_section_label("KEYBOARD SHORTCUTS"))
        
        shortcut_config = self.config.get("shortcut", {})
        
        # Add Brush to Grid
        add_brush_val = shortcut_config.get("add_brush_to_grid", "W")
        self._add_brush_key_original = add_brush_val
        layout.addLayout(self._create_shortcut_row(
            "Add Brush to Group",
            "shortcut", "add_brush_to_grid",
            add_brush_val,
            "addbrushicon"
        ))
        
        # Choose Previous
        prev_val = shortcut_config.get("choose_left_in_grid", ",")
        self._choose_left_key_original = prev_val
        layout.addLayout(self._create_shortcut_row(
            "Previous Brush",
            "shortcut", "choose_left_in_grid",
            prev_val,
            "arrow-left"
        ))
        
        # Choose Next
        next_val = shortcut_config.get("choose_right_in_grid", ".")
        self._choose_right_key_original = next_val
        layout.addLayout(self._create_shortcut_row(
            "Next Brush",
            "shortcut", "choose_right_in_grid",
            next_val,
            "arrow-right"
        ))
        
        layout.addWidget(self._create_separator())
        
        # === NAVIGATION SECTION ===
        layout.addWidget(self._create_section_label("NAVIGATION"))
        
        # Wrap-around toggle
        wrap_value = shortcut_config.get("wrap_around_navigation", True)
        layout.addLayout(self._create_toggle_row(
            "Loop Navigation",
            "wrap_around_navigation",
            wrap_value,
            "reload-preset"
        ))
        
        # Exclusive Uncollapse toggle
        exclusive_value = layout_config.get("exclusive_uncollapse", False)
        layout.addLayout(self._create_toggle_row(
            "Exclusive Uncollapse",
            "exclusive_uncollapse",
            exclusive_value,
            "collapse-all"
        ))
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # === BUTTONS ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(_BUTTON_STYLE)
        self.cancel_btn.setFixedHeight(28)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet(_PRIMARY_BUTTON_STYLE)
        self.save_btn.setFixedHeight(28)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

    def _create_section_label(self, text):
        """Create a section header label"""
        label = QLabel(text)
        label.setStyleSheet(_SECTION_LABEL_STYLE)
        return label

    def _create_separator(self):
        """Create a horizontal separator line"""
        sep = QFrame()
        sep.setStyleSheet(_SEPARATOR_STYLE)
        sep.setFixedHeight(1)
        return sep

    def _create_input_row(self, label_text: str, section: str, key: str, value: any, width=60):
        """Create a row with label and text input"""
        hlayout = QHBoxLayout()
        hlayout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setStyleSheet(_FIELD_LABEL_STYLE)
        
        edit = QLineEdit(str(value))
        edit.setStyleSheet(_INPUT_STYLE)
        edit.setFixedWidth(width)
        edit.setAlignment(Qt.AlignCenter)
        
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(edit)
        
        self.fields[(section, key)] = edit
        return hlayout

    def _create_shortcut_row(self, label_text, section, key, value, icon_name=None):
        """Create a row for shortcut key input with optional icon"""
        hlayout = QHBoxLayout()
        hlayout.setSpacing(8)
        
        # Icon (optional)
        if icon_name:
            icon_label = QLabel()
            pixmap = None
            
            # Try loading custom icon first
            custom_icon_path = os.path.join(_UI_DIR, f"{icon_name}.png")
            if os.path.exists(custom_icon_path):
                custom_pixmap = QPixmap(custom_icon_path)
                if not custom_pixmap.isNull():
                    pixmap = custom_pixmap.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Fall back to Krita's built-in icons
            if pixmap is None:
                icon = Krita.instance().icon(icon_name)
                if icon and not icon.isNull():
                    pixmap = icon.pixmap(14, 14)
            
            if pixmap:
                icon_label.setPixmap(pixmap)
                icon_label.setFixedSize(16, 16)
                hlayout.addWidget(icon_label)
        
        label = QLabel(label_text)
        label.setStyleSheet(_FIELD_LABEL_STYLE)
        
        edit = QLineEdit(str(value))
        edit.setStyleSheet(_INPUT_STYLE)
        edit.setFixedWidth(36)
        edit.setMaxLength(1)
        edit.setAlignment(Qt.AlignCenter)
        
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(edit)
        
        self.fields[(section, key)] = edit
        return hlayout

    def _create_spinbox_row(self, label_text, key, value, min_val, max_val, step, suffix):
        """Create a row with label and spinbox"""
        hlayout = QHBoxLayout()
        hlayout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setStyleSheet(_FIELD_LABEL_STYLE)
        
        spinbox = QDoubleSpinBox()
        spinbox.setStyleSheet(_INPUT_STYLE)
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setSingleStep(step)
        spinbox.setSuffix(suffix)
        spinbox.setValue(value)
        spinbox.setFixedWidth(90)
        spinbox.setDecimals(0)
        
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(spinbox)
        
        # Store reference
        if key == "max_brush_size":
            self.max_brush_spinbox = spinbox
        
        return hlayout

    def _create_toggle_row(self, label_text, key, is_on, icon_name=None):
        """Create a row with label and toggle button"""
        hlayout = QHBoxLayout()
        hlayout.setSpacing(8)
        
        # Icon (optional)
        if icon_name:
            icon_label = QLabel()
            icon = Krita.instance().icon(icon_name)
            if icon and not icon.isNull():
                icon_label.setPixmap(icon.pixmap(14, 14))
                icon_label.setFixedSize(16, 16)
                hlayout.addWidget(icon_label)
        
        label = QLabel(label_text)
        label.setStyleSheet(_FIELD_LABEL_STYLE)
        
        toggle = QPushButton()
        toggle.setFixedSize(44, 20)
        toggle.setCheckable(True)
        toggle.setChecked(is_on)
        self._update_toggle_style(toggle)
        toggle.clicked.connect(lambda: self._update_toggle_style(toggle))
        
        hlayout.addWidget(label)
        hlayout.addStretch()
        hlayout.addWidget(toggle)
        
        # Store reference
        if key == "wrap_around_navigation":
            self.wrap_around_btn = toggle
        elif key == "display_brush_names":
            self.display_names_btn = toggle
        elif key == "exclusive_uncollapse":
            self.exclusive_uncollapse_btn = toggle
        
        return hlayout

    def _update_toggle_style(self, toggle):
        """Update toggle button appearance based on state"""
        if toggle.isChecked():
            toggle.setText("ON")
            toggle.setStyleSheet(_TOGGLE_ON_STYLE)
        else:
            toggle.setText("OFF")
            toggle.setStyleSheet(_TOGGLE_OFF_STYLE)

    def _ensure_config_sections(self):
        """Ensure all required config sections exist with defaults"""
        default_sections = {
            "shortcut": {
                "add_brush_to_grid": "W",
                "choose_left_in_grid": ",",
                "choose_right_in_grid": ".",
                "wrap_around_navigation": True,
            },
            "layout": {
                "spacing_between_buttons": 1,
                "display_brush_names": True,
                "exclusive_uncollapse": False,
            },
        }
        for section, defaults in default_sections.items():
            if section not in self.config:
                self.config[section] = defaults.copy()
            else:
                for key, default_value in defaults.items():
                    if key not in self.config[section]:
                        self.config[section][key] = default_value

    def _ensure_brush_slider_section(self):
        """Ensure brush_slider section exists in config"""
        if "brush_slider" not in self.config:
            self.config["brush_slider"] = {}
        if "max_brush_size" not in self.config["brush_slider"]:
            self.config["brush_slider"]["max_brush_size"] = 1000

    def _get_current_brush_size_from_krita(self):
        """Get current brush size from Krita if available"""
        try:
            app = Krita.instance()
            if not app.activeWindow() or not app.activeWindow().activeView():
                return None
            view = app.activeWindow().activeView()
            if hasattr(view, "brushSize"):
                return view.brushSize()
        except Exception:
            pass
        return None

    def _calculate_max_brush_size_value(self):
        """Calculate the value to set for max brush size spinbox"""
        config_max = float(self.config.get("brush_slider", {}).get("max_brush_size", 1000))
        current_brush_size = self._get_current_brush_size_from_krita()
        
        if current_brush_size is None:
            return config_max
        
        if current_brush_size > config_max:
            return max(100, min(10000, int(current_brush_size)))
        return config_max

    def load_config(self):
        """Load configuration from file"""
        self.config = load_common_config()

    def setup_connections(self):
        """Setup button connections"""
        self.save_btn.clicked.connect(self.save_and_close)
        self.cancel_btn.clicked.connect(self.reject)
    
    def save_and_close(self):
        """Save configuration and close dialog"""
        # Ensure required sections exist
        for section in ["shortcut", "layout", "brush_presets", "brush_slider"]:
            if section not in self.config:
                self.config[section] = {}
        
        # Save max brush size from QDoubleSpinBox
        if hasattr(self, 'max_brush_spinbox'):
            max_brush_size = int(self.max_brush_spinbox.value())
            self.config["brush_slider"]["max_brush_size"] = max_brush_size
        
        # Save wrap-around toggle
        if hasattr(self, 'wrap_around_btn'):
            self.config["shortcut"]["wrap_around_navigation"] = self.wrap_around_btn.isChecked()
        
        # Save display brush names toggle
        if hasattr(self, 'display_names_btn'):
            self.config["layout"]["display_brush_names"] = self.display_names_btn.isChecked()
        
        # Save exclusive uncollapse toggle
        if hasattr(self, 'exclusive_uncollapse_btn'):
            self.config["layout"]["exclusive_uncollapse"] = self.exclusive_uncollapse_btn.isChecked()
        
        # Save edits to config
        for (section, key), edit in self.fields.items():
            val = edit.text()

            # Enforce single-character shortcut for add_brush_to_grid
            if section == "shortcut" and key == "add_brush_to_grid":
                val = (val[:1] or "").strip()
                if not val:
                    val = (self._add_brush_key_original or "W")[:1]
                val = val.upper()

            # Enforce single-character shortcut for choose_left_in_grid
            if section == "shortcut" and key == "choose_left_in_grid":
                val = (val[:1] or "").strip()
                if not val:
                    val = (self._choose_left_key_original or ",")[:1]

            # Enforce single-character shortcut for choose_right_in_grid
            if section == "shortcut" and key == "choose_right_in_grid":
                val = (val[:1] or "").strip()
                if not val:
                    val = (self._choose_right_key_original or ".")[:1]

            # Type conversion for layout section
            if section == "layout":
                try:
                    val = int(val)
                except Exception:
                    pass

            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = val
        
        # Write to file
        save_common_config(self.config)

        self.accept()
