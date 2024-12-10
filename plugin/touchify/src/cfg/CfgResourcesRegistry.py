from touchify.src.cfg.resources.ResourcePack import ResourcePack
from touchify.src.ext.types.TypedList import TypedList
import os
from touchify.paths import BASE_DIR

HAS_ALREADY_LOADED: bool = False

class CfgResourcesRegistry:
    presets: TypedList[ResourcePack] = TypedList(None, ResourcePack)


    def __init__(self) -> None:
        self.ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'resources')
        self.load()

    def load(self):
        self.presets.clear()

        directories = [f for f in os.listdir(self.ROOT_DIRECTORY) if os.path.isdir(os.path.join(self.ROOT_DIRECTORY, f))]
        for folderName in directories:
            fullFolderPath = os.path.join(self.ROOT_DIRECTORY, folderName)
            item = ResourcePack(fullFolderPath)
            self.presets.append(item)


    
    def save(self):
        for preset in self.presets:
            preset: ResourcePack
            preset.save()
            
    def propertygrid_hidden(self):
        return [ "LAST_FILES", "ROOT_DIRECTORY" ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions
