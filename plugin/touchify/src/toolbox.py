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

# CONTRIBUTORS:
# Kapyia @ https://krita-artists.org/
# halcyoen @ https://krita-artists.org/

import importlib

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ext.pykrita import *
else:
    from krita import *
from PyQt5.QtWidgets import *
from .docker.DockerRoot import *
from .variables import *

class TouchifyToolbox(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Touchify Toolbox")

        self.mainWidget = QWidget(self)
        self.setWidget(self.mainWidget)

        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        Krita.instance().notifier().windowCreated.connect(self.onLoaded)

        cfg: ConfigManager = ConfigManager.instance()
        cfg.notifyConnect(self.onConfigUpdated)
    
    def onLoaded(self):              
        self.panelStack = DockerRoot(self)
        self.layout.addWidget(self.panelStack)

    def onConfigUpdated(self):
        self.panelStack.dismantle()
        self.layout.removeWidget(self.panelStack)
        self.panelStack.deleteLater()
        self.panelStack = None

        self.panelStack = DockerRoot(self)
        self.layout.addWidget(self.panelStack)

    def canvasChanged(self, canvas):
        pass

# And add the extension to Krita's list of extensions:
Krita.instance().addDockWidgetFactory(DockWidgetFactory(TOUCHIFY_TOOLBOX_DOCKER_ID, DockWidgetFactoryBase.DockRight, TouchifyToolbox)) # type: ignore

