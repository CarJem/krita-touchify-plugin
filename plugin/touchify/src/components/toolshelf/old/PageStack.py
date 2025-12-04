from copy import deepcopy
from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.components.toolshelf.Page import Page
from touchify.src.components.special.DockerContainer import DockerContainer

from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *

from touchify.src.config.toolshelf.ToolshelfData import ToolshelfDataPage
from touchify.src.components.toolshelf.Page import Page

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget

class PageStack(QStackedWidget):

    dataLoaded = pyqtSignal()
    contentsChanged = pyqtSignal()
    contentsResized = pyqtSignal()

    def __init__(self, parent: "ToolshelfWidget", cfg: ToolshelfData):
        super(PageStack, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.container: "ToolshelfWidget"  = parent
        self._panels: dict[str, Page] = {}
        self._current_panel_id = 'ROOT'
        self.cfg = cfg

        self.total_jobs = 0
        self.completed_jobs = 0

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        super().currentChanged.connect(self.onCurrentChanged)
        
        self.addMainPanel()
        panels = self.cfg.pages
        for entry in panels:
            properties: ToolshelfDataPage = entry
            self.addPanel(properties)

        self.changePanel('ROOT')
        self.evaluateSize()


    def Data_OnWorkerComplete(self):
        self.completed_jobs += 1
        #print("Page: ", self.completed_jobs, " / ", self.total_jobs)
        if self.total_jobs == self.completed_jobs: self.dataLoaded.emit()

    def Data_AppendWorker(self, signal_handler: pyqtBoundSignal):
        self.total_jobs += 1
        signal_handler.connect(self.Data_OnWorkerComplete)

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
            #widget.adjustSize()
        #self.adjustSize()

        currentPage = self.currentWidget()
        currentPage.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        currentPage.setEnabled(True)
        currentPage.updateGeometry()
        #currentPage.adjustSize()
        #self.adjustSize()

    def addMainPanel(self):
        data = deepcopy(self.cfg.homepage)
        data.id = 'ROOT'
        self._mainWidget = Page(self, data)
        self.Data_AppendWorker(self._mainWidget.dataLoaded)
        self._mainWidget.Data_Load()
        self._mainWidget.panelItemUpdated.connect(self.onPanelItemUpdated)
        self._mainWidget.panelItemResized.connect(self.onPanelItemResized)
        #self._mainWidget.panel.sections_stack.setAutoFillBackground(False)
        self._panels['ROOT'] = self._mainWidget
        super().addWidget(self._mainWidget)

    def addPanel(self, data: ToolshelfDataPage):
        panel = Page(self, data)
        self.Data_AppendWorker(self._mainWidget.dataLoaded)
        panel.panelItemUpdated.connect(self.onPanelItemUpdated)
        panel.panelItemResized.connect(self.onPanelItemResized)
        self._panels[data.id] = panel
        super().addWidget(panel)
        panel.Data_Load()

    def goHome(self):
        self.changePanel('ROOT')
    
    def onPanelItemUpdated(self):
        self.contentsChanged.emit()

    def onPanelItemResized(self):
        self.contentsResized.emit()

    def changePanel(self, panel_id: str):
        new_panel = self.panel(panel_id)
        old_panel = self.panel(self._current_panel_id)

        if new_panel != old_panel:
            old_panel.unloadPage()
            self._current_panel_id = panel_id
            new_panel.loadPage()
            self.setCurrentWidget(new_panel)
        self.container.onPageChanged(panel_id)

    def onCurrentChanged(self, index):
        for i in range(0, self.count()):

            widget = self.widget(i)
            if i == index:
                policy = QSizePolicy.Policy.Preferred
                widget.setSizePolicy(policy, policy)
                widget.setEnabled(True)
                widget.updateGeometry()
                #widget.adjustSize()
            else:
                policy = QSizePolicy.Policy.Ignored
                widget.setSizePolicy(policy, policy)
                widget.setDisabled(False)
                widget.updateGeometry()
                #widget.adjustSize()

        #self.adjustSize()

    def panel(self, name) -> Page:
        if name in self._panels:
            return self._panels[name]
        else:
            return None
        
    def deactivateWidget(self):
        pass

    def activateWidget(self):
        pass
    
    def shutdownWidget(self):
        super().currentChanged.disconnect(self.onCurrentChanged)

        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        for panel_id in self._panels:
            self._panels[panel_id].close()