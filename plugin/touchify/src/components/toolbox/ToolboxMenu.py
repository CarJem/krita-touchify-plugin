from typing import TYPE_CHECKING
from krita import QAction, QMenu, pyqtSignal
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.settings.TouchifySettings import TouchifySettings


from PyQt5.QtWidgets import QAction, QMenu


if TYPE_CHECKING:
    from touchify.src.components.toolbox.ToolboxWidget import ToolboxWidget

class ToolboxMenu(QMenu):
    sigEditModeToggled = pyqtSignal(bool)
    sigSettingsRequested = pyqtSignal()
    sigPresetsChangedRequested = pyqtSignal(str)

    sigSavePresetAsRequested = pyqtSignal()
    sigDeletePresetRequested = pyqtSignal()
    sigResetRequested = pyqtSignal()
    
    sigAddSectionRequested = pyqtSignal()
    sigEditSectionRequested = pyqtSignal(str)
    sigDuplicateSectionRequested = pyqtSignal(str)
    sigDeleteSectionRequested = pyqtSignal(str)
    
    sigAddToolRequested = pyqtSignal(str)
    sigEditToolRequested = pyqtSignal(str, str)
    sigDuplicateToolRequested = pyqtSignal(str, str)
    sigDeleteToolRequested = pyqtSignal(str, str)

    def __init__(self, parent: "ToolboxWidget", currentPresetId: str = ""):
        super(ToolboxMenu, self).__init__(parent)

        self.toolbar = parent

        self._currentPresetId = currentPresetId
        self._currentItemUUID: str | None = None
        self._currentSectionUUID: str | None = None
        self._editModeSectionActions: list[QAction] = []
        self._editModeToolActions: list[QAction] = []
        self._tempSeperators: list[QAction] = []

        self.editModeAction = self.addAction("Edit Mode")
        self.editModeAction.setCheckable(True)
        self.editModeAction.setChecked(False)
        self.editModeAction.toggled.connect(self.onEditModeToggled)

        self.presetsSubmenuAction = self.addAction("Presets")
        self.presetsSubmenuAction.setMenu(QMenu(self))
        self.reloadPresets()

        self.addSeparator()



        

        #region Tool Actions
        
        self.addToolAction = self.addAction("Add Tool...")
        self.addToolAction.setEnabled(False)
        self.addToolAction.triggered.connect(self.onAddToolRequested)
        self._editModeToolActions.append(self.addToolAction)

        self.editToolAction = self.addAction("Edit Tool...")
        self.editToolAction.setEnabled(False)
        self.editToolAction.triggered.connect(self.onEditToolRequested)
        self._editModeToolActions.append(self.editToolAction)

        self.cloneToolAction = self.addAction("Clone Tool...")
        self.cloneToolAction.setEnabled(False)
        self.cloneToolAction.triggered.connect(self.onCloneToolRequested)
        self._editModeToolActions.append(self.cloneToolAction)

        self.deleteToolAction = self.addAction("Delete Tool...")
        self.deleteToolAction.setEnabled(False)
        self.deleteToolAction.triggered.connect(self.onDeleteToolRequested)
        self._editModeToolActions.append(self.deleteToolAction)

        #endregion

        self.toolSeperator = self.addSeparator()

        #region Section Actions

        self.addSectionAction = self.addAction("Add Section...")
        self.addSectionAction.setEnabled(False)
        self.addSectionAction.triggered.connect(self.onAddSectionRequested)
        self._editModeSectionActions.append(self.addSectionAction)

        self.editSectionAction = self.addAction("Edit Section...")
        self.editSectionAction.setEnabled(False)
        self.editSectionAction.triggered.connect(self.onEditSectionRequested)
        self._editModeSectionActions.append(self.editSectionAction)

        self.cloneSectionAction = self.addAction("Clone Section...")
        self.cloneSectionAction.setEnabled(False)
        self.cloneSectionAction.triggered.connect(self.onCloneSectionRequested)
        self._editModeSectionActions.append(self.cloneSectionAction)

        self.deleteSectionAction = self.addAction("Delete Section...")
        self.deleteSectionAction.setEnabled(False)
        self.deleteSectionAction.triggered.connect(self.onDeleteSectionRequested)
        self._editModeSectionActions.append(self.deleteSectionAction)

        #endregion

        self.sectionOptionsAction = self.addAction("Section")
        self.sectionOptionsAction.setVisible(False)
        self.sectionOptionsAction.setMenu(QMenu())

        self.presetSeperator = self.addSeparator()

        self.toolboxSettingsAction = self.addAction("Settings...")
        self.toolboxSettingsAction.setEnabled(False)
        self.toolboxSettingsAction.triggered.connect(self.onSettingsRequested)



    def setCurrentPreset(self, currentPresetId: str):
        self._currentPresetId = currentPresetId
        self.reloadPresets()
        self.refreshActions()

    def setCurrentItem(self, section_uuid: str, item_uuid: str):
        self._currentItemUUID = item_uuid
        self._currentSectionUUID = section_uuid
        self.refreshActions()

    def reloadPresets(self):
        self.presetsSubmenuAction.menu().clear()

        isNoPresetActive = self._currentPresetId == "none"

        menus: dict[str, QMenu] = {}
        sub_menus: dict[str, dict[str, QMenu]] = {}


        menuTarget = self.presetsSubmenuAction.menu()
        registry = TouchifySettings.registry(ToolboxData)
        if registry != None:
            for key, preset in registry.items():
                if not key.id in menus:
                    menus[key.id] = menuTarget.addMenu(key.name)
                    sub_menus[key.id] = {}

                preset: ToolboxData
                preset_group: str = ""

                action = QAction(preset.preset_name, self)
                action.setCheckable(True)
                if self._currentPresetId == key.actual_key:
                    action.setChecked(True)
                action.setData(key.actual_key)
                action.triggered.connect(self.onPresetChangeRequested)

                if preset_group == "":
                    menus[key.id].addAction(action)
                else:
                    if not preset_group in sub_menus[key.id]:
                        sub_menus[key.id][preset_group] = menus[key.id].addMenu(preset_group)
                    sub_menus[key.id][preset_group].addAction(action)

        if len(menuTarget.actions()) == 0:
            noActions = menuTarget.addAction("No Presets Avaliable")
            noActions.setEnabled(False)


        self.presetsSubmenuAction.menu().addSeparator()

        noPresetAction = self.presetsSubmenuAction.menu().addAction("No Preset")
        noPresetAction.setCheckable(True)
        noPresetAction.setChecked(isNoPresetActive)
        noPresetAction.setData("none")
        noPresetAction.triggered.connect(self.onPresetChangeRequested)
        self.presetsSubmenuAction.menu().addSeparator()


        if not isNoPresetActive:
            presetSaveAsAction = self.presetsSubmenuAction.menu().addAction("Save as...")
            presetSaveAsAction.setEnabled(True)
            presetSaveAsAction.triggered.connect(self.onSavePresetAsRequested)

            presetDeleteAction = self.presetsSubmenuAction.menu().addAction("Delete")
            presetDeleteAction.setEnabled(True)
            presetDeleteAction.triggered.connect(self.onDeletePresetRequested)
        else:
            presetSaveAsAction = self.presetsSubmenuAction.menu().addAction("Export to Preset...")
            presetSaveAsAction.setEnabled(True)
            presetSaveAsAction.triggered.connect(self.onSavePresetAsRequested)

            resetAction = self.presetsSubmenuAction.menu().addAction("Reset Layout")
            resetAction.setEnabled(True)
            resetAction.triggered.connect(self.onResetRequested)

    def refreshActions(self):
        is_editing = self.editModeAction.isChecked()
        is_tool = self._currentItemUUID != None
        is_section = self._currentSectionUUID != None

        self.toolboxSettingsAction.setEnabled(is_editing)
        self.toolboxSettingsAction.setVisible(is_editing)

        self.sectionOptionsAction.setVisible(is_tool and is_editing)
        self.sectionOptionsAction.setEnabled(is_tool and is_editing)
        self.toolSeperator.setVisible((is_tool or is_section) and is_editing)
        self.toolSeperator.setEnabled((is_tool or is_section) and is_editing)
        self.presetSeperator.setVisible(is_editing)
        self.presetSeperator.setEnabled(is_editing)
        
        if is_tool and is_editing: 
            self.sectionOptionsAction.menu().insertActions(None, self._editModeSectionActions)
            for entry in self._editModeSectionActions:
                try: self.removeAction(entry)
                except: pass
        else: 
            self.insertActions(self.presetSeperator, self._editModeSectionActions)

        for entry in self._editModeToolActions: 
            entry.setVisible(is_tool and is_editing)
            entry.setEnabled(is_tool and is_editing)    

        for entry in self._editModeSectionActions: 
            entry.setVisible(is_section and is_editing)
            entry.setEnabled(is_section and is_editing)

        if is_section and is_editing:
            self.addToolAction.setEnabled(True)
            self.addToolAction.setVisible(True)
        
        if is_editing:
            self.addSectionAction.setEnabled(True)
            self.addSectionAction.setVisible(True)

    def onResetRequested(self):
        self.sigResetRequested.emit()

    def onDeletePresetRequested(self):
        self.sigDeletePresetRequested.emit()

    def onSavePresetAsRequested(self):
        self.sigSavePresetAsRequested.emit()

    def onPresetChangeRequested(self):
        ac: QAction = self.sender()
        if isinstance(ac, QAction):
            id: str = ac.data()
            if isinstance(id, str):
                self.sigPresetsChangedRequested.emit(id)

    def onAddSectionRequested(self):
        self.sigAddSectionRequested.emit()

    def onEditSectionRequested(self):
        self.sigEditSectionRequested.emit(self._currentSectionUUID)

    def onCloneSectionRequested(self):
        self.sigDuplicateSectionRequested.emit(self._currentSectionUUID)

    def onDeleteSectionRequested(self):
        self.sigDeleteSectionRequested.emit(self._currentSectionUUID)

    def onAddToolRequested(self):
        self.sigAddToolRequested.emit(self._currentSectionUUID)

    def onEditToolRequested(self):
        self.sigEditToolRequested.emit(self._currentSectionUUID, self._currentItemUUID)

    def onCloneToolRequested(self):
        self.sigDuplicateToolRequested.emit(self._currentSectionUUID, self._currentItemUUID)

    def onDeleteToolRequested(self):
        self.sigDeleteToolRequested.emit(self._currentSectionUUID, self._currentItemUUID)

    def onSettingsRequested(self):
        self.sigSettingsRequested.emit()

    def onEditModeToggled(self, enabled: bool):
        self.sigEditModeToggled.emit(enabled)
        self.refreshActions()