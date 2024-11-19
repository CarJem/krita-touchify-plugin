from .toolbox.CfgToolbox import *
from ..ext.types.TypedList import TypedList
from ..ext.JsonExtensions import JsonExtensions as Extensions
import os, json
from ...paths import BASE_DIR

HAS_ALREADY_LOADED: bool = False
   
class CfgToolboxRegistry:
    presets: TypedList[CfgToolbox] = []


    def __init__(self) -> None:
        self.ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'toolboxes')
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
        global HAS_ALREADY_LOADED

        if HAS_ALREADY_LOADED:
            return

        presetList = {}
        files = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isfile(os.path.join(self.ROOT_DIRECTORY, f))]
        for file in files:
            if file.lower().endswith(".json"):
                item: CfgToolbox = self.loadClass(file, CfgToolbox)
                presetList[item.preset_name] = item.__dict__

        obj = {
            "presets":  [presetList[key] for key in sorted(presetList.keys(), reverse=True)]
        }

        mappings = json.loads(json.dumps(obj, default=lambda o: o.__dict__, indent=4))
        self.presets = Extensions.init_list(mappings, "presets", CfgToolbox)

        HAS_ALREADY_LOADED = True


    
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
        return [ "LAST_FILES", "ROOT_DIRECTORY" ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


