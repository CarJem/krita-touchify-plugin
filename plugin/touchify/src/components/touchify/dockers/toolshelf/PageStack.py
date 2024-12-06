from copy import deepcopy
from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.components.touchify.actions.TouchifyActionPanel import TouchifyActionPanel
from touchify.src.components.touchify.dockers.toolshelf.Page import Page
from touchify.src.components.touchify.special.DockerContainer import DockerContainer

from touchify.src.settings import *
from touchify.src.variables import *
from touchify.src.docker_manager import *

from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from touchify.src.components.touchify.dockers.toolshelf.Page import Page

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget

class PageStack(QStackedWidget):
    def __init__(self, parent: "ToolshelfWidget", cfg: CfgToolshelf):
        super(PageStack, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.rootWidget: "ToolshelfWidget"  = parent
        self._panels: dict[str, Page] = {}
        self._current_panel_id = 'ROOT'
        self.cfg = cfg

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        super().currentChanged.connect(self.onCurrentChanged)
        
        self.addMainPanel()
        panels = self.cfg.pages
        for entry in panels:
            properties: CfgToolshelfPanel = entry
            self.addPanel(properties)

        self.changePanel('ROOT')
        self.evaluateSize()

    def setEditMode(self, value: bool):
        for panel_id in self._panels:
            panel = self._panels[panel_id]
            panel.setEditMode(value)

    def evaluateSize(self):
        for i in range(0, self.count()):
            widget = self.widget(i)
            policy = QSizePolicy.Policy.Ignored
            widget.setSizePolicy(policy, policy)
            widget.setDisabled(False)
            widget.updateGeometry()
            widget.adjustSize()
        self.adjustSize()

        currentPage = self.currentWidget()
        currentPage.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        currentPage.setEnabled(True)
        currentPage.updateGeometry()
        currentPage.adjustSize()
        self.adjustSize()


    def addMainPanel(self):
        data = deepcopy(self.cfg.homepage)
        data.id = 'ROOT'
        self._mainWidget = Page(self, data)
        self._mainWidget.panel.sections_stack.setAutoFillBackground(False)
        self._panels['ROOT'] = self._mainWidget
        super().addWidget(self._mainWidget)

    def addPanel(self, data: CfgToolshelfPanel):
        panel = Page(self, data)
        self._panels[data.id] = panel
        super().addWidget(panel)

    def goHome(self):
        if self.currentWidget() != self._mainWidget:
            self.changePanel('ROOT')
    
    def onDockerUpdate(self):
        self.adjustSize()

    def changePanel(self, panel_id: str):
        new_panel = self.panel(panel_id)
        old_panel = self.panel(self._current_panel_id)


        old_panel.unloadPage()
        self._current_panel_id = panel_id
        new_panel.loadPage()
        self.setCurrentWidget(new_panel)
        self.rootWidget.onPageChanged(panel_id)

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

    def panel(self, name) -> Page:
        if name in self._panels:
            return self._panels[name]
        else:
            return None
        
    def deactivateWidget(self):
        children = self.findChildren(DockerContainer)
        for child in children:
            child.unloadWidget()

    def activateWidget(self):
        children = self.findChildren(DockerContainer)
        for child in children:
            child.loadWidget()
    
    def shutdownWidget(self):
        super().currentChanged.disconnect(self.onCurrentChanged)

        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        children = self.findChildren(TouchifyActionPanel)
        for child in children:
            child.unregisterActions()

        for panel_id in self._panels:
            self._panels[panel_id].close()
    
    def onKritaConfigUpdate(self):
        pass