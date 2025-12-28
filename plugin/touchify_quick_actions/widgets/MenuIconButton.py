import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from krita import Krita
from touchify_quick_actions.utils.styles import MENU_ICON_BUTTON_STYLE # type: ignore


_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')

class MenuIconButton(QPushButton):

    def __init__(self, icon_name: str, callback):
        """Create an icon button with hover effects"""
        super().__init__(parent=None)
        self.setText("")

        self.refreshStyles()
        button_size = self.sizeHint().height()
        self.setFixedSize(QSize(button_size, button_size))

        icon_size = self._calculate_icon_size(icon_name, button_size)
        self._load_and_set_icon(icon_name, button_size, icon_size)

        self.clicked.connect(callback)

    def refreshStyles(self):
        self.setStyleSheet(MENU_ICON_BUTTON_STYLE())

    def _calculate_icon_size(self, icon_name, button_size):
        """Calculate icon size with special adjustments for specific icons"""
        base_icon_size = button_size
        if icon_name == "addbrushicon":
            return max(8, base_icon_size - 8)  # Smaller icon for Add Brush button
        if icon_name == "folder":
            return max(8, base_icon_size - 2)
        if icon_name == "deletelayer":
            return max(8, base_icon_size - 5)
        return base_icon_size

    def _load_custom_icon(self, icon_name):
        """Load a custom PNG icon from the ui folder"""
        icon_path = os.path.join(_UI_DIR, f"{icon_name}.png")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                return pixmap
        return None

    def _load_and_set_icon(self, icon_name, button_size, icon_size):
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
                self.setIcon(QIcon(scaled_pixmap))
                self.setIconSize(QSize(icon_size, icon_size))
                return

            # Fall back to Krita's built-in icons
            app = Krita.instance()
            icon = app.icon(icon_name)
            if not icon or icon.isNull():
                return

            high_res_size = icon_size * 2
            pixmap = icon.pixmap(high_res_size, high_res_size)
            if pixmap.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(icon_size, icon_size))
                return

            scaled_pixmap = pixmap.scaled(
                icon_size,
                icon_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            high_res_icon = QIcon(scaled_pixmap)
            self.setIcon(high_res_icon)
            self.setIconSize(QSize(icon_size, icon_size))
        except Exception as e:
            print(f"Error loading icon '{icon_name}': {e}")
