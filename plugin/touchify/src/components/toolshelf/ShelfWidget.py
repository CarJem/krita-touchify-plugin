from copy import deepcopy
from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.components.toolshelf.ShelfItem import ShelfItem
from touchify.src.components.toolshelf.ShelfItemOptions import ShelfItemOptions
from touchify.src.components.toolshelf.ShelfLoader import ShelfLoader

from touchify.src.components.toolshelf.ShelfTabBar import ShelfTabBar
from touchify.src.components.toolshelf.ShelfToolbar import ShelfToolbar
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer, ToolshelfSubState
from touchify.src.extensions.json_extensions import JsonExtensions
import touchify.src.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *

from typing import TYPE_CHECKING

from touchify.src.alib_pyqtgraph.dockarea.DockArea import DockArea
if TYPE_CHECKING:
    from .ShelfDockWidget import ShelfDockWidget, ShelfDockWidgetAlt
    from ..special.TouchifyPopup import TouchifyPopup
    from touchify.src.PluginManagers import TouchifyManagers
    from touchify.src.components.canvas.NtWidgetPad import NtWidgetPad

class ShelfWidget(QWidget):
    def __init__(self, parent, managers: "TouchifyManagers", registry_index: int = -3):
        super(ShelfWidget, self).__init__(parent)
        self.display: "ShelfDockWidget" | "ShelfDockWidgetAlt" | "TouchifyPopup" = parent
        self.managers = managers
        self.registry_index = registry_index

        self.hasPreloaded = False
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.dlg_settings: ShelfItemOptions | None = None
        self.containerOptions: ToolshelfSettings = ToolshelfSettings()

        self.api_window = self.managers.api_window()

        self.mainLayout = QGridLayout(self)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.mainLayout)

        self.header = ShelfToolbar(self)
        self.mainLayout.addWidget(self.header, 0, 0)

        self.tabBar = ShelfTabBar(self)
        self.tabBar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.mainLayout.addWidget(self.tabBar, 1, 0)

        self.dockPages: list[DockArea] = []
        self.dockLoader = ShelfLoader(self)
        self.dockStack = QStackedWidget(self)
        self.mainLayout.addWidget(self.dockStack, 2, 0)

        self.dockArea = DockArea(self)
        self.dockStack.addWidget(self.dockArea)

    #region Events

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

    def showEvent(self, event: QShowEvent):
        if self.hasPreloaded == False:
            self.loadShelves()
            self.hasPreloaded = True
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        super().hideEvent(event)

    #endregion
    
    #region Getters / Setters

    def isEditMode(self) -> bool:
        return self.header.optionsMenu.editModeAction.isChecked()

    def currentState(self) -> ToolshelfContainer:
        def getState(dock_area: DockArea):
            subState = ToolshelfSubState()
            subState.layout = dock_area.saveState()
        
            for uuid in dock_area.docks:
                dock = dock_area.docks[uuid]
                if isinstance(dock, ShelfItem):
                    dock: ShelfItem
                    subState.items[uuid] = dock.dock_settings
            return subState

        result = ToolshelfContainer()

        rootState = getState(self.dockArea)
        result.layout = rootState.layout
        result.items = rootState.items

        for dock_area in self.dockPages:
            subState = getState(dock_area)
            result.pages.append(subState)

        result.options = self.containerOptions

        return result

    #endregion

    #region Shelf Mgmt

    def __shelfDispose(self, dock_item: ShelfItem):
        dock_item.sigEditRequested.disconnect()
        dock_item.sigDeleteRequested.disconnect()
        dock_item.sigDuplicateRequested.disconnect()

    def __shelfSetup(self, dock_item: ShelfItem, uuid: str = None):
        if uuid != None: dock_item.setUUID(uuid)
        dock_item.setEditMode(self.isEditMode())
        dock_item.sigDuplicateRequested.connect(self.cloneShelf)
        dock_item.sigEditRequested.connect(self.editShelf)
        dock_item.sigDeleteRequested.connect(self.deleteShelf)

    #endregion

    #region Actions

    def insertPage(self):
        new_dock_area = DockArea(self)
        self.dockPages.append(new_dock_area)
        self.dockStack.addWidget(new_dock_area)
        
        self.saveShelves()
        self.loadShelves()

        self.goToPage(len(self.dockPages) - 1)

    def editPage(self, index: int):
        pass

    def deletePage(self, index: int):
        removed_dock_area = self.dockPages.pop(index)
        self.dockStack.removeWidget(removed_dock_area)
        
        for dock in removed_dock_area.docks.values():
            self.__shelfDispose(dock)
        
        removed_dock_area.clear()
        removed_dock_area.docks.clear()
        removed_dock_area.close()
        removed_dock_area.deleteLater()

        self.saveShelves()
        self.loadShelves()

    def insertShelf(self):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return
        
        if self.dlg_settings != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlg_settings) == False:
                return

        self.dlg_settings = ShelfItemOptions(self.api_window, ToolshelfDock())
        if self.dlg_settings.exec_():
            dock_item = self.dockLoader.Init_Section(self.dlg_settings.editableConfig)
            self.__shelfSetup(dock_item)
            current_area.addDock(dock_item)
            self.saveShelves()

    def cloneShelf(self, uuid: str):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return

        if uuid not in current_area.docks:
            return

        dock_item: ShelfItem = current_area.docks[uuid]   
        dock_settings = deepcopy(dock_item.dock_settings)

        dock_item = self.dockLoader.Init_Section(dock_settings)
        self.__shelfSetup(dock_item)
        current_area.addDock(dock_item)
        self.saveShelves()

    def editShelf(self, uuid: str):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfItem = current_area.docks[uuid]   
        self.dlg_settings = ShelfItemOptions(self.api_window, dock_item.dock_settings)

        if self.dlg_settings.exec_():
            lastState = current_area.saveState()
            self.__shelfDispose(dock_item)
            dock_item.close()

            dock_item = self.dockLoader.Init_Section(self.dlg_settings.editableConfig)
            self.__shelfSetup(dock_item, uuid)
            current_area.addDock(dock_item)
            current_area.restoreState(lastState)
            self.saveShelves()

    def deleteShelf(self, uuid: str):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfItem = current_area.docks[uuid]   
        
        #TODO: Add confirmation dialog
        confirmed = True

        if confirmed:
            self.__shelfDispose(dock_item)
            dock_item.close()
            del current_area.docks[uuid]
            self.saveShelves()

    def resetShelves(self):
        self.goToHomePage()

        for dock in self.dockArea.docks.values():
            self.__shelfDispose(dock)

        self.dockArea.clear()
        self.dockArea.docks.clear()

        for page in self.dockPages:
            for dock in page.docks.values():
                self.__shelfDispose(dock)
            
            page.clear()
            page.docks.clear()
            page.close()
            page.deleteLater()

        self.dockPages.clear()

    def saveShelves(self):
        KritaSettings.writeSetting("TOUCHIFY_TEMP", "TOUCHIFY_TOOLSHELF_DOCKER_CONFIGURATION_" + str(self.registry_index), JsonExtensions.saveClass(self.currentState()), False)

    def loadShelves(self):

        def loadShelf(sub_state: ToolshelfSubState | ToolshelfContainer, dock_area: DockArea):
            for uuid in sub_state.items:
                item = sub_state.items[uuid]
                dock_item = self.dockLoader.Init_Section(item)
                self.__shelfSetup(dock_item, uuid)
                dock_area.addDock(dock_item)
            
            if "main" in sub_state.layout:
                dock_area.restoreState(sub_state.layout)


        self.resetShelves()

        jsonStr = KritaSettings.readSetting("TOUCHIFY_TEMP", "TOUCHIFY_TOOLSHELF_DOCKER_CONFIGURATION_" + str(self.registry_index), "")
        with open( "/home/carjem/debug_toolshelf_load_"  + str(self.registry_index) + ".json", "w") as f:
            f.write(jsonStr)

        state: ToolshelfContainer = JsonExtensions.loadClass(jsonStr, ToolshelfContainer)
        self.containerOptions = state.options

        match self.containerOptions.position:
            case "top":
                self.mainLayout.addWidget(self.header, 0, 0)
                self.mainLayout.addWidget(self.tabBar, 1, 0)
                self.mainLayout.addWidget(self.dockStack, 2, 0)
            case "left":
                self.mainLayout.addWidget(self.header, 0, 0)
                self.mainLayout.addWidget(self.tabBar, 0, 1)
                self.mainLayout.addWidget(self.dockStack, 0, 2)
            case "right":
                self.mainLayout.addWidget(self.header, 0, 2)
                self.mainLayout.addWidget(self.tabBar, 0, 1)
                self.mainLayout.addWidget(self.dockStack, 0, 0)
            case _:
                self.mainLayout.addWidget(self.dockStack, 0, 0)
                self.mainLayout.addWidget(self.tabBar, 1, 0)
                self.mainLayout.addWidget(self.header, 2, 0)

        self.tabBar.reload(state)
        self.header.reload(state)

        loadShelf(state, self.dockArea)

        for subpage_state in state.pages:
            subpage_state: ToolshelfSubState
            sub_dock_area = DockArea(self)
            self.dockStack.addWidget(sub_dock_area)
            self.dockPages.append(sub_dock_area)
            loadShelf(subpage_state, sub_dock_area)


    def openShelfSettings(self):
        if self.dlg_settings != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlg_settings) == False:
                return
        
        self.dlg_settings = ShelfItemOptions(self.api_window, self.containerOptions)

        if self.dlg_settings.exec_():
            self.containerOptions = self.dlg_settings.editableConfig
            self.saveShelves()
            self.loadShelves()

    def goToHomePage(self):
        self.dockStack.setCurrentIndex(0)
        self.tabBar.onPageChanged("ROOT")
        self.header.onPageChanged(-1)

    def goToPage(self, index: int):
        if index < 0: return
        if index >= self.dockStack.count(): return

        self.dockStack.setCurrentIndex(index + 1)
        self.tabBar.onPageChanged("Tab_" + str(index))
        self.header.onPageChanged(index)

    #endregion

    #region Signals

    def onEditModeChanged(self, enabled: bool):
        def _recursive(da: DockArea):
            for uuid in da.docks:
                dock = da.docks[uuid]
                if isinstance(dock, ShelfItem):
                    dock: ShelfItem
                    dock.setEditMode(enabled)
        
        _recursive(self.dockArea)
        for dockArea in self.dockPages:
            _recursive(dockArea)
        
        
        self.saveShelves()

    #endregion