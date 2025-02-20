# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# Modified by Carter Wallace

from typing import Callable

from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt, QPoint


class RoundButton(QPushButton, QWidget):
    """Round button with custom icon."""

    def __init__(
        self, *,
        radius_callback: Callable[[], int],
        background_color_callback: Callable[[], QColor],
        active_color_callback: Callable[[], QColor],
        icon: QIcon = QIcon(),
        icon_scale: float = 1,
        parent: QWidget | None = None,
    ) -> None:
        QPushButton.__init__(self, icon, "", parent)
        self.setCursor(Qt.ArrowCursor)

        self._radius_callback = radius_callback
        self._icon_scale = icon_scale
        self._background_color_callback = background_color_callback
        self._active_color_callback = active_color_callback

        if parent is None:
            self.setWindowFlags((
                self.windowFlags() |  # type: ignore
                Qt.Tool |
                Qt.FramelessWindowHint |
                Qt.NoDropShadowWindowHint))
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setStyleSheet("background: transparent;")

        self.show()

    def show(self) -> None:
        """Change the size and repaint the button."""
        radius = self._radius_callback()
        self.resize(radius*2, radius*2)

        active_color = self._active_color_callback()
        background_color = self._background_color_callback()

        self.setStyleSheet(f"""
            QPushButton [
                border: {round(radius*0.06)}px
                    {self._color_to_str(self._border_color)};
                border-radius: {radius}px;
                border-style: outset;
                background: {self._color_to_str(background_color)};
                qproperty-iconSize:{round(radius*self._icon_scale)}px;
            ]
            QPushButton:hover [
                background: {self._color_to_str(active_color)};
            ]
        """.replace('[', '{').replace(']', '}'))

        super().show()

    @staticmethod
    def _color_to_str(color: QColor) -> str: return f'''rgba(
        {color.red()}, {color.green()}, {color.blue()}, {color.alpha()})'''

    @property
    def _border_color(self) -> QColor:
        """Color of button border."""
        background_color = self._background_color_callback()
        return QColor(
            min(background_color.red()+15, 255),
            min(background_color.green()+15, 255),
            min(background_color.blue()+15, 255),
            255)
    
    @property
    def center(self) -> QPoint:
        """Return point with center widget's point in its coordinates."""
        return QPoint(self.size().width()//2, self.size().height()//2)

    @property
    def center_global(self) -> QPoint:
        """Return point with center widget's point in screen coordinates."""
        return self.pos() + self.center  # type: ignore

    def move_center(self, new_center: QPoint) -> None:
        """Move the widget by providing a new center point."""
        self.move(new_center-self.center)  # type: ignore
