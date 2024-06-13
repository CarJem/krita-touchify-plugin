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

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...core.ext.PyKrita import *
else:
    from krita import *
from .kbbutton import KBButton

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt

class KBButtonBar(QWidget):

    def __init__(self, btnSize, parent=None):
        super(KBButtonBar, self).__init__(parent)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._buttons = {}
        self.btnSize = btnSize


    def addButton(self, properties, onClick, toolTip="", checkable=False):
        btn = KBButton(self.btnSize)
        btn.setIcon(Application.icon(properties['icon']))
        btn.clicked.connect(onClick) # collect and disconnect all when closing
        btn.setToolTip(toolTip)
        btn.setCheckable(checkable)

        self._buttons[properties['id']] = btn
        self.layout().addWidget(btn)


    def setButtonSize(self, size):
        self.btnSize = size
        for btn in self._buttons:
            btn.setFixedSize(QSize(size, size))


    def count(self):
        return len(self._buttons)


    def button(self, ID):
        return self._buttons[ID]