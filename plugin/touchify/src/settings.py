from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.cfg.ResourcePack import ResourcePack
from touchify.src.cfg.TouchifyRegistry import TouchifyRegistry
from touchify.src.cfg.canvas_preset.CfgTouchifyActionCanvasPreset import CfgTouchifyActionCanvasPreset
from touchify.src.cfg.docker_group.CfgTouchifyActionDockerGroup import CfgTouchifyActionDockerGroup
from touchify.src.cfg.popup.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.cfg.toolbox.CfgToolbox import CfgToolbox
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
from touchify.src.cfg.PreferencesRegistry import PreferencesRegistry
from touchify.src.cfg.widget_pad.CfgWidgetPadPreset import CfgWidgetPadPreset
from touchify.src.ext.KritaSettings import KritaSettings
from touchify.src.variables import *

from touchify.src.ext.Extensions import *



class TouchifyConfig:
    def instance():
        try:
            return TouchifyConfig.__instance
        except AttributeError:
            TouchifyConfig.__instance = TouchifyConfig()
            return TouchifyConfig.__instance

    def __init__(self) -> None:
        self.notify_hooks = []
        self.hotkey_options_storage = {}
        self.cfg = TouchifyRegistry()
        
    def preferences(self) -> PreferencesRegistry:
        return self.cfg.preferences

    def getConfig(self) -> TouchifyRegistry:
        return self.cfg
    

    def getRegistryItem(self, item_id: str, type: type) -> None |\
                                                        CfgTouchifyActionPopup |\
                                                        CfgTouchifyActionDockerGroup |\
                                                        CfgTouchifyActionCanvasPreset:
        cfg = self.getConfig()
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == CfgTouchifyActionPopup:
                for item in pack.popups:
                    item: CfgTouchifyActionPopup
                    id = f"{pack.INTERNAL_FILENAME_ID}/popup/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item
            elif type == CfgTouchifyActionDockerGroup:
                for item in pack.docker_groups:
                    item: CfgTouchifyActionDockerGroup
                    id = f"{pack.INTERNAL_FILENAME_ID}/docker_group/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item
            elif type == CfgTouchifyActionCanvasPreset:
                for item in pack.canvas_presets:
                    item: CfgTouchifyActionCanvasPreset
                    id = f"{pack.INTERNAL_FILENAME_ID}/canvas_preset/{item.INTERNAL_FILENAME_ID}"
                    if item_id == id: return item

        return None
    
    def getRegistry(self, type: type) -> dict[str, any] |\
                                        dict[str,CfgTouchifyActionPopup] |\
                                        dict[str,CfgTouchifyActionDockerGroup] |\
                                        dict[str,CfgTouchifyActionCanvasPreset] |\
                                        dict[str,CfgToolshelf] |\
                                        dict[str,CfgToolbox] |\
                                        dict[str,CfgWidgetPadPreset]:
        cfg = self.getConfig()
        results: dict = {}
        for pack in cfg.resources.presets:
            pack: ResourcePack

            if type == CfgTouchifyActionPopup:
                for item in pack.popups:
                    item: CfgTouchifyActionPopup
                    id = f"{pack.INTERNAL_FILENAME_ID}/popup/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item
            elif type == CfgTouchifyActionDockerGroup:
                for item in pack.docker_groups:
                    item: CfgTouchifyActionDockerGroup
                    id = f"{pack.INTERNAL_FILENAME_ID}/docker_group/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item
            elif type == CfgTouchifyActionCanvasPreset:
                for item in pack.canvas_presets:
                    item: CfgTouchifyActionCanvasPreset
                    id = f"{pack.INTERNAL_FILENAME_ID}/canvas_preset/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item
            elif type == CfgToolshelf:
                for item in pack.toolshelves:
                    item: CfgToolshelf
                    id = f"{pack.INTERNAL_FILENAME_ID}/toolshelves/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item
            elif type == CfgToolbox:
                for item in pack.toolboxes:
                    item: CfgToolbox
                    id = f"{pack.INTERNAL_FILENAME_ID}/toolboxes/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item
            elif type == CfgWidgetPadPreset:
                for item in pack.widget_layouts:
                    item: CfgWidgetPadPreset
                    id = f"{pack.INTERNAL_FILENAME_ID}/widget_layout/{item.INTERNAL_FILENAME_ID}"
                    results[id] = item

        return results

    #region Toolshelf 

    def getActiveToolshelfId(self, registry_index: int) -> str:
        fallback_val = "none"
        if registry_index == 0:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Main", fallback_val)
        elif registry_index == 1:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Alt", fallback_val)
        elif registry_index == 2:
            return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Docker", fallback_val)
        else:
            return fallback_val

    def getActiveToolshelf(self, registry_index: int) -> CfgToolshelf:
        registry = self.getRegistry(CfgToolshelf)
        registry_selection = self.getActiveToolshelfId(registry_index)

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return CfgToolshelf()

    def setActiveToolshelf(self, registry_index: int, id: str):
        if registry_index == 0:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Main", id, False)
        elif registry_index == 1:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Alt", id, False)
        elif registry_index == 2:
            KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_TOOLSHELF, "SelectedPreset_Docker", id, False)

        self.notifyUpdate()
    
    #endregion

    #region Toolbox 

    def getActiveToolboxId(self) -> str:
        fallback_val = "none"
        return KritaSettings.readSetting(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", fallback_val)

    def getActiveToolbox(self) -> CfgToolbox:
        registry = self.getRegistry(CfgToolbox)
        registry_selection = self.getActiveToolboxId()

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return CfgToolbox()

    def setActiveToolbox(self, id: str):
        KritaSettings.writeSetting(TOUCHIFY_ID_DOCKER_TOOLBOX, "SelectedPreset", id, False)
        self.notifyUpdate()
    
    #endregion

    #region Widget Layouts 

    def getActiveWidgetLayoutId(self) -> str:
        fallback_val = "none"
        return KritaSettings.readSetting(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", fallback_val)

    def getActiveWidgetLayout(self) -> CfgWidgetPadPreset:
        registry = self.getRegistry(CfgWidgetPadPreset)
        registry_selection = self.getActiveWidgetLayoutId()

        if registry_selection in registry:
            return registry[registry_selection]    
        else: 
            return CfgWidgetPadPreset()

    def setActiveWidgetLayout(self, id: str):
        KritaSettings.writeSetting(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", id, False)
        self.notifyUpdate()
    
    #endregion

    def addHotkeyOption(self, actionName, displayName, action, parameters):
        self.hotkey_options_storage[actionName] = {
            "displayName": displayName,
            "action": action,
            "params": parameters
        }
    
    def runHotkeyOption(self, actionName: str):
        if actionName == "none":
            return
        
        if actionName not in TouchifyConfig.instance().hotkey_options_storage:
            return
        
        actionObj = TouchifyConfig.instance().hotkey_options_storage[actionName]
        params = actionObj["params"]
        action = actionObj["action"]
        
        action(**params)

    def notifyConnect(self, event):
        self.notify_hooks.append(event)

    def notifyUpdate(self):
        self.cfg.load()

        for hook in self.notify_hooks:
            hook()




