# This Python file uses the following encoding: utf-8
from copy import deepcopy
from uuid import uuid4
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *



from jemlib.api_krita.wrappers.window import WindowAPI
from jemlib.api_touchify.env import *
from touchify.src.PluginOptions import PluginOptions
from touchify.src.components.toolbox import ToolboxClasses
from touchify.src.components.toolbox.ToolboxButton import ToolboxButton
from touchify.src.components.toolbox.ToolboxMenu import ToolboxMenu
from touchify.src.components.toolbox.ToolboxStyles import ToolboxStyles
from touchify.src.components.toolbox.ToolboxLayout import ToolboxEmptySpace
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from jemlib.managers.GlobalEvents import GlobalEvents
from jemlib.api_touchify.env import *

from touchify.src.components.toolbox.ToolboxLoader import ToolboxLoader
from touchify.src.components.toolbox.ToolboxWidget import ToolboxWidget
from touchify.src.components.toolbox.ToolboxScrollArea import ToolboxScrollArea
from touchify.src.config.toolbox.ToolboxDataCategory import ToolboxDataCategory
from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem
from touchify.src.settings.TouchifySettings import TouchifySettings
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions

from typing import TYPE_CHECKING

from jemlib.managers.KritaSettings import KritaSettings
from jemlib.alib_widgets.widget.DropIndicatorOverlay import DropIndicatorOverlay
if TYPE_CHECKING:
    from touchify.src.PluginManagers import TouchifyManagers
    from ...PluginWindow import TouchifyWindow

    

DOCKER_TITLE=f"{TouchifyEnv.Title.CORE_DOCKERS_PREFIX} Toolbox"

