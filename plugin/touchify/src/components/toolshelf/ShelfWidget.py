from functools import partial
from PyQt5.QtWidgets import QSizePolicy
from jemlib.alib_propertygrid.PropertySystem import PropertySystem
from krita import *
from PyQt5.QtWidgets import *

from krita import *

from jemlib.alib_vaporjem import Logger
from touchify.src.PluginOptions import PluginOptions
from touchify.src.components.toolshelf.ShelfContextMenu import ShelfContextMenu
from touchify.src.components.toolshelf.ShelfDock import ShelfDock
from touchify.src.components.toolshelf.ShelfLoader import ShelfLoader

from touchify.src.components.toolshelf.ShelfDockArea import ShelfDockArea
from touchify.src.components.toolshelf.ShelfTabBar import ShelfTabBar
from touchify.src.components.toolshelf.ShelfToolbar import ShelfToolbar
from touchify.src.components.toolshelf.ShelfWidgetStack import ShelfWidgetStack
from touchify.src.config.toolshelf.ToolshelfPageSettings import ToolshelfPageSettings
from touchify.src.config.toolshelf.ToolshelfAreaSettings import ToolshelfAreaSettings
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.config.toolshelf.ToolshelfArea import ToolshelfArea
from touchify.src.config.toolshelf.ToolshelfPage import ToolshelfPage
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.managers.GlobalEvents import GlobalEvents
import touchify.src.components.toolshelf.ShelfClasses as ShelfClasses
from touchify.src.settings.TouchifySettings import *
from jemlib.api_touchify.env import *
from touchify.src.managers.DockerManager import *

from typing import TYPE_CHECKING

from jemlib.managers.KritaSettings import KritaSettings
if TYPE_CHECKING:
    from .ToolshelfDockerWidget import ToolshelfDockerWidget
    from ..popup.PopupWidget import PopupWidget
    from touchify.src.PluginManagers import TouchifyManagers
    from touchify.src.components.toolshelf.ToolshelfNestedDock import ToolshelfNestedDock

