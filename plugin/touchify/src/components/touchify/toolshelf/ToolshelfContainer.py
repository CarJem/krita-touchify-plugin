from PyQt5.QtWidgets import QSizePolicy, QStackedWidget
import uuid
from krita import *
from PyQt5.QtWidgets import *

from krita import *
from .ToolshelfPanelHeader import ToolshelfPanelHeader
from ...touchify.actions.TouchifyActionPanel import TouchifyActionPanel
from .ToolshelfPage import ToolshelfPage
from ..core.DockerContainer import DockerContainer

from ....settings.TouchifyConfig import *
from ....variables import *
from ....docker_manager import *

from ....cfg.CfgToolshelf import CfgToolshelfPanel
from .ToolshelfPageMain import ToolshelfPageMain
from .ToolshelfPage import ToolshelfPage

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfWidget import ToolshelfWidget
    from ..dockers.TouchifyToolshelfDocker import TouchifyToolshelfDocker

class ToolshelfContainer(QStackedWidget):
    
    
    class MouseListener(QObject):
        mouseReleased = pyqtSignal()

        def __init__(self):
            super().__init__()

        def eventFilter(self, obj, event):
            if (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton) or \
            (event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton):
                self.mouseReleased.emit()
            return super().eventFilter(obj, event)

    def __init__(self, parent: "ToolshelfWidget", PanelIndex: int):
        super(ToolshelfContainer, self).__init__(parent)
        
        self.mouse_listener = ToolshelfContainer.MouseListener()
        
        self.dockWidget: "ToolshelfWidget" | "TouchifyToolshelfDocker"  = parent
        self._panels = {}
        self._pinned = False
        self._current_panel_id = 'MAIN'
        self._headers: List[ToolshelfPanelHeader] = []
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.PanelIndex = PanelIndex
        self.cfg = self.getCfg()
        QApplication.instance().installEventFilter(self.mouse_listener)
        self.mouse_listener.mouseReleased.connect(self.onMouseRelease)
        super().currentChanged.connect(self.onCurrentChanged)
        
        self.addMainPanel()
        panels = self.cfg.panels
        for entry in panels:
            properties: CfgToolshelfPanel = entry
            self.addPanel(properties.id, properties)

        self.changePanel('MAIN')
        
    def getCfg(self):
        cfg = TouchifyConfig.instance().getConfig()
        if self.PanelIndex == 0: return cfg.toolshelf_main
        elif self.PanelIndex == 1: return cfg.toolshelf_alt
        elif self.PanelIndex == 2: return cfg.toolshelf_docker
        else: return None

    def addMainPanel(self):
        self._mainWidget = ToolshelfPageMain(self, self.PanelIndex)
        self._panels['MAIN'] = self._mainWidget
        header = ToolshelfPanelHeader(self.cfg, True, self)
        self._headers.append(header)
        self._mainWidget.shelfLayout.insertWidget(0, header)
        super().addWidget(self._mainWidget)

    def addPanel(self, ID, data: CfgToolshelfPanel):
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
        QApplication.instance().removeEventFilter(self.mouse_listener)
        self.mouse_listener.mouseReleased.disconnect(self.onMouseRelease)

        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        children = self.findChildren(TouchifyActionPanel)
        for child in children:
            child.unregisterActions()

        for header in self._headers:
            header.close()

        for panel_id in self._panels:
            self._panels[panel_id].close()
    
    def onKritaConfigUpdate(self):
        pass

    def onMouseRelease(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
        
        if not isinstance(widget_under_cursor, QOpenGLWidget): return
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return
        
        if self.isPinned() == False:
            self.goHome()

    def updateStyleSheet(self):
        if self._mainWidget:
            self._mainWidget.updateStyleSheet()
        for panel in self._panels:
            self._panels[panel].updateStyleSheet()
        for button in self._headers:
            button.updateStyleSheet()
        return