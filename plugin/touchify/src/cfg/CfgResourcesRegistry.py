import string
from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
import os, json
from touchify.paths import BASE_DIR

HAS_ALREADY_LOADED: bool = False

class CfgResourcePack:
    actions_registry: TypedList[CfgTouchifyAction] = []
    registry_id: str = "NewActRegistry"
    registry_name: str = "New Action Registry"

    json_version: int = 1


    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        self.actions_registry = Extensions.init_list(args, "actions_registry", CfgTouchifyAction)

    def __str__(self):
        return self.registry_name.replace("\n", "\\n")

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.registry_id if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

    def forceLoad(self):
        self.actions_registry = TypedList(self.actions_registry, CfgTouchifyAction)

    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["registry_id"] = "Registry ID"
        labels["registry_name"] = "Registry Name"
        labels["actions_registry"] = "Registered Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions    

class CfgResourcesRegistry:
    presets: TypedList[CfgResourcePack] = []


    def __init__(self) -> None:
        self.ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'resources')
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
        self.presets.clear()

        presetList = {}
        files = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isfile(os.path.join(self.ROOT_DIRECTORY, f))]
        for file in files:
            if file.lower().endswith(".json"):
                item: CfgResourcePack = self.loadClass(file, CfgResourcePack)
                presetList[item.registry_id] = item.__dict__

        obj = {
            "presets":  [presetList[key] for key in sorted(presetList.keys(), reverse=True)]
        }

        mappings = json.loads(json.dumps(obj, default=lambda o: o.__dict__, indent=4))
        self.presets = Extensions.init_list(mappings, "presets", CfgResourcePack)

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