class ShelfWidget(QWidget):

    class SettingsLoader(QObject):

        def __init__(self, parent: "ShelfWidget"):
            super().__init__(parent)
            self._shelf = parent

        def getCurrentShelfId(self, registry_index: int) -> str:
            fallback_val = "none"

            if registry_index >= 0:
                return KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOOLSHELF, "SelectedPreset_" + str(registry_index), fallback_val)
            else:
                return fallback_val

        def getCurrentShelf(self, registry_index: int) -> Toolshelf:
            registry = TouchifySettings.registry(Toolshelf)
            registry_selection = self.getCurrentShelfId(registry_index)

            if registry_selection in registry:
                return registry[registry_selection]    
            else: 
                return Toolshelf()
            
        def getShelf(self, registry_selection: str) -> Toolshelf:
            registry = TouchifySettings.registry(Toolshelf)
            if registry_selection in registry:
                return registry[registry_selection]    
            else: 
                return Toolshelf()
            
        def setCurrentShelf(self, registry_index: int, id: str) -> str:
            if registry_index >= 0:
                KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOOLSHELF, "SelectedPreset_" + str(registry_index), id, False)

        def getCurrentRegistryKey(self, registry_index: int) -> "TouchifySettings.RegistryKey":
            registry = TouchifySettings.registry(Toolshelf)
            registry_selection: str = self.getCurrentShelfId(registry_index)

            if registry_selection in registry:
                keys = [key for key, val in registry.items() if key.actual_key == registry_selection]
                return keys[0]
            else: 
                return "none"

        def sync(self, registry_index: int, noReload: bool = False):
            TouchifySettings.save()
            if noReload: return
            TouchifySettings.load()
            GlobalEvents().SIGNAL_TOOLSHELF_PRESET_UPDATED.emit(registry_index)

        def loadLayout(self, registry_index: int):
            if self.getCurrentShelfId(registry_index).lower() != "none":
                return self.getCurrentShelf(registry_index).preset_data
            else:
                jsonStr = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOOLSHELF_NOPRESETDATA, str(registry_index), "")
                return JsonExtensions.loadClass(jsonStr, ToolshelfArea)
            
        def saveLayout(self, state: ToolshelfArea, registry_index: int):
            if self.getCurrentShelfId(registry_index).lower() != "none":
                self.savePreset(state, registry_index, True)
            else:
                jsonStr = JsonExtensions.saveClass(state)
                KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOOLSHELF_NOPRESETDATA, str(registry_index), jsonStr, False)
            
        def savePreset(self, state: ToolshelfArea, registry_index: int, no_reload: bool = False):
            cached_state = self.getCurrentShelf(registry_index)
            cached_state.preset_data = state
            self.sync(registry_index, no_reload)
        
        def savePresetAs(self, editorResults: ShelfClasses.PresetSaveAs, state: ToolshelfArea, registry_index: int):
            selectedResourcePackIndex: int = int(editorResults.resource_pack) - 1
            if selectedResourcePackIndex <= -1: return

            selectedResourcePack = TouchifySettings.resourcePacks()[selectedResourcePackIndex]
        
            result: Toolshelf = Toolshelf()
            result.preset_data = state
            result.preset_name = editorResults.display_name
            selectedResourcePack.shelves.append(result)
            self.sync(registry_index)

        def deletePreset(self, registry_index: int):
            shelfToDelete = self.getCurrentShelf(registry_index)
            shelfRegistryKey = self.getCurrentRegistryKey(registry_index)

            if shelfToDelete == None or shelfToDelete == "none":
                return
            
            shelfParentResourcePack = shelfRegistryKey.getResourcePack()
            if shelfParentResourcePack == None:
                return
            
            shelfParentResourcePack.shelves.remove(shelfToDelete)

            self.setCurrentShelf(registry_index, "none")
            self.sync(registry_index)

    sigShelfIndexChanged = QtCore.pyqtSignal()
    sigEditModeChanged = QtCore.pyqtSignal(bool)

    def __init__(self, parent, managers: "TouchifyManagers", registry_index: int = 0, fixed_state: ToolshelfArea = None, parent_dock_widget: "ToolshelfNestedDock" = None):
        super(ShelfWidget, self).__init__(parent)
        self.display: "ToolshelfDockerWidget" | "PopupWidget" | "ToolshelfNestedDock" = parent
        self.managers = managers
        self.registry_index = registry_index
        self.settingsLoader = self.SettingsLoader(self)


        if parent_dock_widget != None:
            self.nestedDock = parent_dock_widget
            self.is_nested = True
        else:
            self.nestedDock = None
            self.is_nested = False

        if fixed_state != None:
            self.constant_data = fixed_state
            self.is_restricted = True
        else:
            self.constant_data = None
            self.is_restricted = False

        self.hasPreloaded = False
        self._hideTitlebar = False
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        self.propertyEditor: PluginOptions | None = None
        self.containerOptions: ToolshelfAreaSettings = ToolshelfAreaSettings()
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

        self.dockPages: list[ShelfDockArea] = []
        self.dockPageOptions: list[ToolshelfPageSettings] = []

        self.dockLoader = ShelfLoader(self)
        self.dockStack = ShelfWidgetStack(self)
        self.mainLayout.addWidget(self.dockStack, 2, 0)

        self.dockArea = ShelfDockArea(self)
        self.dockStack.addWidget(self.dockArea)

        self.optionsMenu = ShelfContextMenu(self, self.currentPresetId(), self.is_nested, self.is_restricted)
        self.optionsMenu.aboutToHide.connect(self.onOptionsMenuAboutToHide)

        self.optionsMenu.sigAddShelfItemRequested.connect(self.addShelfItem)
        self.optionsMenu.sigEditShelfItemRequested.connect(self.editShelfItem)
        self.optionsMenu.sigEnterShelfItemRequested.connect(self.enterNestedShelfItem)
        self.optionsMenu.sigCloneShelfItemRequested.connect(self.cloneShelfItem)
        self.optionsMenu.sigDeleteShelfItemRequested.connect(self.deleteShelfItem)

        self.optionsMenu.sigEnterNestedShelfItemRequested.connect(self.enterNestedContainer)
        self.optionsMenu.sigLeaveNestedShelfItemRequested.connect(self.exitNestedContainer)

        self.optionsMenu.sigAddPageRequested.connect(self.insertPage)
        self.optionsMenu.sigEditPageRequested.connect(self.editPage)
        self.optionsMenu.sigDeletePageRequested.connect(self.deletePage)

        self.optionsMenu.sigPresetsChangedRequested.connect(self.changePreset)
        self.optionsMenu.sigEditModeToggled.connect(self.onEditModeChanged)
        self.optionsMenu.sigSettingsRequested.connect(self.editLayout)

        self.optionsMenu.sigSavePresetAsRequested.connect(self.savePresetAs)
        self.optionsMenu.sigSavePresetRequested.connect(self.savePreset)
        self.optionsMenu.sigDeletePresetRequested.connect(self.deletePreset)
        self.optionsMenu.sigResetRequested.connect(partial(self.resetLayout, False))

        self.updateStyle()

        managers.mgr_canvas.normalFocus.connect(self.onCanvasFocusGained)
        managers.api_window().notifier.toolChanged.connect(self.onToolChanged)

    def updateStyle(self):
        if self.is_nested:
            self.dockStack.setStyleSheet(f"""
                ShelfWidgetStack {{
                    border: 0px solid transparent
                }}
            """)
        else:
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
            Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | Preloading: start')
            self.hasPreloaded = True
            self.loadLayout()
            Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | Preloading: finish')
        super().showEvent(event)

    def hideEvent(self, event: QHideEvent):
        super().hideEvent(event)


    def contextMenuEvent(self, a0: QContextMenuEvent):

        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
            return super().contextMenuEvent()
        
        is_context_menu_allowed = len(current_area.docks) == 0 or (self.header.underMouse() or self.tabBar.underMouse())
        
        if self.isEditMode() and is_context_menu_allowed:
            self.onContextMenu(a0.globalPos())
            
        return super().contextMenuEvent(a0)

    #endregion
    
    #region Getters / Setters

    def setTitlebarVisibility(self, state: bool):
        self._hideTitlebar = state
        self.header.setVisible(state)

    def setEditMode(self, state: bool) -> bool:
        self.optionsMenu.editModeAction.setChecked(state)

    def isEditMode(self) -> bool:
        return self.optionsMenu.editModeAction.isChecked()

    def getDockAreaId(self, dock_index: int):
        if self.is_nested:
            return f"{str(self.nestedDock._parentAreaId)}/{str(dock_index)}/{str(self.nestedDock._name)}"
        else:
            return f"{TouchifyEnv.SettingsPath.TOOLSHELF}/{str(self.registry_index)}/{str(dock_index)}"

    def getNestedLevel(self):
        def nested_test(x: ShelfWidget, i: int = 0):
            if x.is_nested:
                i += 1 
                return nested_test(x.nestedDock.parentShelf, i)
            else:
                return i

        return nested_test(self)

    def currentPresetId(self) -> str:
        return self.settingsLoader.getCurrentShelfId(self.registry_index)

    def currentState(self) -> ToolshelfArea:
        def getState(dock_area: ShelfDockArea):
            subState = ToolshelfPage()
            subState.layout = dock_area.saveState()
        
            for uuid in dock_area.docks:
                dock = dock_area.docks[uuid]
                if isinstance(dock, ShelfDock):
                    dock: ShelfDock
                    subState.items[uuid] = dock._dockSettings
            return subState

        result = ToolshelfArea()

        rootState: ToolshelfArea = getState(self.dockArea)
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
        dock_item.sigContextMenuRequested.disconnect()
        dock_item.sigContainerHoverUpdated.disconnect()

    def __shelfSetup(self, dock_item: ShelfDock, uuid: str = None, index: int = 0):
        if uuid != None: dock_item.setUUID(uuid)
        dock_item.setEditMode(self.isEditMode())
        dock_item.setParentAreaId(self.getDockAreaId(index))
        dock_item.sigContextMenuRequested.connect(self.onContextMenu)
        dock_item.sigContainerHoverUpdated.connect(self.onMouseHover)

    #endregion

    #region Actions (ShelfLayout)

    def resetLayout(self, noSave: bool = True):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | resetLayout: start')
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


        self.containerOptions = ToolshelfAreaSettings()

        self.dockPages.clear()
        self.dockPageOptions.clear()

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | resetLayout: prefinished')

        if not noSave:
            self.saveLayout()
            self.loadLayout()

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | resetLayout: finished')

    def saveLayout(self):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | save_layout: start')
        if self.is_restricted: 
            return
        elif self.is_nested:
            self.nestedDock.setMetadata(self.currentState())
        else:
            self.settingsLoader.saveLayout(self.currentState(), self.registry_index)
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | save_layout: finish')

    def loadLayout(self):
        def loadShelf(sub_state: ToolshelfPage | ToolshelfArea, dock_area: ShelfDockArea, dock_index: int):
            dock_area.setAreaId(self.getDockAreaId(dock_index))
            for uuid in sub_state.items:
                item = sub_state.items[uuid]
                dock_item = self.dockLoader.Init_Section(item)
                self.__shelfSetup(dock_item, uuid, dock_area._parentAreaId)
                dock_area.addDock(dock_item)
            
            if "main" in sub_state.layout:
                try:
                    dock_area.restoreState(sub_state.layout)
                except Exception as ex:
                    print(str(ex))

        if not self.hasPreloaded: 
            return

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: init')
        self.resetLayout()
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: reset')
        state: ToolshelfArea

        if self.is_restricted:
            state: ToolshelfArea = PropertySystem.deepcopy(self.constant_data)
        elif self.is_nested:
            state: ToolshelfArea = self.nestedDock.getMetadata()
        else:
            state: ToolshelfArea = self.settingsLoader.loadLayout(self.registry_index)

        if state == None:
            return

        self.containerOptions: ToolshelfAreaSettings = state.options
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

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: load started mainpage')
        loadShelf(state, self.dockArea, 0)
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: load finished mainpage')
        

        for idx, subpage_state in enumerate(state.pages):
            Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: load started page_{str(idx)}')
            subpage_state: ToolshelfPage
            sub_dock_area = ShelfDockArea(self)
            self.dockStack.addWidget(sub_dock_area)
            self.dockPages.append(sub_dock_area)
            self.dockPageOptions.append(subpage_state.options)
            loadShelf(subpage_state, sub_dock_area, idx+1)
            Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: load finished page_{str(idx)}')
            

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: load tabbar/header/menu')
        self.tabBar.reload(state)
        self.header.reload(state, self.currentPresetId())
        self.optionsMenu.reload(self.currentPresetId())

        self.header.setVisible(self._hideTitlebar)

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: reload display')
        self.display.shelfReloadEvent(state)
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | loading_layout: finished')

    def editLayout(self):
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), self.containerOptions)
        result: ToolshelfAreaSettings = self.propertyEditor.exec_()
        if not result: return 
        self.containerOptions = result
             
        self.saveLayout()
        self.loadLayout()

    #endregion

    #region Actions (ShelfPages)

    def insertPage(self):
        new_dock_area = ShelfDockArea(self)
        new_dock_area_settigns = ToolshelfPageSettings()
        self.dockPages.append(new_dock_area)
        self.dockPageOptions.append(new_dock_area_settigns)
        self.dockStack.addWidget(new_dock_area)
        
        self.saveLayout()
        self.loadLayout()

        self.goToPage(len(self.dockPages) - 1)

    def editPage(self, index: int):
        if index == -1:
            pageData = self.homepageOptions
        else:
            pageData = self.dockPageOptions[index]

        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), pageData)
        result: ToolshelfPageSettings = self.propertyEditor.exec_()
        if not result: return

        if index == -1: self.homepageOptions = result
        else: self.dockPageOptions[index] = result

        self.saveLayout()
        self.loadLayout()

    def deletePage(self, index: int):
        removed_dock_area_options = self.dockPageOptions.pop(index)
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

    def addShelfItem(self):
        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
            return

        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), ToolshelfDock())
        result: ToolshelfDock = self.propertyEditor.exec_()
        if not result: return

        dock_item = self.dockLoader.Init_Section(result)
        self.__shelfSetup(dock_item, None, current_area._parentAreaId)
        current_area.addDock(dock_item)
        self.saveLayout()

    def cloneShelfItem(self, uuid: str):
        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
            return

        if uuid not in current_area.docks:
            return

        dock_item: ShelfDock = current_area.docks[uuid]   
        dock_settings = PropertySystem.deepcopy(dock_item._dockSettings)

        dock_item = self.dockLoader.Init_Section(dock_settings)
        self.__shelfSetup(dock_item, None, current_area._parentAreaId)
        current_area.addDock(dock_item)
        self.saveLayout()

    def editShelfItem(self, uuid: str):
        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
            return

        if uuid not in current_area.docks:
            return
        
        dock_item: ShelfDock = current_area.docks[uuid]   
        
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), dock_item._dockSettings)
        result: ShelfDock = self.propertyEditor.exec_()
        if not result: return


        lastState = current_area.saveState()
        self.__shelfDispose(dock_item)
        dock_item.close()

        dock_item = self.dockLoader.Init_Section(result)
        self.__shelfSetup(dock_item, uuid, current_area._parentAreaId)
        current_area.addDock(dock_item)
        current_area.restoreState(lastState)
        self.saveLayout()

    def deleteShelfItem(self, uuid: str):
        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
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

    #endregion

    #region Actions (Containers)

    def enterNestedShelfItem(self, item_uuid: str):
        current_area: ShelfDockArea | None = self.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea):
            return

        if item_uuid not in current_area.docks:
            return
        
        from touchify.src.components.toolshelf.ToolshelfNestedDock import ToolshelfNestedDock
        if not isinstance(current_area.docks[item_uuid], ToolshelfNestedDock):
            return
        
        dock_item: ToolshelfNestedDock = current_area.docks[item_uuid]   
        dock_item.setContainerEditMode(True)

    def enterNestedContainer(self):
        if not self.is_nested:
            return
        
        self.nestedDock.setContainerEditMode(True)

    def exitNestedContainer(self):
        if not self.is_nested:
            return
        
        self.nestedDock.setContainerEditMode(False)

    #endregion

    #region Actions (Presets)

    def changePreset(self, id: str):
        if self.is_nested:
            shlf = self.settingsLoader.getShelf(id)
            self.nestedDock.setMetadata(shlf.preset_data)
            self.loadLayout()
        else:
            self.settingsLoader.setCurrentShelf(self.registry_index, id)
            self.loadLayout()

    def savePreset(self):
        self.settingsLoader.savePreset(self.currentState(), self.registry_index)

    def savePresetAs(self):
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), ShelfClasses.PresetSaveAs())
        result: ShelfClasses.PresetSaveAs = self.propertyEditor.exec_()
        if not result: return

        self.settingsLoader.savePresetAs(result, self.currentState(), self.registry_index)

    def deletePreset(self):
        self.settingsLoader.deletePreset(self.registry_index)

    #endregion

    #region Actions

    def openShelfMenu(self, pos: QPoint = None):
        if pos == None:
            pos = QCursor.pos()
        
        self.optionsMenu.exec_(pos)

    def goToHomePage(self):
        self.dockStack.setCurrentIndex(0)
        self.tabBar.onPageChanged("ROOT")
        self.header.onPageChanged(-1)
        self.optionsMenu.onPageChanged(-1)

    def goToPage(self, index: int):
        if index < 0: return
        if index >= self.dockStack.count(): return

        self.dockStack.setCurrentIndex(index + 1)
        self.tabBar.onPageChanged("Tab_" + str(index))
        self.header.onPageChanged(index)
        self.optionsMenu.onPageChanged(index)

    #endregion

    #region Signals

    def onMouseHover(self, state: bool, item_uuid: str):
        pass

    def onContextMenu(self, pos: QPoint, item_id: str = None):
        if self.is_restricted: return

        self.optionsMenu.updateSelection(item_id)
        self.optionsMenu.exec_(pos)

    def onOptionsMenuAboutToHide(self):
        self.header.mainButton.setMenu(None)

    def onCanvasFocusGained(self):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | container_focus_gained')
        if self.containerOptions.enable_pinning:
            if self.dockStack.currentIndex() != 1 and not self.header.pinButton.isChecked():
                self.goToHomePage()

    def onToolChanged(self, current_tool: str):
        def _recursive(da: ShelfDockArea):
            for uuid in da.docks:
                dock = da.docks[uuid]
                if isinstance(dock, ShelfDock):
                    dock: ShelfDock
                    dock.onToolChanged(current_tool)

        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | tool_changed')
        _recursive(self.dockArea)
        for dockArea in self.dockPages:
            _recursive(dockArea)

    def onThemeChanged(self):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | theme_changing: start')
        self.updateStyle()
        self.loadLayout()
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | theme_changing: finish')
            
    def onConfigUpdated(self):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | onConfigUpdated')
        self.loadLayout()

    def onShelfIndexChanged(self):
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | onShelfIndexChanged')
        self.sigShelfIndexChanged.emit()

    def onEditModeChanged(self, enabled: bool):        
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | onEditModeChanged: started')
        self.dockArea.setEditMode(enabled)
        for dockArea in self.dockPages:
            dockArea.setEditMode(enabled)
        self.saveLayout()
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | onEditModeChanged: prefinished')
        self.sigEditModeChanged.emit(enabled)
        Logger.logDebug('Touchify','ShelfWidget', "unknown", f'shelf: {self.registry_index} | onEditModeChanged: finished')

    #endregion