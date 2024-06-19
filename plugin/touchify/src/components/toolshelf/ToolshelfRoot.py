

import uuid
from ...cfg.CfgToolboxPanel import CfgToolboxPanel
from krita import *

from PyQt5.QtWidgets import QPushButton, QStackedWidget, QSizePolicy
from PyQt5.QtCore import QSize, QEvent
from ...config import *
from .ToolshelfPanelHost import ToolshelfPanelHost
from .ToolshelfMainPage import ToolshelfMainPage
from ...docker_manager import DockerManager

class ToolshelfRoot(QStackedWidget):

    def __init__(self, parent=None, enableToolOptions: bool = False):
        super(ToolshelfRoot, self).__init__(parent)
        self._panels = {}
        self.shortcutConnections = []
        self.current_panel_id = 'MAIN'
        
        self.cfg = self.getCfg(enableToolOptions)
        super().currentChanged.connect(self.currentChanged)
        
        self._mainWidget = ToolshelfMainPage(self, enableToolOptions)
        self.addPanel('MAIN', True, self._mainWidget)

        panels = self.cfg.panels

        for entry in panels:
            properties: CfgToolboxPanel = entry
            if properties.isEnabled:
                PANEL_ID = str(uuid.uuid4())
                panel_title = properties.id
                self.addPanel(PANEL_ID, False, properties)    
                self._mainWidget.addDockerButton(properties, self.panel(PANEL_ID).activate, panel_title)
        self.changePanel('MAIN')
        self.currentChanged(self.currentIndex())

    def getCfg(self, enableToolOptions: bool = False):
        cfg = ConfigManager.instance().getJSON()
        if enableToolOptions: return cfg.toolshelf_main
        else: return cfg.toolshelf_alt

    def addPanel(self, ID, isPanelMode, data):
        panel = ToolshelfPanelHost(self, ID, isPanelMode, data)
        if self.count() > 0:
            backButton = ToolboxPanelCloseButton(self.goHome, self.cfg)
            panel.layout().addWidget(backButton)
        self._panels[ID] = panel
        super().addWidget(panel)

    def goHome(self):
        self.changePanel('MAIN')

    def changePanel(self, panel_id: any):
        new_panel = self.panel(panel_id)
        old_panel = self.panel(self.current_panel_id)

        old_panel.unloadDockers()
        self.current_panel_id = panel_id
        new_panel.loadDockers()
        self.setCurrentWidget(new_panel)

    def currentChanged(self, index):
        for i in range(0, self.count()):
            policy = QSizePolicy.Ignored
            widget = self.widget(i)
            if i == index:
                policy = QSizePolicy.Policy.Expanding
                widget.setEnabled(True)
            else:
                policy = QSizePolicy.Policy.Ignored
                widget.setDisabled(False)

            widget.setSizePolicy(policy, policy)
            widget.updateGeometry()

        self.adjustSize()
        self.parentWidget().adjustSize()
    
    def dismantle(self):
        self.changePanel('MAIN')

        for pnl in self._panels:
            panel: ToolshelfPanelHost = self._panels[pnl]
            panel.unloadDockers()

        for c in self.shortcutConnections:
            self.disconnect(c)

    def panel(self, name) -> ToolshelfPanelHost:
        return self._panels[name]


class ToolboxPanelCloseButton(QPushButton):


    def __init__(self, onClick, cfg: CfgToolshelf, parent=None):
        super(ToolboxPanelCloseButton, self).__init__(parent)

        configManager: ConfigManager = ConfigManager.instance()
        self._height = cfg.dockerBackHeight
        self._iconSize = self._height - 2
        
        self.setIcon(Krita.instance().action('move_layer_up').icon())
        self.setIconSize(QSize(self._iconSize, self._iconSize))
        self.setFixedHeight(self._height)
        self.clicked.connect(onClick)