

from ...cfg.CfgToolboxDocker import KB_Docker
from krita import *

from PyQt5.QtWidgets import QPushButton, QStackedWidget, QSizePolicy
from PyQt5.QtCore import QSize, QEvent
from ...config import *
from .ToolboxRoot import DockerPanel
from .ToolboxMainPage import DockerMainPage
from ...docker_manager import KBBorrowManager

class DockerRoot(QStackedWidget):

    def __init__(self, parent=None):
        super(DockerRoot, self).__init__(parent)
        super().currentChanged.connect(self.currentChanged)
        self._panels = {}
        self.shortcutConnections = []
        
        self._mainWidget = DockerMainPage()
        self.addPanel('MAIN', self._mainWidget)
        self.initPanels()

    def initPanels(self):
        configManager: ConfigManager = ConfigManager.instance()
        for entry in configManager.getJSON().kb_dockers:
            cfgDocker: KB_Docker = entry
            if cfgDocker.isEnabled:
                self.initPanel(cfgDocker)

    def addPanel(self, ID, widget):
        panel = DockerPanel(ID, widget)

        if self.count() > 0:
            backButton = KBPanelCloseButton(lambda: self.setCurrentIndex(0))
            panel.layout().addWidget(backButton)

        self._panels[ID] = panel
        super().addWidget(panel)


    def initPanel(self, properties: KB_Docker):
        ID = properties.id
        title = KBBorrowManager.instance().dockerWindowTitle(ID)

        self.addPanel(ID, None)
        if properties.nesting_mode == "docking":
            self.panel(ID).setDockMode(True)
        if properties.size_x != 0 and properties.size_y != 0:
            size = [properties.size_x, properties.size_y]
            self.panel(ID).setSizeHint(size)
            
        self._mainWidget.addDockerButton(properties, self.panel(ID).activate, title)


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
    
    def dismantle(self):
        for pnl in self._panels:
            panel: DockerPanel = self._panels[pnl]
            panel.unloadDockers()

        for c in self.shortcutConnections:
            self.disconnect(c)

        self._mainWidget.unloadDocker()

    def panel(self, name):
        return self._panels[name]


class KBPanelCloseButton(QPushButton):


    def __init__(self, onClick, parent=None):
        super(KBPanelCloseButton, self).__init__(parent)

        configManager: ConfigManager = ConfigManager.instance()
        self._height = configManager.getJSON().kb_dockerBackHeight
        self._iconSize = self._height - 2
        
        self.setIcon(Krita.instance().action('move_layer_up').icon())
        self.setIconSize(QSize(self._iconSize, self._iconSize))
        self.setFixedHeight(self._height)
        self.clicked.connect(onClick)