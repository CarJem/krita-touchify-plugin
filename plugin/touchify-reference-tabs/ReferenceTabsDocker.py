# Reference Tabs
# Copyright (C) 2022 Freya Lupen <penguinflyer2222@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from krita import Krita, DockWidget, DockWidgetFactory, DockWidgetFactoryBase


from .ReferenceTabsWidget import ReferenceTabsWidget

# constant string for the config group in kritarc
PLUGIN_CONFIG = "Touchify/ReferenceTabsDocker"


class ReferenceTabsDocker(DockWidget):

    def __init__(self):
        super().__init__()

        widget = ReferenceTabsWidget()

        # Load config from kritarc
        widget.currentFolder = Krita.instance().readSetting(PLUGIN_CONFIG, "currentFolder", "")
        widget.currentFolderChanged.connect(writeCurrentFolderToConfig)

        self.setWindowTitle("Touchify Addon: Reference Tabs")
        self.setWidget(widget)

    # This override is required.
    def canvasChanged(self, canvas):
        pass

def writeCurrentFolderToConfig(currentFolder):
    Krita.instance().writeSetting(PLUGIN_CONFIG, "currentFolder", currentFolder)

Krita.instance().addDockWidgetFactory(DockWidgetFactory(PLUGIN_CONFIG, DockWidgetFactoryBase.DockPosition.DockRight, ReferenceTabsDocker))

