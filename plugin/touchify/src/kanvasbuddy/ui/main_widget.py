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
    from ...ext.PyKrita import *
else:
    from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QMargins

from .kbbuttonbar import KBButtonBar
from .kbconfigmanager import KBConfigManager

class KBMainWidget(QWidget):
    _config = KBConfigManager()
    _dockerButtonSize = int(_config.loadConfig('SIZES')['dockerButtons'])
    _quickActionButtonSize = int(_config.loadConfig('SIZES')['actionButtons'])
    _margins = QMargins(4, 4, 4, 4)

    def __init__(self, parent=None):
        super(KBMainWidget, self).__init__(parent)
        self._config = KBConfigManager()
        self.setAutoFillBackground(True)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(self._margins)

        self.dockerBtns = KBButtonBar(self._dockerButtonSize)
        self.layout().addWidget(self.dockerBtns)    

        self.quickActions = KBButtonBar(self._quickActionButtonSize)
        self.initQuickActions()
        self.layout().addWidget(self.quickActions)


    def addDockerButton(self, properties, onClick, title):
        self.dockerBtns.addButton(properties, onClick, title)


    def initQuickActions(self):
        cfg = self._config.loadConfig('ACTIONS')
        props = self._config.loadProperties('quickActions')
        for entry in cfg:
            if cfg.getboolean(entry):
                action = Application.action(props[entry]['id'])
                self.quickActions.addButton(
                    props[entry],
                    action.trigger,
                    action.toolTip(),
                    action.isCheckable()
                    )

                if action.isCheckable():
                    btn = self.quickActions.button(props[entry]['id'])
                    btn.setChecked(action.isChecked())



    def synchronizeSliders(self):
        self.propSliders.synchronizeSliders()