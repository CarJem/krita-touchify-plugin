from typing import TYPE_CHECKING
from krita import QAction, QMenu, pyqtSignal
from touchify.src.config.toolshelf.Toolshelf import Toolshelf
from touchify.src.settings.TouchifySettings import TouchifySettings


from PyQt5.QtWidgets import QAction, QMenu


if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfWidget import ShelfWidget

class ShelfContextMenu(QMenu):
    sigEditModeToggled = pyqtSignal(bool)
    sigAddShelfItemRequested = pyqtSignal()
    sigEditShelfItemRequested = pyqtSignal(str)
    sigEnterShelfItemRequested = pyqtSignal(str)
    sigCloneShelfItemRequested = pyqtSignal(str)
    sigDeleteShelfItemRequested = pyqtSignal(str)
    sigAddPageRequested = pyqtSignal()
    sigEditPageRequested = pyqtSignal(int)
    sigDeletePageRequested = pyqtSignal(int)
    sigSettingsRequested = pyqtSignal()
    sigPresetsChangedRequested = pyqtSignal(str)
    sigSavePresetRequested = pyqtSignal()
    sigSavePresetAsRequested = pyqtSignal()
    sigDeletePresetRequested = pyqtSignal()
    sigResetRequested = pyqtSignal()
    sigLeaveNestedShelfItemRequested = pyqtSignal()
    sigEnterNestedShelfItemRequested = pyqtSignal()

    def __init__(self, parent: "ShelfWidget", currentPresetId: str = "", is_nested: bool = False, is_restricted: bool = False):
        super(ShelfContextMenu, self).__init__(parent)

        self.host = parent
        self.current_page_index: int = -1

        self.current_dock_item_id = None
        self.current_dock_is_nested = False

        self.is_nested = is_nested
        self.is_restricted = is_restricted

        self._editModePageActions: list[QAction] = []

        self.editModeAction = self.addAction("Edit Mode")
        self.editModeAction.setCheckable(True)
        self.editModeAction.setChecked(False)
        self.editModeAction.toggled.connect(self.onEditModeToggled)

        self.leaveNestedDockAction = self.addAction("Save Panel")
        self.leaveNestedDockAction.setVisible(False)
        self.leaveNestedDockAction.triggered.connect(self.onLeaveNestedDockRequested)

        self.enterNestedDockAction = self.addAction("Edit Panel")
        self.enterNestedDockAction.setVisible(False)
        self.enterNestedDockAction.triggered.connect(self.onEnterNestedDockRequested)

        self.enterDockAction = self.addAction("Edit Panel")
        self.enterDockAction.setEnabled(False)
        self.enterDockAction.triggered.connect(self.onEnterItemRequested)

        self.shelfPresetsSubmenuAction = self.addAction("Presets")
        self.shelfPresetsSubmenuAction.setEnabled(not is_restricted)
        self.shelfPresetsSubmenuAction.setMenu(QMenu(self))
        self.loadPresets(currentPresetId)

        self.addSeparator()

        self.addDockAction = self.addAction("Add Dock...")
        self.addDockAction.setEnabled(False)
        self.addDockAction.triggered.connect(self.onAddItemRequested)

        self.editDockAction = self.addAction("Edit Dock...")
        self.editDockAction.setEnabled(False)
        self.editDockAction.triggered.connect(self.onEditItemRequested)

        self.cloneDockAction = self.addAction("Clone Dock...")
        self.cloneDockAction.setEnabled(False)
        self.cloneDockAction.triggered.connect(self.onCloneItemRequested)

        self.deleteDockAction = self.addAction("Delete Dock...")
        self.deleteDockAction.setEnabled(False)
        self.deleteDockAction.triggered.connect(self.onDeleteItemRequested)

        self.addSeparator()

        self.addPageAction = self.addAction("Add Page...")
        self.addPageAction.setEnabled(False)
        self.addPageAction.triggered.connect(self.onAddPageRequested)
        self._editModePageActions.append(self.addPageAction)

        self.editPageAction = self.addAction("Edit Page...")
        self.editPageAction.setEnabled(False)
        self.editPageAction.triggered.connect(self.onEditPageRequested)
        self._editModePageActions.append(self.editPageAction)

        self.deletePageAction = self.addAction("Delete Page...")
        self.deletePageAction.setEnabled(False)
        self.deletePageAction.triggered.connect(self.onDeletePageRequested)
        self._editModePageActions.append(self.deletePageAction)

        self.pageOptionsAction = self.addAction("Page")
        self.pageOptionsAction.setVisible(False)
        self.pageOptionsAction.setMenu(QMenu())

        self.editSeperator = self.addSeparator()

        self.shelfSettingsAction = self.addAction("Settings...")
        self.shelfSettingsAction.setEnabled(False)
        self.shelfSettingsAction.triggered.connect(self.onSettingsRequested)

    def reload(self, currentPresetId: str):
        self.loadPresets(currentPresetId)

    def loadPresets(self, currentPresetId: str):
        self.shelfPresetsSubmenuAction.menu().clear()

        if self.is_restricted:
            return

        isNoPresetActive = currentPresetId == "none" or self.is_nested

        menus: dict[str, QMenu] = {}
        sub_menus: dict[str, dict[str, QMenu]] = {}


        menuTarget: QMenu = None

        if self.is_nested:
            menuTarget = self.shelfPresetsSubmenuAction.menu().addMenu("Use Preset...")
        else:
            menuTarget = self.shelfPresetsSubmenuAction.menu()

        registry = TouchifySettings.registry(Toolshelf)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = menuTarget.addMenu(key.name)
                    sub_menus[key.id] = {}

                preset: Toolshelf
                action = QAction(preset.preset_name, self)
                action.setCheckable(not self.is_nested)
                if not self.is_nested:
                    if currentPresetId == key.actual_key:
                        action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.onPresetChangeRequested)

                if preset.preset_group == "":
                    menus[key.id].addAction(action)
                else:
                    if not preset.preset_group in sub_menus[key.id]:
                        sub_menus[key.id][preset.preset_group] = menus[key.id].addMenu(preset.preset_group)
                    sub_menus[key.id][preset.preset_group].addAction(action)

        if len(menuTarget.actions()) == 0:
            noActions = menuTarget.addAction("No Presets Avaliable")
            noActions.setEnabled(False)

        if self.is_nested == False:
            self.shelfPresetsSubmenuAction.menu().addSeparator()

        if self.is_nested == False:
            noPresetAction = self.shelfPresetsSubmenuAction.menu().addAction("No Preset")
            noPresetAction.setCheckable(True)
            noPresetAction.setChecked(isNoPresetActive)
            noPresetAction.setData("none")
            noPresetAction.triggered.connect(self.onPresetChangeRequested)
            self.shelfPresetsSubmenuAction.menu().addSeparator()


        if not isNoPresetActive:
            presetSaveAction = self.shelfPresetsSubmenuAction.menu().addAction("Save")
            presetSaveAction.setEnabled(True)
            presetSaveAction.triggered.connect(self.onSavePresetRequested)

            presetSaveAsAction = self.shelfPresetsSubmenuAction.menu().addAction("Save as...")
            presetSaveAsAction.setEnabled(True)
            presetSaveAsAction.triggered.connect(self.onSavePresetAsRequested)

            presetDeleteAction = self.shelfPresetsSubmenuAction.menu().addAction("Delete")
            presetDeleteAction.setEnabled(True)
            presetDeleteAction.triggered.connect(self.onDeletePresetRequested)
        else:
            presetSaveAsAction = self.shelfPresetsSubmenuAction.menu().addAction("Export to Preset...")
            presetSaveAsAction.setEnabled(True)
            presetSaveAsAction.triggered.connect(self.onSavePresetAsRequested)

            resetAction = self.shelfPresetsSubmenuAction.menu().addAction("Reset Layout")
            resetAction.setEnabled(True)
            resetAction.triggered.connect(self.onResetRequested)

    def updateSelection(self, item_id: str = None):
        from touchify.src.components.toolshelf.ShelfDockArea import ShelfDockArea
        from touchify.src.components.toolshelf.ShelfDock import ShelfDock
        from touchify.src.components.toolshelf.ToolshelfNestedDock import ToolshelfNestedDock

        current_area: ShelfDockArea | None = self.host.dockStack.currentWidget()
        if current_area == None or not isinstance(current_area, ShelfDockArea): dock_item = None
        elif item_id not in current_area.docks: dock_item = None
        else: dock_item: ShelfDock = current_area.docks[item_id]

        if dock_item:
            self.current_dock_item_id = item_id
            self.current_dock_is_nested = isinstance(dock_item, ToolshelfNestedDock)
        else:
            self.current_dock_item_id = None
            self.current_dock_is_nested = False

        self.refreshActions()

    def refreshActions(self):
        is_editing = self.editModeAction.isChecked()
        is_dock_selected = self.current_dock_item_id != None
        is_dock_nested = self.current_dock_is_nested

        if self.is_restricted:
            self.shelfPresetsSubmenuAction.setText("Presets")
            self.shelfPresetsSubmenuAction.setEnabled(False)
            self.shelfPresetsSubmenuAction.setVisible(False)

            self.editModeAction.setVisible(False)

            self.leaveNestedDockAction.setVisible(False)
            self.enterNestedDockAction.setVisible(False)
        elif self.is_nested:
            self.shelfPresetsSubmenuAction.setText("Templates")
            self.shelfPresetsSubmenuAction.setEnabled(is_editing)
            self.shelfPresetsSubmenuAction.setVisible(is_editing)

            self.editModeAction.setVisible(False)

            self.leaveNestedDockAction.setVisible(is_editing)    
            self.enterNestedDockAction.setVisible(not is_editing)
        else:
            self.shelfPresetsSubmenuAction.setText("Presets")
            self.shelfPresetsSubmenuAction.setEnabled(True)

            self.editModeAction.setVisible(True)

            self.leaveNestedDockAction.setVisible(False)
            self.enterNestedDockAction.setVisible(False)

        #region Edit Mode Dock Actions

        self.addDockAction.setEnabled(is_editing)
        self.addDockAction.setVisible(is_editing)

        self.editDockAction.setEnabled(is_editing and is_dock_selected)
        self.editDockAction.setVisible(is_editing and is_dock_selected)

        self.cloneDockAction.setEnabled(is_editing and is_dock_selected)
        self.cloneDockAction.setVisible(is_editing and is_dock_selected)

        self.deleteDockAction.setEnabled(is_editing and is_dock_selected)
        self.deleteDockAction.setVisible(is_editing and is_dock_selected)

        self.enterDockAction.setEnabled(is_editing and is_dock_selected and is_dock_nested)
        self.enterDockAction.setVisible(is_editing and is_dock_selected and is_dock_nested)

        #endregion

        #region Edit Mode Page Actions

        if is_dock_selected and is_editing: 
            self.pageOptionsAction.setVisible(True)
            self.pageOptionsAction.menu().insertActions(None, self._editModePageActions)
            for entry in self._editModePageActions:
                try: self.removeAction(entry)
                except: pass
        else: 
            self.pageOptionsAction.setVisible(False)
            self.insertActions(self.pageOptionsAction, self._editModePageActions)

        if is_editing:
            self.addPageAction.setEnabled(True)
            self.addPageAction.setVisible(True)

            self.editPageAction.setEnabled(True)
            self.editPageAction.setVisible(True)

            self.deletePageAction.setEnabled(self.current_page_index >= 0)
            self.deletePageAction.setVisible(True)
        else:
            self.addPageAction.setEnabled(False)
            self.addPageAction.setVisible(False)

            self.editPageAction.setEnabled(False)
            self.editPageAction.setVisible(False)

            self.deletePageAction.setEnabled(False)
            self.deletePageAction.setVisible(False)

        #endregion
       
        self.editSeperator.setVisible(is_editing)

        self.shelfSettingsAction.setEnabled(is_editing)
        self.shelfSettingsAction.setVisible(is_editing)

    def onResetRequested(self):
        self.sigResetRequested.emit()

    def onDeletePresetRequested(self):
        self.sigDeletePresetRequested.emit()

    def onSavePresetRequested(self):
        self.sigSavePresetRequested.emit()

    def onSavePresetAsRequested(self):
        self.sigSavePresetAsRequested.emit()

    def onPresetChangeRequested(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                self.sigPresetsChangedRequested.emit(id)

    def onAddItemRequested(self):
        self.sigAddShelfItemRequested.emit()

    def onEditItemRequested(self):
        if not self.current_dock_item_id: return
        self.sigEditShelfItemRequested.emit(self.current_dock_item_id)

    def onEnterItemRequested(self):
        if not self.current_dock_item_id: return
        self.sigEnterShelfItemRequested.emit(self.current_dock_item_id)

    def onLeaveNestedDockRequested(self):
        self.sigLeaveNestedShelfItemRequested.emit()

    def onEnterNestedDockRequested(self):
        self.sigEnterNestedShelfItemRequested.emit()

    def onCloneItemRequested(self):
        if not self.current_dock_item_id: return
        self.sigCloneShelfItemRequested.emit(self.current_dock_item_id)

    def onDeleteItemRequested(self):
        if not self.current_dock_item_id: return
        self.sigDeleteShelfItemRequested.emit(self.current_dock_item_id)

    def onSettingsRequested(self):
        self.sigSettingsRequested.emit()

    def onEditPageRequested(self):
        self.sigEditPageRequested.emit(self.current_page_index)

    def onDeletePageRequested(self):
        self.sigDeletePageRequested.emit(self.current_page_index)

    def onAddPageRequested(self):
        self.sigAddPageRequested.emit()

    def onPageChanged(self, index: int):
        self.current_page_index = index
        self.refreshActions()

    def onEditModeToggled(self, enabled: bool):
        self.sigEditModeToggled.emit(enabled)
        self.refreshActions()