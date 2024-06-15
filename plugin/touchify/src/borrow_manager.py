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

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ext.PyKrita import *
else:
    from krita import *
from PyQt5.QtWidgets import QWidget
from .ext.extensions import *
from .config import *
from .docker.DockerPresetChooser import DockerPresetChooser
from .components.nu_tools.nt_logic.Nt_ScrollAreaContainer import Nt_ScrollAreaContainer

class KBBorrowManager():

    _widgetDocker = {}
    _actualDocker = {}
    _previousDockerState = {}

    def __init__(self):
        self._qWin = Krita.instance().activeWindow().qwindow()

    def widget(self, ID):
        return self._actualDocker[ID]
    
    def borrowDockerWidget(self, ID):
        return self.borrowDockerWidget(self, ID, False)

    def borrowDockerWidget(self, ID, dockMode=False):
        """
        Borrow a docker widget from Krita's existing list of dockers and 
        returns True. Returns False if invalid widget was passed."""
        docker = self._qWin.findChild(QDockWidget, ID)
        # Does requested widget exist?
        if isinstance(docker, QDockWidget) and docker.widget():

            self._previousDockerState[ID] = {
                "dockMode": dockMode,
                "previousVisibility": docker.isVisible(),
                "dockWidgetArea": self._qWin.dockWidgetArea(docker)
            }

            if dockMode:
                self._actualDocker[ID] = docker
                self._actualDocker[ID].show()
                self._actualDocker[ID].titleBarWidget().setVisible(False)
                return self._actualDocker[ID]
            else:
                self._widgetDocker[ID] = docker
                self._actualDocker[ID] = docker.widget()
                self._widgetDocker[ID].hide()
                return self._actualDocker[ID]
        return None
    
    def returnWidget(self, ID):
        """
        Return the borrowed docker to it's original QDockWidget"""
        # Ensure there's a widget to return
        if ID in self._actualDocker:
            if self._actualDocker[ID]:
                if self._previousDockerState[ID]["dockMode"]:
                    self._qWin.addDockWidget(self._previousDockerState[ID]["dockWidgetArea"], self._actualDocker[ID])
                    titlebarSetting = KritaSettings.readSetting("", "showDockerTitleBars", "false")
                    showTitlebar = True if titlebarSetting == "true" else False
                    self._actualDocker[ID].titleBarWidget().setVisible(showTitlebar)
                    if self._previousDockerState[ID]["previousVisibility"] == False:
                        self._actualDocker[ID].hide()
                else:
                    self._widgetDocker[ID].setWidget(self._actualDocker[ID])
                    if self._previousDockerState[ID]["previousVisibility"] == True:
                        self._widgetDocker[ID].show()
                self._previousDockerState[ID] = None
                self._actualDocker[ID] = None
                self._widgetDocker[ID] = None

    def returnAll(self):
        for ID in self._widgetDocker:
            self.returnWidget(ID)

    def dockerWindowTitle(self, ID):
        title = self._qWin.findChild(QWidget, ID).windowTitle()
        return title.replace('&', '')
    
    def instance():
        if KBBorrowManager.root == None:
            KBBorrowManager.root = KBBorrowManager()
        return KBBorrowManager.root
    
KBBorrowManager.root = None