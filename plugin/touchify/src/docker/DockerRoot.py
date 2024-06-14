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
    from ..ext.PyKrita import *
else:
    from krita import *

from PyQt5.QtWidgets import QPushButton, QStackedWidget, QSizePolicy
from PyQt5.QtCore import QSize, QEvent
from ..config import *
from .DockerPanel import DockerPanel
from .DockerMainPage import DockerMainPage
from ..borrow_manager import KBBorrowManager

class DockerRoot(QStackedWidget):

    def __init__(self, parent=None):
        super(DockerRoot, self).__init__(parent)
        super().currentChanged.connect(self.currentChanged)
        self._panels = {}
        self.shortcutConnections = []
        
        self._mainWidget = DockerMainPage()
        self.addPanel('MAIN', self._mainWidget)
        self.appendShortcutAction('MAIN')
        self.initPanels()


    def initPanels(self):
        configManager = KBConfigManager()
        panelConfig = configManager.loadConfig('DOCKERS')
        properties = configManager.loadProperties('dockers')
        for entry in panelConfig:
            if panelConfig.getboolean(entry):
                self.initPanel(properties[entry])


    def addPanel(self, ID, widget):
        panel = DockerPanel(ID, widget)

        if self.count() > 0:
            backButton = KBPanelCloseButton(lambda: self.setCurrentIndex(0))
            panel.layout().addWidget(backButton)

        self._panels[ID] = panel
        super().addWidget(panel)


    def initPanel(self, properties):
        ID = properties['id']
        title = KBBorrowManager.instance().dockerWindowTitle(ID)

        self.addPanel(ID, None)
        if properties['size']:
            self.panel(ID).setSizeHint(properties['size'])
            
        self._mainWidget.addDockerButton(properties, self.panel(ID).activate, title)
        self.appendShortcutAction(ID)


    def appendShortcutAction(self, ID):
        i = str(self.count() - 1)  #account for main panel
        name = "KBPanel" + i
        action = Krita.instance().activeWindow().createAction(name, "KanvasBuddy")
        self.shortcutConnections.append(
            action.triggered.connect(self.panel(ID).activate)
        )
        self.shortcutConnections.append(
            action.triggered.connect(lambda: self.activateWindow())
        )


    def currentChanged(self, index):
        for i in range(0, self.count()):
            policy = QSizePolicy.Ignored
            widget = self.widget(i)
            if i == index:
                policy = QSizePolicy.Policy.Expanding
                widget.setEnabled(True)
                if hasattr(widget, "loadDockers"):
                    widget.loadDockers()
            else:
                widget.setDisabled(False)
                if hasattr(widget, "unloadDockers"):
                    widget.unloadDockers()

            widget.setSizePolicy(policy, policy)
            widget.updateGeometry()



        self.adjustSize()
        self.parentWidget().adjustSize()
        

    def event(self, e):
        r = super().event(e) # Get the return value of the parent class' event method first
        pinned = KritaSettings.readSetting("KanvasBuddy", "KBPinnedMode", "false")

        if (e.type() == QEvent.WindowDeactivate and pinned == "false"):
            self.setCurrentIndex(0)
        
        return r
    
    
    def dismantle(self):
        for c in self.shortcutConnections:
            self.disconnect(c)


    def panel(self, name):
        return self._panels[name]


class KBPanelCloseButton(QPushButton):
    _config = KBConfigManager()
    _height = int(_config.loadConfig('SIZES')['dockerBack'])
    _iconSize = _height-2

    def __init__(self, onClick, parent=None):
        super(KBPanelCloseButton, self).__init__(parent)
        self.setIcon(Krita.instance().action('move_layer_up').icon())
        self.setIconSize(QSize(self._iconSize, self._iconSize))
        self.setFixedHeight(self._height)
        self.clicked.connect(onClick)