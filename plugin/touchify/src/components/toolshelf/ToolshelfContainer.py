from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from .buttons.ToolshelfPanelHeader import ToolshelfPanelHeader
from .buttons.ToolshelfActionBar import ToolshelfActionBar
from .pages.ToolshelfPage import ToolshelfPage
from ..DockerContainer import DockerContainer

from ...settings.TouchifyConfig import *
from ...variables import *
from ...docker_manager import *

from ...cfg.CfgToolshelf import CfgToolshelfPanel
from .pages.ToolshelfPageMain import ToolshelfPageMain
from .pages.ToolshelfPage import ToolshelfPage

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget


class ToolshelfContainer(QStackedWidget):

    def __init__(self, parent: "ToolshelfWidget", isPrimaryPanel: bool):
        super(ToolshelfContainer, self).__init__(parent)
        self.dockWidget = parent
        self._panels = {}
        self._pinned = False
        self._current_panel_id = 'MAIN'
        self._headers: List[ToolshelfPanelHeader] = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        qApp.focusObjectChanged.connect(self.handleFocusChange)

        self.isPrimaryPanel = isPrimaryPanel
        self.cfg = self.getCfg()
        super().currentChanged.connect(self.onCurrentChanged)

        self.addMainPanel()
        panels = self.cfg.panels
        for entry in panels:
            properties: CfgToolshelfPanel = entry
            PANEL_ID = properties.id
            panel_title = properties.id
            self.addPanel(PANEL_ID, properties)
            self._mainWidget.addDockerButton(properties, self.panel(PANEL_ID).activate, panel_title)
        self.changePanel('MAIN')

    def getCfg(self):
        cfg = TouchifyConfig.instance().getJSON()
        if self.isPrimaryPanel: return cfg.toolshelf_main
        else: return cfg.toolshelf_alt

    def addMainPanel(self):
        self._mainWidget = ToolshelfPageMain(self, self.isPrimaryPanel)
        self._panels['MAIN'] = self._mainWidget
        header = ToolshelfPanelHeader(self.cfg, True, self)
        self._headers.append(header)
        self._mainWidget.shelfLayout.insertWidget(0, header)
        super().addWidget(self._mainWidget)

    def addPanel(self, ID, data):
        panel = ToolshelfPage(self, ID, data)
        header = ToolshelfPanelHeader(self.cfg, False, self)

        panel.shelfLayout.insertWidget(0, header)
        self._headers.append(header)
        
        self._panels[ID] = panel
        super().addWidget(panel)


    def resizeEvent(self, event: QResizeEvent):
        self.dockWidget.onSizeChanged()
        super().resizeEvent(event)

    def goHome(self):
        self.changePanel('MAIN')

    def isPinned(self):
        return self._pinned

    def setPinned(self, value):
        self._pinned = not self._pinned
        for header in self._headers:
            header.pinButton.setChecked(self._pinned)

    def togglePinned(self):
        self._pinned = not self._pinned
        for header in self._headers:
            header.pinButton.setChecked(self._pinned)

    def changePanel(self, panel_id: str):
        new_panel = self.panel(panel_id)
        old_panel = self.panel(self._current_panel_id)

        old_panel.unloadPage()
        self._current_panel_id = panel_id
        new_panel.loadPage()
        self.setCurrentWidget(new_panel)
        self.onCurrentChanged(self.currentIndex())

    def onCurrentChanged(self, index):
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
        if name in self._panels:
            return self._panels[name]
        else:
            return None
    
    def shutdownWidget(self):
        qApp.focusObjectChanged.disconnect(self.handleFocusChange)
        super().currentChanged.disconnect(self.onCurrentChanged)

        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        children = self.findChildren(ToolshelfActionBar)
        for child in children:
            child.unregisterActions()

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