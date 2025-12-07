from copy import deepcopy
from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.components.toolshelf.ShelfItem import ShelfItem
from touchify.src.components.toolshelf.ShelfOptionsDialog import ShelfOptionsDialog
from touchify.src.components.toolshelf.ShelfLoader import ShelfLoader

from touchify.src.components.toolshelf.ShelfTabBar import ShelfTabBar
from touchify.src.components.toolshelf.ShelfToolbar import ShelfToolbar
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.config.toolshelf.ToolshelfPage import ToolshelfPage
from touchify.src.extensions.json_extensions import JsonExtensions
import touchify.src.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *

from typing import TYPE_CHECKING, Any

from touchify.src.alib_pyqtgraph.dockarea.DockArea import DockArea
if TYPE_CHECKING:
    from .ShelfDockWidget import ShelfDockWidget, ShelfDockWidgetAlt
    from ..popup.PopupWidget import PopupWidget
    from touchify.src.PluginManagers import TouchifyManagers

class ShelfWidget(QWidget):
    sigShelfIndexChanged = QtCore.pyqtSignal()

    def __init__(self, parent, managers: "TouchifyManagers", registry_index: int = 0, enforced_data: ToolshelfContainer = None):
        super(ShelfWidget, self).__init__(parent)
        self.display: "ShelfDockWidget" | "PopupWidget" = parent
        self.managers = managers
        self.registry_index = registry_index


        if enforced_data != None:
            self.constant_data = enforced_data
            self.is_restricted = True
        else:
            self.constant_data = None
            self.is_restricted = False

        self.hasPreloaded = False


        self._allowAutoSave = True
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.dlgConfigEditor: ShelfOptionsDialog | None = None
        self.containerOptions: ToolshelfSettings = ToolshelfSettings()
        self.homepageOptions: ToolshelfPageSettings = ToolshelfPageSettings()

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
        self.dockPageOptions: list[ToolshelfPageSettings] = []

        self.dockLoader = ShelfLoader(self)
        self.dockStack = ShelfWidgetStack(self)
        self.mainLayout.addWidget(self.dockStack, 2, 0)

        self.dockArea = DockArea(self)
        self.dockStack.addWidget(self.dockArea)

        self.updateStyle()

    def __setupDialog(self, options: Any):
        if self.dlgConfigEditor != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlgConfigEditor) == False:
                return None
        
        self.dlgConfigEditor = ShelfOptionsDialog(self.api_window, options)
        return self.dlgConfigEditor

    def updateStyle(self):
        self.dockStack.setStyleSheet(f"""
            ShelfWidgetStack {{
                border: 1px solid palette(base)  
            }}
        """)


    #region Events

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

    def showEvent(self, event: QShowEvent):
        if self.hasPreloaded == False:
            self.loadLayout()
            self.hasPreloaded = True
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        super().hideEvent(event)

    #endregion
    
    #region Getters / Setters

    def isEditMode(self) -> bool:
        return self.header.optionsMenu.editModeAction.isChecked()
    
    def isAutoSaveEnabled(self) -> bool:
        return self._allowAutoSave

    def currentPresetId(self) -> str:
        return TouchifySettings.instance().getActiveShelfId(self.registry_index)

    def currentState(self) -> ToolshelfContainer:
        def getState(dock_area: DockArea):
            subState = ToolshelfPage()
            subState.layout = dock_area.saveState()
        
            for uuid in dock_area.docks:
                dock = dock_area.docks[uuid]
                if isinstance(dock, ShelfItem):
                    dock: ShelfItem
                    subState.items[uuid] = dock.dock_settings
            return subState

        result = ToolshelfContainer()

        rootState: ToolshelfContainer = getState(self.dockArea)
        result.layout = rootState.layout
        result.items = rootState.items

        for idx, dock_area in enumerate(self.dockPages):
            subState: ToolshelfPage = getState(dock_area)
            subState.options = self.dockPageOptions[idx]
            result.pages.append(subState)

        result.options = self.containerOptions
        result.pageOptions = self.homepageOptions

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
        dock_item.sigDuplicateRequested.connect(self.cloneShelfItem)
        dock_item.sigEditRequested.connect(self.editShelfItem)
        dock_item.sigDeleteRequested.connect(self.deleteShelfItem)

    #endregion

    #region Actions (ShelfLayout)

    def resetLayout(self, noSave: bool = True):
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


        self.containerOptions = ToolshelfSettings()

        self.dockPages.clear()
        self.dockPageOptions.clear()

        if not noSave:
            self.saveLayout()
            self.loadLayout()

    def saveLayout(self):
        if self.is_restricted: 
            return

        state = JsonExtensions.saveClass(self.currentState())
        if self.currentPresetId().lower() != "none":
            if self.isAutoSaveEnabled(): self.savePreset(True)
        else:
            KritaSettings.writeSetting("TOUCHIFY_TEMP", "TOUCHIFY_TOOLSHELF_DOCKER_CONFIGURATION_" + str(self.registry_index), state, False)

    def loadLayout(self):
        def loadShelf(sub_state: ToolshelfPage | ToolshelfContainer, dock_area: DockArea):
            for uuid in sub_state.items:
                item = sub_state.items[uuid]
                dock_item = self.dockLoader.Init_Section(item)
                self.__shelfSetup(dock_item, uuid)
                dock_area.addDock(dock_item)
            
            if "main" in sub_state.layout:
                dock_area.restoreState(sub_state.layout)


        self.resetLayout()
        state: ToolshelfContainer



        if self.is_restricted:
            state: ToolshelfContainer = deepcopy(self.constant_data)
        elif self.currentPresetId().lower() != "none":
            state: ToolshelfContainer = TouchifySettings.instance().getActiveShelf(self.registry_index).preset_data
        else:
            jsonStr = KritaSettings.readSetting("TOUCHIFY_TEMP", "TOUCHIFY_TOOLSHELF_DOCKER_CONFIGURATION_" + str(self.registry_index), "")
            state: ToolshelfContainer = JsonExtensions.loadClass(jsonStr, ToolshelfContainer)

        if state == None:
            return

        self.containerOptions: ToolshelfSettings = state.options
        self.homepageOptions: ToolshelfPageSettings = state.pageOptions

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

        loadShelf(state, self.dockArea)

        for subpage_state in state.pages:
            subpage_state: ToolshelfPage
            sub_dock_area = DockArea(self)
            self.dockStack.addWidget(sub_dock_area)
            self.dockPages.append(sub_dock_area)
            self.dockPageOptions.append(subpage_state.options)
            loadShelf(subpage_state, sub_dock_area)

        self.tabBar.reload(state)
        self.header.reload(state, self.currentPresetId())

        self.display.shelfReloadEvent(state)

    def editLayout(self):
        dlg = self.__setupDialog(self.containerOptions)
        if dlg.exec_():
            self.containerOptions = dlg.editableConfig
            self.saveLayout()
            self.loadLayout()

    #endregion

    #region Actions (ShelfPages)

    def insertPage(self):
        new_dock_area = DockArea(self)
        self.dockPages.append(new_dock_area)
        self.dockStack.addWidget(new_dock_area)
        
        self.saveLayout()
        self.loadLayout()

        self.goToPage(len(self.dockPages) - 1)

    def editPage(self, index: int):
        if index == -1:
            pageData = self.homepageOptions
        else:
            pageData = self.dockPageOptions[index]

        dlg = self.__setupDialog(pageData)
        if dlg.exec_():
            if index == -1: self.homepageOptions = dlg.editableConfig
            else: self.dockPageOptions[index] = dlg.editableConfig

            self.saveLayout()
            self.loadLayout()

    def deletePage(self, index: int):
        removed_dock_area = self.dockPages.pop(index)
        self.dockStack.removeWidget(removed_dock_area)
        
        for dock in removed_dock_area.docks.values():
            self.__shelfDispose(dock)
        
        removed_dock_area.clear()
        removed_dock_area.docks.clear()
        removed_dock_area.close()
        removed_dock_area.deleteLater()

        self.saveLayout()
        self.loadLayout()

    #endregion

    #region Actions (ShelfItems)

    def insertShelfItem(self):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return

        dlg = self.__setupDialog(ToolshelfDock())
        if dlg.exec_():
            dock_item = self.dockLoader.Init_Section(dlg.editableConfig)
            self.__shelfSetup(dock_item)
            current_area.addDock(dock_item)
            self.saveLayout()

    def cloneShelfItem(self, uuid: str):
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
        self.saveLayout()

    def editShelfItem(self, uuid: str):
        current_area: DockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, DockArea):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfItem = current_area.docks[uuid]   
        
        dlg = self.__setupDialog(dock_item.dock_settings)
        if dlg.exec_():
            lastState = current_area.saveState()
            self.__shelfDispose(dock_item)
            dock_item.close()

            dock_item = self.dockLoader.Init_Section(dlg.editableConfig)
            self.__shelfSetup(dock_item, uuid)
            current_area.addDock(dock_item)
            current_area.restoreState(lastState)
            self.saveLayout()

    def deleteShelfItem(self, uuid: str):
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
            self.saveLayout()

    #endregion

    #region Actions (Presets)

    def changePreset(self, id: str):
        TouchifySettings.instance().setActiveShelf(self.registry_index, id)
        self.loadLayout()

    def editPreset(self):
        pass

    def savePreset(self, noReload: bool = False):
        state = self.currentState()
        if self.currentPresetId().lower() == "none": return

        cached_state = TouchifySettings.instance().getActiveShelf(self.registry_index)
        cached_state.preset_data = state
        TouchifySettings.instance().getConfig().save()

        if not noReload: TouchifySettings.reload()

    def savePresetAs(self):
        dlg = self.__setupDialog(ShelfOptionsDialog.PresetSaveAs())
        if dlg.exec_():
            result: Toolshelf = Toolshelf()
            editorResults: ShelfOptionsDialog.PresetSaveAs = dlg.editableConfig
            selectedResourcePackIndex: int = int(editorResults.resource_pack) - 1

            if selectedResourcePackIndex <= -1: return

            selectedResourcePack = TouchifySettings.instance().getResourcePacks()[selectedResourcePackIndex]
            result.preset_data = self.currentState()
            result.preset_name = editorResults.display_name
            selectedResourcePack.shelves.append(result)
            TouchifySettings.instance().getConfig().save()
            TouchifySettings.reload()

    def deletePreset(self):
        shelfToDelete = TouchifySettings.instance().getActiveShelf(self.registry_index)
        shelfRegistryKey = TouchifySettings.instance().getActiveShelfKey(self.registry_index)

        if shelfToDelete == None or shelfToDelete == "none":
            return
        
        shelfParentResourcePack = shelfRegistryKey.getResourcePack()
        if shelfParentResourcePack == None:
            return
        
        shelfParentResourcePack.shelves.remove(shelfToDelete)

        TouchifySettings.instance().setActiveShelf(self.registry_index, "none")
        TouchifySettings.instance().getConfig().save()
        TouchifySettings.reload()

    #endregion

    #region Actions

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

    def onConfigUpdated(self):
        self.loadLayout()

    def onShelfIndexChanged(self):
        self.sigShelfIndexChanged.emit()

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
        
        
        self.saveLayout()

    #endregion

class ShelfWidgetStack(QStackedWidget):
    def __init__(self, parent: ShelfWidget = None):
        super().__init__(parent)
        self.shelf = parent

    def setCurrentIndex(self, index):
        super().setCurrentIndex(index)
        self.shelf.onShelfIndexChanged()

    def sizeHint(self):
        widget = self.currentWidget()
        if widget:
            return self.currentWidget().sizeHint()
        else:
            return super().sizeHint()
    
    def minimumSizeHint(self):
        widget = self.currentWidget()
        if widget:
            return self.currentWidget().minimumSizeHint()
        else:
            return super().minimumSizeHint()