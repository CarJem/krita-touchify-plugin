from copy import deepcopy
from PyQt5.QtWidgets import QSizePolicy
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from touchify.src.components.toolshelf.ShelfDock import ShelfDock
from touchify.src.components.special.PropertyGridDialog import PropertyGridDialog
from touchify.src.components.toolshelf.ShelfLoader import ShelfLoader

from touchify.src.components.toolshelf.ShelfContainer import ShelfContainer, ShelfPanel
from touchify.src.components.toolshelf.ShelfTabBar import ShelfTabBar
from touchify.src.components.toolshelf.ShelfToolbar import ShelfToolbar
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
from touchify.src.config.toolshelf.ToolshelfSettings import ToolshelfSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfContainer import ToolshelfContainer
from touchify.src.config.toolshelf.ToolshelfPage import ToolshelfPage
from touchify.src.extensions.json_extensions import JsonExtensions
import touchify.src.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.managers.shared.events import GlobalEvents
import touchify.src.components.toolshelf.ShelfClasses as ShelfClasses
from touchify.src.managers.shared.settings import *
from touchify.__env__ import *
from touchify.src.managers.normal.dockers import *

from typing import TYPE_CHECKING, Any

from touchify.src.managers.shared.settings_krita import KritaSettings
if TYPE_CHECKING:
    from .ShelfDockWidget import ShelfDockWidget, ShelfDockWidgetAlt
    from ..popup.PopupWidget import PopupWidget
    from touchify.src.PluginManagers import TouchifyManagers

