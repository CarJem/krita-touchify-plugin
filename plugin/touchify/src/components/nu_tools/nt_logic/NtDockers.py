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

from krita import Window

from ...toolshelf.ToolshelfWidget import ToolshelfWidget

from ...toolshelf.ToolshelfWidget import ToolshelfContainer
from .Nt_AdjustToSubwindowFilter import Nt_AdjustToSubwindowFilter
from .NtWidgetPad import NtWidgetPad
from .... import stylesheet
from ....variables import *

class NtDockers():

    def __init__(self, window: Window, alignment: str, enableToolOptions: bool = False):
        self.qWin = window.qwindow()
        self.mdiArea = self.qWin.findChild(QMdiArea)

        self.toolshelf = ToolshelfWidget(enableToolOptions)

        # Create "pad"
        self.pad = NtWidgetPad(self.mdiArea)
        self.pad.setObjectName("toolOptionsPad")
        self.pad.setViewAlignment(alignment)
        self.pad.borrowDocker(self.toolshelf)

        # Create and install event filter
        self.adjustFilter = Nt_AdjustToSubwindowFilter(self.mdiArea)
        self.adjustFilter.setTargetWidget(self.pad)
        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)
        self.qWin.installEventFilter(self.adjustFilter)

        # Create visibility toggle action 
        action_id = TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS if enableToolOptions else TOUCHIFY_ID_ACTION_SHOW_TOOL_OPTIONS_ALT
        action_name = "Show Tool Options Shelf" if enableToolOptions else "Show Toolbox Shelf"
        action = window.createAction(action_id, action_name, KRITA_ID_MENU_SETTINGS)
        action.toggled.connect(self.pad.toggleWidgetVisible)
        action.setCheckable(True)
        action.setChecked(True)

    def onSubWindowActivated(self, subWin):
        if subWin:
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
        self.toolshelf.updateStyleSheet()
        return
    
    def close(self):
        self.mdiArea.subWindowActivated.disconnect(self.onSubWindowActivated)
        self.qWin.removeEventFilter(self.adjustFilter)
        self.toolshelf.onUnload()
        self.pad.widget = None
        self.pad.widgetDocker = None
        #self.dockerAction.setEnabled(True)
        return self.pad.close()