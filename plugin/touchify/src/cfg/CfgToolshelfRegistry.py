from ..variables import TOUCHIFY_ID_SETTINGS_TOOLSHELF
from ..ext.KritaSettings import KritaSettings
from .toolshelf.CfgToolshelf import *
from ..ext.types.TypedList import TypedList
from ..ext.JsonExtensions import JsonExtensions as Extensions
import os, json
from ...paths import BASE_DIR


   
class CfgToolshelfRegistry:
    presets: TypedList[CfgToolshelf] = []


    HAS_ALREADY_LOADED: bool = False


    def __init__(self, key: str) -> None:
        self.HAS_ALREADY_LOADED = False
        self.ROOT_KEY = key
        self.ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'toolshelfs', self.ROOT_KEY)
        self.load()


    def loadClass(self, configName, type):
        try:
            CONFIG_FILE = os.path.join(self.ROOT_DIRECTORY, configName)
            with open(CONFIG_FILE) as f:
                return type(**json.load(f))
        except:
            return type()
            
    def saveClass(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.ROOT_DIRECTORY, configName)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, default=lambda o: o.__dict__, indent=4)

    def load(self):
        if self.HAS_ALREADY_LOADED:
            return

        presetList = []
        files = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isfile(os.path.join(self.ROOT_DIRECTORY, f))]
        for file in files:
            if file.lower().endswith(".json"):
                item: CfgToolshelf = self.loadClass(file, CfgToolshelf)
                presetList.append(item.__dict__)

        obj = {
            "presets": presetList
        }

        mappings = json.loads(json.dumps(obj, default=lambda o: o.__dict__, indent=4))
        presets_real = Extensions.default_assignment(mappings, "presets", [])
        self.presets = Extensions.list_assignment(presets_real, CfgToolshelf)

        self.HAS_ALREADY_LOADED = True
    
    def save(self):
        files = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isfile(os.path.join(self.ROOT_DIRECTORY, f))]
        for fileName in files:
            filePath = os.path.join(self.ROOT_DIRECTORY, fileName)
            if os.path.exists(filePath) and os.path.isfile(filePath):
                os.remove(filePath)

        for preset in self.presets:
            fileName = preset.getFileName() + ".json"
            self.saveClass(preset, fileName)


    def propertygrid_hidden(self):
        return [ "LAST_FILES", "ROOT_DIRECTORY", "ROOT_KEY", "HAS_ALREADY_LOADED" ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions
    

    def getActiveIndex(self):
        return KritaSettings.readSettingInt(TOUCHIFY_ID_SETTINGS_TOOLSHELF, f"{self.ROOT_KEY.capitalize()}_SelectedPreset", 0)

    def getActive(self):
        result: CfgToolshelf = None
        selectedPresetIndex = self.getActiveIndex()

        if 0 <= selectedPresetIndex < len(self.presets):
            result: CfgToolshelf = self.presets[selectedPresetIndex]
        elif len(self.presets) >= 1:
            selectedPresetIndex = 0
            result: CfgToolshelf = self.presets[selectedPresetIndex]
        else:
            selectedPresetIndex = 0
            result = CfgToolshelf()
        
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_TOOLSHELF, f"{self.ROOT_KEY.capitalize()}_SelectedPreset", selectedPresetIndex, False)  
        return result
    

    def setActive(self, index: int):
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_TOOLSHELF, f"{self.ROOT_KEY.capitalize()}_SelectedPreset", index, False) 

