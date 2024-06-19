"""
    Plugin for Krita UI Redesign, Copyright (C) 2020 Kapyia, Pedro Reis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5.QtWidgets import QMdiArea, QDockWidget

from ..toolshelf.ToolshelfCore import ToolshelfCore

from ..toolshelf.ToolshelfRoot import ToolshelfRoot
from .nt_logic.Nt_AdjustToSubwindowFilter import NtToolboxWithShelfEventFilter
from .NtWidgetPad import NtWidgetPad
from ... import stylesheet
from ...variables import *

class NtDockers():

    def __init__(self, window, alignment: str, enableToolOptions: bool = False):
        qWin = window.qwindow()
        mdiArea = qWin.findChild(QMdiArea)

        self.toolshelf = ToolshelfCore(enableToolOptions)

        # Create "pad"
        self.pad = NtWidgetPad(mdiArea)
        self.pad.setObjectName("toolOptionsPadRight")
        self.pad.setViewAlignment(alignment)
        self.pad.borrowDocker(self.toolshelf)

        # Create and install event filter
        self.adjustFilter = NtToolboxWithShelfEventFilter(mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        mdiArea.subWindowActivated.connect(self.ensureFilterIsInstalled)
        qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action 
        action = window.createAction(TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS, "Show Tool Options", KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

    def ensureFilterIsInstalled(self, subWin):
        """Ensure that the current SubWindow has the filter installed,
        and immediately move the Toolbox to current View."""
        if subWin:
            subWin.installEventFilter(self.adjustFilter)
            self.pad.adjustToView()
            self.updateStyleSheet()
    

    def findDockerAction(self, window, text):
        dockerMenu = None
        
        for m in window.qwindow().actions():
            if m.objectName() == "settings_dockers_menu":
                dockerMenu = m

                for a in dockerMenu.menu().actions():
                    if a.text().replace('&', '') == text:
                        return a
                
        return False
    
    def onConfigUpdate(self):
        pass

    def onKritaConfigUpdate(self):
        pass


    def updateStyleSheet(self):
        #variables.setColors()
        #self.pad.setStyleSheet(variables.nu_tool_options_style)
        return
    
    def close(self):
        self.toolshelf.onUnload()
        self.pad.widget = None
        self.pad.widgetDocker = None
        #self.dockerAction.setEnabled(True)
        return self.pad.close()