# SPDX-FileCopyrightText: © 2022-2024 Wojciech Trybus <wojtryb@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# Modified by Carter Wallace

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer

class AnimatedWidget(QWidget):
    """Adds the fade-in animation when the widget is shown (60 FPS)."""

    def __init__(self, parent, animation_time: float = 0) -> None:
        super().__init__(parent)
        self._animation_time = animation_time
        self._animation_interval = self._read_animation_interval()
        self._animation_timer = QTimer()
        self._animation_timer.setInterval(17)
        self._animation_timer.timeout.connect(self._increase_opacity)

    def show(self) -> None:
        """Decrease opacity to 0, and start a timer which animates it."""
        self.setWindowOpacity(0)
        self._animation_timer.start(17)
        super().show()

    def _increase_opacity(self) -> None:
        """Add interval to current opacity, stop the timer when full."""
        current_opacity = self.windowOpacity()
        self.setWindowOpacity(current_opacity+self._animation_interval)
        if current_opacity >= 1:
            self._animation_timer.stop()

    def _read_animation_interval(self) -> float:
        """Return how much opacity (0-1) should be increased on each frame."""
        if time := self._animation_time:
            return 0.0167/time
        return 1
