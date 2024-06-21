from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from .ToolshelfPagePanel import ToolshelfPagePanel

from ...config import *
from ...variables import *
from ...docker_manager import *
from ... import stylesheet

from ...cfg.CfgToolshelf import CfgToolboxPanel
from .ToolshelfPageMain import ToolshelfPageMain
from .ToolshelfPageHost import ToolshelfPageHost


HAS_KRITA_FULLY_LOADED = False

def ON_KRITA_WINDOW_CREATED():
    global HAS_KRITA_FULLY_LOADED
    HAS_KRITA_FULLY_LOADED = True

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

    def updateStyleSheet(self):
        self.setStyleSheet(stylesheet.nu_tool_options_back_button_style)
        return

class ToolshelfContainer(QStackedWidget):

    def __init__(self, parent=None, enableToolOptions: bool = False):
        super(ToolshelfContainer, self).__init__(parent)
        self._panels = {}
        self.shortcutConnections = []
        self.current_panel_id = 'MAIN'
        self._backButtons: List[ToolboxPanelCloseButton] = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.cfg = self.getCfg(enableToolOptions)
        super().currentChanged.connect(self.currentChanged)

        self.addMainPanel(enableToolOptions)
        panels = self.cfg.panels
        for entry in panels:
            properties: CfgToolboxPanel = entry
            if properties.isEnabled:
                PANEL_ID = str(uuid.uuid4())
                panel_title = properties.id
                self.addPanel(PANEL_ID, properties)
                self._mainWidget.addDockerButton(properties, self.panel(PANEL_ID).activate, panel_title)
        self.changePanel('MAIN')

    def getCfg(self, enableToolOptions: bool = False):
        cfg = ConfigManager.instance().getJSON()
        if enableToolOptions: return cfg.toolshelf_main
        else: return cfg.toolshelf_alt

    def addMainPanel(self, enableToolOptions: bool = False):
        self._mainWidget = ToolshelfPageMain(self, enableToolOptions)
        self._panels['MAIN'] = self._mainWidget
        super().addWidget(self._mainWidget)

    def addPanel(self, ID, data):
        panel = ToolshelfPagePanel(self, ID, data)
        backButton = ToolboxPanelCloseButton(self.goHome, self.cfg)
        panel.layout().addWidget(backButton)
        self._backButtons.append(backButton)
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
        self.currentChanged(self.currentIndex())

    def currentChanged(self, index):
        for i in range(0, self.count()):

            widget = self.widget(i)
            if i == index:
                policy = QSizePolicy.Policy.Preferred
                widget.setSizePolicy(policy, policy)
                widget.setEnabled(True)
                widget.updateGeometry()
                widget.adjustSize()
            else:
                policy = QSizePolicy.Policy.Ignored
                widget.setSizePolicy(policy, policy)
                widget.setDisabled(False)
                widget.updateGeometry()
                widget.adjustSize()

        self.adjustSize()

    def dismantle(self):
        self.changePanel('MAIN')

        for pnl in self._panels:
            panel: ToolshelfPageHost = self._panels[pnl]
            panel.unloadDockers()

        for c in self.shortcutConnections:
            self.disconnect(c)

    def panel(self, name) -> ToolshelfPageHost:
        return self._panels[name]


    def updateStyleSheet(self):
        if self._mainWidget:
            self._mainWidget.updateStyleSheet()
        for button in self._backButtons:
            button.updateStyleSheet()
        return

class ToolshelfWidget(QDockWidget):

    def __init__(self, enableToolOptions: bool = False):
        super().__init__()
        self.setWindowTitle("Touchify Toolshelf")

        self.enableToolOptions = enableToolOptions

        stylesheet = f"""QScrollArea {{ background: transparent; }}
        QScrollArea > QWidget > ToolshelfContainer {{ background: transparent; }}
        """

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(stylesheet)
        self.setWidget(self.scrollArea)

        if HAS_KRITA_FULLY_LOADED:
            self.onLoaded()
        else:
            Krita.instance().notifier().windowCreated.connect(self.onLoaded)

    def hasPanelStack(self):
        if hasattr(self, "panelStack"):
            if self.panelStack:
                return True
        return False
    
    #def sizeHint(self):
        #if self.hasPanelStack():
            #return self.panelStack.sizeHint()
        #else: return super().sizeHint() 

    def updateStyleSheet(self):
        if self.hasPanelStack():
            self.panelStack.updateStyleSheet()

    def onKritaConfigUpdate(self):
        if self.hasPanelStack():
            self.panelStack._mainWidget.onKritaConfigUpdate()
    
    def onLoaded(self):              
        self.panelStack = ToolshelfContainer(self, self.enableToolOptions)
        self.panelStack.updateStyleSheet()
        self.scrollArea.setWidget(self.panelStack)

    def onUnload(self):
        self.panelStack.dismantle()
        self.scrollArea.takeWidget()
        self.panelStack.deleteLater()
        self.panelStack = None

    def onConfigUpdated(self):
        self.onUnload()
        self.onLoaded()


Krita.instance().notifier().windowCreated.connect(ON_KRITA_WINDOW_CREATED)