class ToolboxDocker(QDockWidget):

    class SettingsManager(QObject):
        def __init__(self, parent: "ToolboxDocker"):
            super().__init__(parent)
            self._toolbox = parent

        def getCurrentToolboxId(self) -> str:
            fallback_val = "none"
            return KritaSettings.readSetting(TouchifyEnv.DockerID.TOOLBOX, "SelectedPreset", fallback_val)

        def setCurrentToolboxId(self, id: str):
            KritaSettings.writeSetting(TouchifyEnv.DockerID.TOOLBOX, "SelectedPreset", id, False)
            GlobalEvents().SIGNAL_TOOLBOX_LAYOUT_UPDATED.emit()

        def getCurrentRegistryKey(self) -> "TouchifySettings.RegistryKey":
            registry = TouchifySettings.registry(ToolboxData)
            registry_selection: str = self.getCurrentToolboxId()

            if registry_selection in registry:
                keys = [key for key, val in registry.items() if key.actual_key == registry_selection]
                return keys[0]
            else: 
                return "none"


        def loadLayout(self) -> ToolboxData:
            if self.getCurrentToolboxId().lower() != "none":
                registry = TouchifySettings.registry(ToolboxData)
                registry_selection = self.getCurrentToolboxId()

                if registry_selection in registry:
                    return registry[registry_selection]    
                else: 
                    return ToolboxData()
            else:
                try:
                    jsonStr = KritaSettings.readSetting(TouchifyEnv.SettingsPath.TOOLBOX_NOPRESETDATA, "Cache", "")
                    return JsonExtensions.loadClass(jsonStr, ToolboxData)
                except:
                    return ToolboxData()

        def saveLayout(self, cache_data: ToolboxData, use_cache: bool = True):
            is_cache_preset_active = self.getCurrentToolboxId().lower() == "none"
            if is_cache_preset_active and use_cache:
                jsonStr = JsonExtensions.saveClass(cache_data)
                KritaSettings.writeSetting(TouchifyEnv.SettingsPath.TOOLBOX_NOPRESETDATA, "Cache", jsonStr, False)
                GlobalEvents().SIGNAL_TOOLBOX_LAYOUT_UPDATED.emit()
            else:
                TouchifySettings.save()
                TouchifySettings.load()
                GlobalEvents().SIGNAL_TOOLBOX_LAYOUT_UPDATED.emit()


    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.settingsManager = self.SettingsManager(self)
        self.style_data = ToolboxStyles.ThemeData(ToolboxData(), Qt.Orientation.Vertical)

        self.setWindowTitle(DOCKER_TITLE) # window title also acts as the Docker title in Settings > Dockers
        self.setContentsMargins(0,0,0,0)

        #label = QLabel(" ") # label conceals the 'exit' buttons and Docker title
        #label.setFrameShape(QFrame.StyledPanel)
        #label.setFrameShadow(QFrame.Raised)
        #label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        #label.setMinimumWidth(16)
        #self.setTitleBarWidget(label)

        self.api_window: WindowAPI = None
        self.managers: "TouchifyManagers" = None

        self.containerLoader = ToolboxLoader(self)
        self.propertyEditor: PluginOptions = None
        
        self._isDynamicOrientation = False
        self._toolboxItems: list[ToolboxButton] = []
        self._isNotLoading = True


        self._drag_section_uuid = None
        self._drag_tool_uuid = None
        self._drag_last_button = None
        self._drag_last_position = None

        self.drag_highlight_timer = QTimer()
        self.drag_highlight_timer.timeout.connect(self.onToolDragging)
        self.drag_highlight_timer.setInterval(16)

        self.toolbox = ToolboxWidget()
        self.toolbox.sigContextMenuRequested.connect(self.onContextMenu)
        self.toolbox.sigSectionContextMenuRequested.connect(self.onSectionContextMenu)
        self.toolbox.sigToolContextMenuRequested.connect(self.onToolContextMenu)
        self.toolbox.sigDragStarted.connect(self.onToolDragStarted)
        self.toolbox.sigDragEnded.connect(self.onToolDragEnded)

        self._drop_overlay = DropIndicatorOverlay(self)

        self.scrollArea = ToolboxScrollArea(self, self.toolbox)
        self.scrollArea.setContentsMargins(0,0,0,0)
        self.scrollArea.setViewportMargins(0,0,0,0)
        self.scrollArea.setWidgetResizable(True)
        self.setWidget(self.scrollArea)

        self.settingsMenu = ToolboxMenu(self, self.settingsManager.getCurrentToolboxId())
        self.settingsMenu.sigEditModeToggled.connect(self.onEditModeChanged)
        self.settingsMenu.sigSettingsRequested.connect(self.editToolbox)
        self.settingsMenu.sigPresetsChangedRequested.connect(self.changePreset)
        self.settingsMenu.sigDeletePresetRequested.connect(self.deletePreset)
        self.settingsMenu.sigSavePresetAsRequested.connect(self.savePresetAs)
        self.settingsMenu.sigResetRequested.connect(self.resetToolbox)

        self.settingsMenu.sigAddSectionRequested.connect(self.addSection)
        self.settingsMenu.sigEditSectionRequested.connect(self.editSection)
        self.settingsMenu.sigDuplicateSectionRequested.connect(self.duplicateSection)
        self.settingsMenu.sigDeleteSectionRequested.connect(self.deleteSection)

        self.settingsMenu.sigAddToolRequested.connect(self.addTool)
        self.settingsMenu.sigEditToolRequested.connect(self.editTool)
        self.settingsMenu.sigDuplicateToolRequested.connect(self.duplicateTool)
        self.settingsMenu.sigDeleteToolRequested.connect(self.deleteTool)

        self.updateStylesheet()

        GlobalEvents().SIGNAL_TOOLBOX_LAYOUT_UPDATED.connect(self.onTouchifyReload)
    
    def setup(self, instance: "TouchifyWindow"):
        self.api_window = instance.api_window
        self.managers = instance.managers
        self.updateToolbox()

    #region Actions

    def updateToolbox(self):
        self._isNotLoading = False

        self.toolbox.reset()
        self._toolboxItems.clear()
        self._toolboxItems = []

        layout_config = self.settingsManager.loadLayout()
        self.containerLoader.Sync(layout_config)
        current_priority = 0

        self.settingsMenu.setCurrentPreset(self.settingsManager.getCurrentToolboxId())

        orientation = Qt.Orientation.Vertical
        match layout_config.orientation_mode:
            case ToolboxData.OrientationMode.Dynamic:
                self._isDynamicOrientation = True
            case ToolboxData.OrientationMode.Vertical:
                self._isDynamicOrientation = False
                orientation = Qt.Orientation.Vertical
            case ToolboxData.OrientationMode.Horizontal:
                self._isDynamicOrientation = False
                orientation = Qt.Orientation.Horizontal

        max_column_count = layout_config.column_count
        for cat in layout_config.categories:
            cat: ToolboxDataCategory
            if cat.column_count > max_column_count:
                max_column_count = cat.column_count
        
        
        for cat in layout_config.categories:
            cat: ToolboxDataCategory
            item_count = 0
            for item_index, act in enumerate(cat.items):    
                act: ToolboxDataItem
                btn = self.containerLoader.Build_Action(act)
                if btn:
                    btn.setData(act, item_index, str(uuid4()), cat.id)
                    btn.setEditMode(self.isEditMode())
                    self.toolbox.addButton(btn, cat.id, current_priority, btn.getUuid())
                    self._toolboxItems.append(btn)
                    current_priority += 1
                    item_count += 1

            if max_column_count > item_count:
                for idx in range(item_count, max_column_count):
                    btn = ToolboxEmptySpace()
                    btn.setCuuid(cat.id)
                    self.toolbox.addButton(btn, cat.id, current_priority, str(uuid4()))
                    self._toolboxItems.append(btn)
                    current_priority += 1


        self.toolbox.setIconSize(layout_config.icon_size)
        self.toolbox.setDesiredRowCount(max_column_count)
        self.toolbox.setButtonsVisible([])
        self.toolbox.applyIconSize()
        self.setOrientation(orientation)
        self.updateStylesheet()

        self._isNotLoading = True

    def updateStylesheet(self):
        layout_config = self.settingsManager.loadLayout()
        orientation = self.scrollArea.orientation()
        self.style_data = ToolboxStyles.ThemeData(layout_config, orientation)
        self.setStyleSheet(ToolboxStyles.getStyleSheet(self.style_data))

    #endregion

    #region User Actions

    def changePreset(self, id: str):
        self.settingsManager.setCurrentToolboxId(id)
        self.updateToolbox()

    def deletePreset(self):
        toolboxToDelete = self.settingsManager.loadLayout()
        toolboxRegistryKey = self.settingsManager.getCurrentRegistryKey()

        if toolboxToDelete == None or toolboxToDelete == "none":
            return
        
        shelfParentResourcePack = toolboxRegistryKey.getResourcePack()
        if shelfParentResourcePack == None:
            return
        
        shelfParentResourcePack.toolboxes.remove(toolboxToDelete)

        self.settingsManager.setCurrentToolboxId("none")
        self.updateToolbox()

    def savePresetAs(self):
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), ToolboxClasses.PresetSaveAs())
        if self.propertyEditor.exec_():
            editorResults: ToolboxClasses.PresetSaveAs = self.propertyEditor.editableConfig

            selectedResourcePackIndex: int = int(editorResults.resource_pack) - 1
            if selectedResourcePackIndex <= -1: return

            selectedResourcePack = TouchifySettings.resourcePacks()[selectedResourcePackIndex]
            result = ToolboxData()
            result.update(deepcopy(self.settingsManager.loadLayout()))
            result.preset_name = editorResults.display_name
            selectedResourcePack.toolboxes.append(result)
            self.settingsManager.saveLayout(result, False)

    def addSection(self):
        layout_config = self.settingsManager.loadLayout()

        avaliable_section_names = self.getSectionNames(layout_config)
        if not avaliable_section_names: return
        
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), ToolboxDataCategory())
        if self.propertyEditor.exec_():
            result: ToolboxDataCategory = self.propertyEditor.editableConfig
            while result.id in avaliable_section_names:
                result.id += ".clone"
            layout_config.categories.append(result)
            self.settingsManager.saveLayout(layout_config)

    def editSection(self, id: str):
        layout_config = self.settingsManager.loadLayout()
        
        avaliable_section_names = self.getSectionNames(layout_config)
        if not avaliable_section_names: return

        selected_section = self.getSectionByUUID(layout_config, id)
        if not selected_section: return

        selected_section_index = layout_config.categories.index(selected_section)
        
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), selected_section)
        if self.propertyEditor.exec_():
            result: ToolboxDataCategory = self.propertyEditor.editableConfig
            while result.id in avaliable_section_names:
                result.id += ".clone"
            cached_state = self.settingsManager.loadLayout()
            cached_state.categories[selected_section_index] = result
            self.settingsManager.saveLayout(layout_config)
        
    def duplicateSection(self, id: str):
        layout_config = self.settingsManager.loadLayout()

        avaliable_section_names = self.getSectionNames(layout_config)
        if not avaliable_section_names: return
        
        selected_section = self.getSectionByUUID(layout_config, id)
        if not selected_section: return
        
        new_section = deepcopy(selected_section)
        while new_section.id in avaliable_section_names:
            new_section.id += ".clone"
        layout_config.categories.append(new_section)
        self.settingsManager.saveLayout(layout_config)

    def deleteSection(self, id: str):
        layout_config = self.settingsManager.loadLayout()
        
        selected_section = self.getSectionByUUID(layout_config, id)
        if not selected_section: return
        
        layout_config.categories.remove(selected_section)
        self.settingsManager.saveLayout(layout_config)

    def addTool(self, section_id: str):
        layout_config = self.settingsManager.loadLayout()

        selected_section = self.getSectionByUUID(layout_config, section_id)
        if not selected_section: return
        
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), ToolboxDataItem())
        if self.propertyEditor.exec_():
            result: ToolboxDataItem = self.propertyEditor.editableConfig
            selected_section.items.append(result)
            self.settingsManager.saveLayout(layout_config)

    def editTool(self, section_id: str, tool_id: str):
        layout_config = self.settingsManager.loadLayout()

        selected_section = self.getSectionByUUID(layout_config, section_id)
        if not selected_section: return

        selected_button = self.getToolByUUID(layout_config, section_id, tool_id)
        if not selected_button: return

        selected_item = selected_button._data
        selected_item_index = selected_button._dataIndex
        if len(selected_section.items) < selected_item_index or selected_item_index < 0: return

        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), selected_item)
        if self.propertyEditor.exec_():
            result: ToolboxDataItem = self.propertyEditor.editableConfig
            selected_section.items[selected_item_index] = result
            self.settingsManager.saveLayout(layout_config)

    def moveTool(self, section_id: str, tool_id: str, target_section_id: str, target_tool_id: str, direction: str):
        layout_config = self.settingsManager.loadLayout()

        selected_section = self.getSectionByUUID(layout_config, section_id)
        if not selected_section: return

        selected_button = self.getToolByUUID(layout_config, section_id, tool_id)
        if not selected_button: return

        targeted_section = self.getSectionByUUID(layout_config, target_section_id)
        if not targeted_section: return


        selected_item_index = selected_button._dataIndex
        if len(selected_section.items) < selected_item_index or selected_item_index < 0: return

        if target_tool_id != None: 
            # Insert the button next to the target button
            targeted_button = self.getToolByUUID(layout_config, target_section_id, target_tool_id)
            if not targeted_button: return
            
            targeted_item_index = targeted_button._dataIndex
            if len(targeted_section.items) < targeted_item_index or targeted_item_index < 0: return

            item_to_move = selected_section.items.pop(selected_item_index)

            if direction == 'right' and len(targeted_section.items) != targeted_item_index + 1:
                targeted_section.items.insert(targeted_item_index + 1, item_to_move)
            else:
                targeted_section.items.insert(targeted_item_index, item_to_move)
        else: 
            # In the event that a section has no target button, just append it
            item_to_move = selected_section.items.pop(selected_item_index)
            targeted_section.items.append(item_to_move)

        self.settingsManager.saveLayout(layout_config)

    def duplicateTool(self, section_id: str, tool_id: str):
        layout_config = self.settingsManager.loadLayout()

        selected_section = self.getSectionByUUID(layout_config, section_id)
        if not selected_section: return

        selected_button = self.getToolByUUID(layout_config, section_id, tool_id)
        if not selected_button: return

        selected_item = selected_button._data
        selected_item_index = selected_button._dataIndex
        if len(selected_section.items) < selected_item_index or selected_item_index < 0: return
        
        selected_section.items.append(deepcopy(selected_item))
        self.settingsManager.saveLayout(layout_config)

    def deleteTool(self, section_id: str, tool_id: str):
        layout_config = self.settingsManager.loadLayout()

        selected_section = self.getSectionByUUID(layout_config, section_id)
        if not selected_section: return

        selected_button = self.getToolByUUID(layout_config, section_id, tool_id)
        if not selected_button: return

        selected_item_index = selected_button._dataIndex
        if len(selected_section.items) < selected_item_index or selected_item_index < 0: return

        selected_section.items.pop(selected_item_index)
        self.settingsManager.saveLayout(layout_config)

    def resetToolbox(self):
        self.settingsManager.saveLayout(ToolboxData())

    def editToolbox(self):
        layout_config = self.settingsManager.loadLayout()
        self.propertyEditor = PluginOptions.Setup(self.propertyEditor, self.api_window.qwindow.window(), layout_config)
        if self.propertyEditor.exec_():
            result: ToolboxData = self.propertyEditor.editableConfig
            cached_state = self.settingsManager.loadLayout()
            cached_state.update(result)
            self.settingsManager.saveLayout(cached_state)

    #endregion

    #region Get / Set

    def getSectionNames(self, layout_config: ToolboxData):
        sections: list[ToolboxDataCategory] = layout_config.categories
        if len(sections) == 0: return

        avaliable_section_names: list[str] = (x.id for x in sections)
        return avaliable_section_names

    def getSectionByUUID(self, layout_config: ToolboxData, section_uuid: str):
        sections: list[ToolboxDataCategory] = layout_config.categories
        if len(sections) == 0: return None
    
        selected_section = next((x for x in sections if x.id == section_uuid), None)
        if selected_section == None or not isinstance(selected_section, ToolboxDataCategory): return None

        return selected_section

    def getToolByUUID(self, layout_config: ToolboxData, section_uuid: str, tool_uuid: str):
        sections: list[ToolboxDataCategory] = layout_config.categories
        if len(sections) == 0: return None
    
        selected_section = next((x for x in sections if x.id == section_uuid), None)
        if selected_section == None or not isinstance(selected_section, ToolboxDataCategory): return None

        selected_button = next((x for x in self._toolboxItems if isinstance(x, ToolboxButton) and x.getUuid() == tool_uuid))
        if selected_button == None or not isinstance(selected_button, ToolboxButton): return None

        return selected_button
        

    def isEditMode(self):
        return self.settingsMenu.editModeAction.isChecked()

    def setOrientation(self, orientation: Qt.Orientation):
        self.scrollArea.setOrientation(orientation)
        self.updateStylesheet()

    #endregion

    #region Events

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.isFloating() and self._isNotLoading and self._isDynamicOrientation:
            if (self.width() > self.height()):
                self.setOrientation(Qt.Orientation.Horizontal)
            else:
                self.setOrientation(Qt.Orientation.Vertical)

    #endregion

    #region Signals


    def onToolContextMenu(self, section_uuid: str, item_uuid: str, pos: QPoint):
        self.settingsMenu.setCurrentItem(section_uuid, item_uuid)
        self.settingsMenu.refreshActions()
        self.settingsMenu.exec_(pos)

    def onSectionContextMenu(self, section_uuid: str, pos: QPoint):
        self.settingsMenu.setCurrentItem(section_uuid, None)
        self.settingsMenu.refreshActions()
        self.settingsMenu.exec_(pos)

    def onContextMenu(self, pos: QPoint):
        self.settingsMenu.setCurrentItem(None, None)
        self.settingsMenu.refreshActions()
        self.settingsMenu.exec_(pos)

    def onToolDragStarted(self, section_uuid: str, tool_uuid: str):
        self._drag_section_uuid = section_uuid
        self._drag_tool_uuid = tool_uuid
        self.drag_highlight_timer.start()

    def onToolDragEnded(self, section_uuid: str, tool_uuid: str):
        self.drag_highlight_timer.stop()
        self._drag_section_uuid = None
        self._drag_tool_uuid = None
        self._drop_overlay.set_position(None)

        if self._drag_last_button and self._drag_last_position:
            if isinstance(self._drag_last_button, ToolboxButton):
                target_cuuid = self._drag_last_button.getCuuid()
                target_uuid = self._drag_last_button.getUuid()
            elif isinstance(self._drag_last_button, ToolboxEmptySpace):
                target_cuuid = self._drag_last_button.getCuuid()
                target_uuid = None
            else:
                target_cuuid = None
                target_uuid = None
                
            self.moveTool(section_uuid, tool_uuid, target_cuuid, target_uuid, self._drag_last_position)

        self._drag_last_button = None
        self._drag_last_position = None

    def onToolDragging(self):      
        cursor_pos = QCursor.pos()

        # Find which button the cursor is over
        hovered_button = None
        for btn in self._toolboxItems:
            if isinstance(btn, ToolboxButton) and btn.matches(self._drag_section_uuid, self._drag_tool_uuid):
                continue
            
            btn_global_pos = btn.mapToGlobal(QPoint(0, 0))
            btn_rect = btn.geometry()
            btn_right = btn_global_pos.x() + btn_rect.width()
            btn_bottom = btn_global_pos.y() + btn_rect.height()
            
            if (btn_global_pos.x() <= cursor_pos.x() <= btn_right and
                btn_global_pos.y() <= cursor_pos.y() <= btn_bottom):
                hovered_button = btn
                break

        if hovered_button != self._drag_last_button: 
            self._drag_last_button = hovered_button

        if hovered_button:
            frame_size = QRect(hovered_button.mapTo(self, QPoint(0, 0)), hovered_button.size())
            btn_global_pos = hovered_button.mapToGlobal(QPoint(0, 0))
            local_x = cursor_pos.x() - btn_global_pos.x()
            #local_y = cursor_pos.y() - btn_global_pos.y()

            is_left = local_x < hovered_button.width() / 2
            #is_top = local_y < hovered_button.height() / 2

            new_position = 'left' if is_left else 'right'

            if new_position != self._drag_last_position:
                self._drag_last_position = new_position
            
            self._drop_overlay.setGeometry(frame_size)
            self._drop_overlay.set_position(new_position)
            self.update()
        else:
            self._drop_overlay.set_position(None)
            self.update()
    
    def onEditModeChanged(self, enabled: bool):
        self.toolbox.setEditMode(enabled)
        for widget in self._toolboxItems:
            if isinstance(widget, ToolboxButton):
                button: ToolboxButton = widget
                button.setEditMode(enabled)
        

    def onTouchifyReload(self):
        self.updateToolbox()

    def onThemeChanged(self):
        self.updateToolbox()

    def updatePalette(self):
        pass

    def canvasChanged(self, canvas):
        pass
        
    #endregion




