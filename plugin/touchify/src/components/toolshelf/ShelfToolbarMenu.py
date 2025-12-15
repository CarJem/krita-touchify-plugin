from typing import TYPE_CHECKING
from krita import QAction, QMenu, pyqtSignal
from touchify.src.config.toolshelf.Toolshelf import Toolshelf
from touchify.src.settings.TouchifySettings import TouchifySettings


from PyQt5.QtWidgets import QAction, QMenu


if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfToolbar import ShelfToolbar

class ShelfToolbarMenu(QMenu):
    sigEditModeToggled = pyqtSignal(bool)
    sigAddShelfItemRequested = pyqtSignal()
    sigAddPageRequested = pyqtSignal()
    sigEditPageRequested = pyqtSignal(int)
    sigDeletePageRequested = pyqtSignal(int)
    sigSettingsRequested = pyqtSignal()
    sigPresetsChangedRequested = pyqtSignal(str)
    sigSavePresetRequested = pyqtSignal()
    sigSavePresetAsRequested = pyqtSignal()
    sigDeletePresetRequested = pyqtSignal()
    sigResetRequested = pyqtSignal()

    def __init__(self, parent: "ShelfToolbar", currentPresetId: str = "", is_nested: bool = False, is_restricted: bool = False):
        super(ShelfToolbarMenu, self).__init__(parent)

        self.toolbar = parent
        self.current_page_index: int = -1

        self.is_nested = is_nested
        self.is_restricted = is_restricted

        self.editModeAction = self.addAction("Edit Mode")
        self.editModeAction.setCheckable(True)
        self.editModeAction.setChecked(False)
        self.editModeAction.toggled.connect(self.onEditModeToggled)

        self.addSeparator()

        self.addDockAction = self.addAction("Add Dock...")
        self.addDockAction.setEnabled(False)
        self.addDockAction.triggered.connect(self.onAddItemRequested)

        self.addSeparator()

        self.addPageAction = self.addAction("Add Page...")
        self.addPageAction.setEnabled(False)
        self.addPageAction.triggered.connect(self.onAddPageRequested)

        self.editPageAction = self.addAction("Edit Page...")
        self.editPageAction.setEnabled(False)
        self.editPageAction.triggered.connect(self.onEditPageRequested)

        self.deletePageAction = self.addAction("Delete Page...")
        self.deletePageAction.setEnabled(False)
        self.deletePageAction.triggered.connect(self.onDeletePageRequested)


        self.addSeparator()

        self.shelfPresetsSubmenuAction = self.addAction("Presets")
        self.shelfPresetsSubmenuAction.setEnabled(not is_restricted)
        self.shelfPresetsSubmenuAction.setMenu(QMenu(self))
        self.loadPresets(currentPresetId)

        self.addSeparator()

        self.shelfSettingsAction = self.addAction("Shelf Settings...")
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
            menuTarget = self.shelfPresetsSubmenuAction.menu().addMenu("Copy Preset from...")
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
            presetSaveAsAction = self.shelfPresetsSubmenuAction.menu().addAction("Save to Preset...")
            presetSaveAsAction.setEnabled(True)
            presetSaveAsAction.triggered.connect(self.onSavePresetAsRequested)

            resetAction = self.shelfPresetsSubmenuAction.menu().addAction("Reset")
            resetAction.setEnabled(True)
            resetAction.triggered.connect(self.onResetRequested)






    def refreshActions(self):
        is_editing = self.editModeAction.isChecked()

        if self.is_restricted:
            self.shelfPresetsSubmenuAction.setEnabled(False)
        elif self.is_nested:
            self.shelfPresetsSubmenuAction.setEnabled(is_editing)
        else:
            self.shelfPresetsSubmenuAction.setEnabled(True)

        self.addDockAction.setEnabled(is_editing)
        self.addPageAction.setEnabled(is_editing)
        self.editPageAction.setEnabled(is_editing)
        self.deletePageAction.setEnabled(is_editing and self.current_page_index >= 0)
        self.shelfSettingsAction.setEnabled(is_editing)

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