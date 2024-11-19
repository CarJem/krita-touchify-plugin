from touchify.src.variables import TOUCHIFY_ID_SETTINGS_WIDGETPAD
from touchify.src.ext.KritaSettings import KritaSettings
from touchify.src.cfg.widget_pad.CfgWidgetPadPreset import *
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
import os, json
from touchify.paths import BASE_DIR


   
class CfgWidgetPadRegistry:
    presets: TypedList[CfgWidgetPadPreset] = []


    HAS_ALREADY_LOADED: bool = False


    def __init__(self) -> None:
        self.HAS_ALREADY_LOADED = False
        self.ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'widget_pads')
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

        presetList = {}
        files = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isfile(os.path.join(self.ROOT_DIRECTORY, f))]
        for file in files:
            if file.lower().endswith(".json"):
                item: CfgWidgetPadPreset = self.loadClass(file, CfgWidgetPadPreset)
                presetList[item.preset_name] = item.__dict__

        obj = {
            "presets":   [presetList[key] for key in sorted(presetList.keys(), reverse=True)]
        }

        mappings = json.loads(json.dumps(obj, default=lambda o: o.__dict__, indent=4))
        self.presets = Extensions.init_list(mappings, "presets", CfgWidgetPadPreset)

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
        return [ "LAST_FILES", "ROOT_DIRECTORY", "HAS_ALREADY_LOADED" ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions
    

    def getActiveIndex(self):
        return KritaSettings.readSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", 0)

    def getActive(self):
        result: CfgWidgetPadPreset = None
        selectedPresetIndex = self.getActiveIndex()

        if 0 <= selectedPresetIndex < len(self.presets):
            result: CfgWidgetPadPreset = self.presets[selectedPresetIndex]
        elif len(self.presets) >= 1:
            selectedPresetIndex = 0
            result: CfgWidgetPadPreset = self.presets[selectedPresetIndex]
        else:
            selectedPresetIndex = 0
            result = CfgWidgetPadPreset()
        
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", selectedPresetIndex, False)  
        return result
    

    def setActive(self, index: int):
        KritaSettings.writeSettingInt(TOUCHIFY_ID_SETTINGS_WIDGETPAD, "SelectedPreset", index, False) 

