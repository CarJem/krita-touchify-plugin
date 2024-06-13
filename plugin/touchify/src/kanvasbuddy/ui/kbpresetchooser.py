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
from PyQt5.QtCore import pyqtSignal

class KBPresetChooser(PresetChooser):
    presetChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(KBPresetChooser, self).__init__(parent)
        self.presetSelected.connect(self.brushPresetChanged)
        self.presetClicked.connect(self.brushPresetChanged)

    def brushPresetChanged(self, preset):
        Application.activeWindow().activeView().activateResource(
            self.currentPreset()
            )
        self.presetChanged.emit()