class ShelfWidget(QWidget):

    class SettingsLoader(QObject):

        def __init__(self, parent: "ShelfWidget"):
            super().__init__(parent)
            self._shelf = parent

        def getCurrentShelfId(self, registry_index: int) -> str:
            fallback_val = "none"

            if registry_index >= 0:
                return KritaSettings.readSetting(Env.SettingsPath.TOOLSHELF, "SelectedPreset_" + str(registry_index), fallback_val)
            else:
                return fallback_val

        def getCurrentShelf(self, registry_index: int) -> Toolshelf:
            registry = TouchifySettings.registry(Toolshelf)
            registry_selection = self.getCurrentShelfId(registry_index)

            if registry_selection in registry:
                return registry[registry_selection]    
            else: 
                return Toolshelf()
            
        def setCurrentShelf(self, registry_index: int, id: str) -> str:
            if registry_index >= 0:
                KritaSettings.writeSetting(Env.SettingsPath.TOOLSHELF, "SelectedPreset_" + str(registry_index), id, False)

        def getCurrentRegistryKey(self, registry_index: int) -> "TouchifySettings.RegistryKey":
            registry = TouchifySettings.registry(Toolshelf)
            registry_selection: str = self.getCurrentShelfId(registry_index)

            if registry_selection in registry:
                keys = [key for key, val in registry.items() if key.actual_key == registry_selection]
                return keys[0]
            else: 
                return "none"

        def sync(self, noReload: bool = False):
            TouchifySettings.save()

            if noReload: return
            TouchifySettings.load()
            GlobalEvents.EMIT_SIGNAL_TOOLSHELF_UPDATED(self._shelf.registry_index)

    sigShelfIndexChanged = QtCore.pyqtSignal()

    def __init__(self, parent, managers: "TouchifyManagers", registry_index: int = 0, enforced_data: ToolshelfContainer = None):
        super(ShelfWidget, self).__init__(parent)
        self.display: "ShelfDockWidget" | "PopupWidget" = parent
        self.managers = managers
        self.registry_index = registry_index
        self.settingsLoader = self.SettingsLoader(self)


        if enforced_data != None:
            self.constant_data = enforced_data
            self.is_restricted = True
        else:
            self.constant_data = None
            self.is_restricted = False

        self.hasPreloaded = False


        self._allowAutoSave = True
        self._hideTitlebar = False
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.dlgConfigEditor: PropertyGridDialog | None = None
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

        self.dockPages: list[ShelfPanel] = []
        self.dockPageOptions: list[ToolshelfPageSettings] = []

        self.dockLoader = ShelfLoader(self)
        self.dockStack = ShelfWidgetStack(self)
        self.mainLayout.addWidget(self.dockStack, 2, 0)

        self.dockArea = ShelfPanel(self)
        self.dockStack.addWidget(self.dockArea)

        self.updateStyle()

        managers.mgr_canvas.normalFocus.connect(self.onCanvasFocusGained)
        managers.api_window().notifier.toolChanged.connect(self.onToolChanged)

    def __setupDialog(self, options: Any):
        if self.dlgConfigEditor != None:
            if PyQtExtensions.CommonHelpers.isDeleted(self.dlgConfigEditor) == False:
                return None
        
        self.dlgConfigEditor = PropertyGridDialog(self.api_window, options)
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

    def setTitlebarVisibility(self, state: bool):
        self._hideTitlebar = state
        self.header.setVisible(state)

    def isEditMode(self) -> bool:
        return self.header.optionsMenu.editModeAction.isChecked()
    
    def isAutoSaveEnabled(self) -> bool:
        return self._allowAutoSave

    def currentPresetId(self) -> str:
        return self.settingsLoader.getCurrentShelfId(self.registry_index)

    def currentState(self) -> ToolshelfContainer:
        def getState(dock_area: ShelfPanel):
            subState = ToolshelfPage()
            subState.layout = dock_area.saveState()
        
            for uuid in dock_area.docks:
                dock = dock_area.docks[uuid]
                if isinstance(dock, ShelfDock):
                    dock: ShelfDock
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

    def __shelfDispose(self, dock_item: ShelfDock):
        dock_item.sigEditRequested.disconnect()
        dock_item.sigDeleteRequested.disconnect()
        dock_item.sigEditContainerRequested.disconnect()
        dock_item.sigDuplicateRequested.disconnect()
        dock_item.sigContainerHoverUpdated.disconnect()

    def __shelfSetup(self, dock_item: ShelfDock, uuid: str = None):
        if uuid != None: dock_item.setUUID(uuid)
        dock_item.setEditMode(self.isEditMode())
        dock_item.sigDuplicateRequested.connect(self.cloneShelfItem)
        dock_item.sigEditRequested.connect(self.editShelfItem)
        dock_item.sigDeleteRequested.connect(self.deleteShelfItem)
        dock_item.sigEditContainerRequested.connect(self.editShelfItemContainer)
        dock_item.sigContainerHoverUpdated.connect(self.highlightShelfItemContainer)

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
            KritaSettings.writeSetting(Env.SettingsPath.TOOLSHELF_NOPRESETDATA, str(self.registry_index), state, False)

    def loadLayout(self):
        def loadShelf(sub_state: ToolshelfPage | ToolshelfContainer, dock_area: ShelfPanel):
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
            state: ToolshelfContainer = self.settingsLoader.getCurrentShelf(self.registry_index).preset_data
        else:
            jsonStr = KritaSettings.readSetting(Env.SettingsPath.TOOLSHELF_NOPRESETDATA, str(self.registry_index), "")
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
            sub_dock_area = ShelfPanel(self)
            self.dockStack.addWidget(sub_dock_area)
            self.dockPages.append(sub_dock_area)
            self.dockPageOptions.append(subpage_state.options)
            loadShelf(subpage_state, sub_dock_area)

        self.tabBar.reload(state)
        self.header.reload(state, self.currentPresetId())

        self.header.setVisible(self._hideTitlebar)

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
        new_dock_area = ShelfPanel(self)
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
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        dlg = self.__setupDialog(ToolshelfDock())
        if dlg.exec_():
            dock_item = self.dockLoader.Init_Section(dlg.editableConfig)
            self.__shelfSetup(dock_item)
            current_area.addDock(dock_item)
            self.saveLayout()

    def cloneShelfItem(self, uuid: str):
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        if uuid not in current_area.docks:
            return

        dock_item: ShelfDock = current_area.docks[uuid]   
        dock_settings = deepcopy(dock_item.dock_settings)

        dock_item = self.dockLoader.Init_Section(dock_settings)
        self.__shelfSetup(dock_item)
        current_area.addDock(dock_item)
        self.saveLayout()

    def editShelfItem(self, uuid: str):
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfDock = current_area.docks[uuid]   
        
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
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfDock = current_area.docks[uuid]   
        
        #TODO: Add confirmation dialog
        confirmed = True

        if confirmed:
            self.__shelfDispose(dock_item)
            dock_item.close()
            del current_area.docks[uuid]
            self.saveLayout()

    def highlightShelfItemContainer(self, state: bool, item_uuid: str):
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        if item_uuid not in current_area.docks:
            return
        
        dock_item: ShelfDock = current_area.docks[item_uuid]   

        if not isinstance(dock_item.container(), ShelfContainer):
            return
        
        dock_container: ShelfContainer = dock_item.container()
        dock_container.highlight(state)

    def editShelfItemContainer(self, item_uuid: str):
        current_area: ShelfPanel | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfPanel):
            return

        if item_uuid not in current_area.docks:
            return
        
        dock_item: ShelfDock = current_area.docks[item_uuid]   

        if not isinstance(dock_item.container(), ShelfContainer):
            return
        
        dock_container: ShelfContainer = dock_item.container()
        
        dlg = self.__setupDialog(dock_container.getOptions())
        if dlg.exec_():
            dock_container.setOptions(dlg.editableConfig)
            self.saveLayout()


    #endregion

    #region Actions (Presets)

    def changePreset(self, id: str):
        self.settingsLoader.setCurrentShelf(self.registry_index, id)
        self.loadLayout()

    def editPreset(self):
        pass

    def savePreset(self, noReload: bool = False):
        state = self.currentState()
        if self.currentPresetId().lower() == "none": return

        cached_state = self.settingsLoader.getCurrentShelf(self.registry_index)
        cached_state.preset_data = state
        self.settingsLoader.sync(noReload)

    def savePresetAs(self):
        dlg = self.__setupDialog(ShelfClasses.PresetSaveAs())
        if dlg.exec_():
            result: Toolshelf = Toolshelf()
            editorResults: PropertyGridDialog.PresetSaveAs = dlg.editableConfig
            selectedResourcePackIndex: int = int(editorResults.resource_pack) - 1

            if selectedResourcePackIndex <= -1: return

            selectedResourcePack = TouchifySettings.resourcePacks()[selectedResourcePackIndex]
            result.preset_data = self.currentState()
            result.preset_name = editorResults.display_name
            selectedResourcePack.shelves.append(result)
            self.settingsLoader.sync()

    def deletePreset(self):
        shelfToDelete = self.settingsLoader.getCurrentShelf(self.registry_index)
        shelfRegistryKey = self.settingsLoader.getCurrentRegistryKey(self.registry_index)

        if shelfToDelete == None or shelfToDelete == "none":
            return
        
        shelfParentResourcePack = shelfRegistryKey.getResourcePack()
        if shelfParentResourcePack == None:
            return
        
        shelfParentResourcePack.shelves.remove(shelfToDelete)

        self.settingsLoader.setCurrentShelf(self.registry_index, "none")
        self.settingsLoader.sync()

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

    def onCanvasFocusGained(self):
        if self.containerOptions.enable_pinning:
            if self.dockStack.currentIndex() != 1 and not self.header.pinButton.isChecked():
                self.goToHomePage()

    def onToolChanged(self, current_tool: str):
        def _recursive(da: ShelfPanel):
            for uuid in da.docks:
                dock = da.docks[uuid]
                if isinstance(dock, ShelfDock):
                    dock: ShelfDock
                    dock.onToolChanged(current_tool)

        _recursive(self.dockArea)
        for dockArea in self.dockPages:
            _recursive(dockArea)
            

    def onConfigUpdated(self):
        self.loadLayout()

    def onShelfIndexChanged(self):
        self.sigShelfIndexChanged.emit()

    def onEditModeChanged(self, enabled: bool):
        def _recursive(da: ShelfPanel):
            for uuid in da.docks:
                dock = da.docks[uuid]
                if isinstance(dock, ShelfDock):
                    dock: ShelfDock
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