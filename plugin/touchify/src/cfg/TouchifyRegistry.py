import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.paths import BASE_DIR
from touchify.src.cfg.HotkeyRegistry import HotkeyRegistry
from touchify.src.cfg.ResourcePackRegistry import ResourcePackRegistry
from touchify.src.cfg.PreferencesRegistry import PreferencesRegistry
from touchify.src.variables import *

from touchify.src.ext.Extensions import *

import json


class TouchifyRegistry:

    def __init__(self):
        self.__base_dir__ = BASE_DIR            
        self.resources: ResourcePackRegistry = ResourcePackRegistry()
        self.hotkeys: HotkeyRegistry = HotkeyRegistry()
        self.preferences: PreferencesRegistry = PreferencesRegistry()
        self.load()

    def loadClass(self, configName, type):
        try:
            CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
            with open(CONFIG_FILE) as f:
                return type(**json.load(f))
        except:
            return type()
            
    def saveClass(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, default=lambda o: o.__dict__, indent=4)

    def propertygrid_labels(self):
        labels = {}
        labels["registries"] = "Registries"
        labels["resources"] = "Resource Packs"
        labels["hotkeys"] = "Hotkeys"
        labels["preferences"] = "Preferences"
        return labels
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["registries"] = {"items": ["resources", "hotkeys", "preferences"], "use_labels": True, "flip_labels": True}
        return row
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["resources"] = {"type": "expandable"}
        restrictions["hotkeys"] = {"type": "expandable"}
        restrictions["preferences"] = {"type": "expandable"}
        return restrictions
    
    def save(self):
        self.saveClass(self.hotkeys, "hotkeys")
        self.resources.save()
        self.preferences.save()

    def load(self):
        self.hotkeys = self.loadClass("hotkeys", HotkeyRegistry)
        self.resources.load()
        self.preferences.load()
        