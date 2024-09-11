from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from ...actions.TouchifyActionPanel import TouchifyActionPanel
from .ToolshelfPage import ToolshelfPage
from ...special.DockerContainer import DockerContainer

from .....settings.TouchifyConfig import *
from .....variables import *
from .....docker_manager import *

from .....cfg.toolshelf.CfgToolshelf import CfgToolshelfPanel
from .ToolshelfPageMain import ToolshelfPageMain
from .ToolshelfPage import ToolshelfPage
from .extras.MouseListener import MouseListener

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget

class ToolshelfPageStack(QStackedWidget):
    def __init__(self, parent: "ToolshelfWidget", cfg: CfgToolshelf):
        super(ToolshelfPageStack, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.rootWidget: "ToolshelfWidget"  = parent
        self._panels = {}
        self._current_panel_id = 'ROOT'
        self.cfg = cfg

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        super().currentChanged.connect(self.onCurrentChanged)
        
        self.addMainPanel()
        panels = self.cfg.panels
        for entry in panels:
            properties: CfgToolshelfPanel = entry
            self.addPanel(properties.id, properties)

        self.changePanel('ROOT')

    def addMainPanel(self):
        self._mainWidget = ToolshelfPageMain(self, self.cfg)
        self._panels['ROOT'] = self._mainWidget
        super().addWidget(self._mainWidget)

    def addPanel(self, ID, data: CfgToolshelfPanel):
        panel = ToolshelfPage(self, ID, data)
        self._panels[ID] = panel
        super().addWidget(panel)

    def resizeEvent(self, event: QResizeEvent):
        self.rootWidget.onSizeChanged()
        super().resizeEvent(event)

    def goHome(self):
        if self.currentWidget() != self._mainWidget:
            self.changePanel('ROOT')

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

    def panel(self, name) -> ToolshelfPage:
        if name in self._panels:
            return self._panels[name]
        else:
            return None
    
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