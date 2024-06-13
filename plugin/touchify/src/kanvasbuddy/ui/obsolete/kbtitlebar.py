# This file is part of KanvasBuddy.

# KanvasBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# KanvasBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.

from krita import Krita

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton, QStyle
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QSize, Qt

from ..kbbutton import KBButton
from ..kbconfigmanager import KBConfigManager

class KBTitleBar(QWidget):
    _config = KBConfigManager()
    _btnSize = int(_config.loadConfig('SIZES')['titleButtons'])
    _btnIconSize = _btnSize-3
    _fontSize = _btnSize-1

    def __init__(self, parent):
        super(KBTitleBar, self).__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 1, 2, 1)
        self.pressing = False

        font = self.font()
        font.setPixelSize(self._fontSize)
        self.title = QLabel("KanvasBuddy")
        self.title.setFont(font)
        self.title.setStyleSheet("""
            color: grey;
        """)

        self.pinnedMode = KBPinnedModeButton(self._btnSize, self._btnIconSize)
        self.closeButton = KBCloseButton(self._btnSize, self._btnIconSize)
        self.closeButton.clicked.connect(self.parent.close)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.pinnedMode)
        self.layout.addWidget(self.closeButton)
        self.setLayout(self.layout)


    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True


    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                self.mapToGlobal(self.movement).y(),
                                self.parent.width(),
                                self.parent.height())
            self.start = self.end


    def mouseReleaseEvent(self, event):
        self.pressing = False


class KBPinnedModeButton(KBButton):

    def __init__(self, size, iconSize, parent=None):
        super(KBPinnedModeButton, self).__init__(size, parent)
        self.setCheckable(True)
        self.setToolTip("Toggle pinned panel mode")
        self.setIconSize(QSize(iconSize, iconSize))
        self.setIcon(Krita.instance().icon('light_krita_tool_reference_images.svg'))
        self.setChecked(self.pinnedModeIsChecked())
        self.clicked.connect(self.togglePinnedMode)


    def pinnedModeIsChecked(self):
        if Application.readSetting("KanvasBuddy", "KBPinnedMode", "false") == "true":
            return True

        return False


    def togglePinnedMode(self, checked):        
        Application.writeSetting("KanvasBuddy", "KBPinnedMode", str(checked).lower())


class KBCloseButton(KBButton):

    def __init__(self, size, iconSize, parent=None):
        super(KBCloseButton, self).__init__(size, parent)
        self.setIconSize(QSize(iconSize, iconSize))
        self.setIcon(self.window().style().standardIcon(QStyle.SP_DockWidgetCloseButton))
        self.clicked.connect(self.window().close)