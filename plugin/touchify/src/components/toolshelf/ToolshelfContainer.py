from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.components.toolshelf.buttons.ToolboxPanelHeader import ToolboxPanelHeader
from .buttons.ToolshelfQuickActions import ToolshelfQuickActions
from .pages.ToolshelfPagePanel import ToolshelfPagePanel
from ..DockerContainer import DockerContainer

from ...config import *
from ...variables import *
from ...docker_manager import *

from ...cfg.CfgToolshelf import CfgToolboxPanel
from .pages.ToolshelfPageMain import ToolshelfPageMain
from .pages.ToolshelfPage import ToolshelfPage




class ToolshelfContainer(QStackedWidget):

    def __init__(self, parent=None, isPrimaryPanel: bool = False):
        super(ToolshelfContainer, self).__init__(parent)
        self._panels = {}
        self._pinned = False
        self._current_panel_id = 'MAIN'
        self._headers: List[ToolboxPanelHeader] = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        qApp.focusObjectChanged.connect(self.handleFocusChange)

        self.isPrimaryPanel = isPrimaryPanel
        self.cfg = self.getCfg()
        super().currentChanged.connect(self.currentChanged)

        self.addMainPanel()
        panels = self.cfg.panels
        for entry in panels:
            properties: CfgToolboxPanel = entry
            PANEL_ID = str(uuid.uuid4())
            panel_title = properties.id
            self.addPanel(PANEL_ID, properties)
            self._mainWidget.addDockerButton(properties, self.panel(PANEL_ID).activate, panel_title)
        self.changePanel('MAIN')

    def getCfg(self):
        cfg = ConfigManager.instance().getJSON()
        if self.isPrimaryPanel: return cfg.toolshelf_main
        else: return cfg.toolshelf_alt

    def addMainPanel(self):
        self._mainWidget = ToolshelfPageMain(self, self.isPrimaryPanel)
        self._panels['MAIN'] = self._mainWidget
        header = ToolboxPanelHeader(self.cfg, True, self)
        self._headers.append(header)
        self._mainWidget.shelfLayout.insertWidget(0, header)
        super().addWidget(self._mainWidget)

    def addPanel(self, ID, data):
        panel = ToolshelfPagePanel(self, ID, data)
        header = ToolboxPanelHeader(self.cfg, False, self)

        panel.shelfLayout.insertWidget(0, header)
        self._headers.append(header)
        
        self._panels[ID] = panel
        super().addWidget(panel)

    def goHome(self):
        self.changePanel('MAIN')

    def isPinned(self):
        return self._pinned

    def togglePinned(self):
        self._pinned = not self._pinned
        for header in self._headers:
            header.pinButton.setChecked(self._pinned)

    def changePanel(self, panel_id: any):
        new_panel = self.panel(panel_id)
        old_panel = self.panel(self._current_panel_id)

        old_panel.unloadPage()
        self._current_panel_id = panel_id
        new_panel.loadPage()
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

    def panel(self, name) -> ToolshelfPage:
        return self._panels[name]
    
    def shutdownWidget(self):
        qApp.focusObjectChanged.disconnect(self.handleFocusChange)
        super().currentChanged.disconnect(self.currentChanged)

        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        for header in self._headers:
            header.close()

        for panel_id in self._panels:
            self._panels[panel_id].close()

    def doesCanvasHaveFocus(self, source):
        if not isinstance(source, QOpenGLWidget): return False

        if source.metaObject().className() == "KisOpenGLCanvas2":
            return True
                
        return False
    
    def onKritaConfigUpdate(self):
        pass

    def handleFocusChange(self, source):
        if self.isPinned() == False and self.doesCanvasHaveFocus(source):
            self.goHome()

    def updateStyleSheet(self):
        if self._mainWidget:
            self._mainWidget.updateStyleSheet()
        for panel in self._panels:
            self._panels[panel].updateStyleSheet()
        for button in self._headers:
            button.updateStyleSheet()
        return