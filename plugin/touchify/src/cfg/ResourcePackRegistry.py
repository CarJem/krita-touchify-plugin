import copy
import types
from touchify.src.cfg.ResourcePack import ResourcePack
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
import os
from touchify.paths import BASE_DIR

HAS_ALREADY_LOADED: bool = False

class ResourcePackRegistry:
    presets: TypedList[ResourcePack] = TypedList(None, ResourcePack)


    def __init__(self) -> None:
        self.INTERNAL_ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'resources')
        self.INTERNAL_active_files: list[str] = []
        self.load()

    def load(self):
        self.presets.clear()
        self.INTERNAL_active_files.clear()

        directories = [f for f in os.listdir(self.INTERNAL_ROOT_DIRECTORY) if os.path.isdir(os.path.join(self.INTERNAL_ROOT_DIRECTORY, f))]
        for folderName in directories:
            fullFolderPath = os.path.join(self.INTERNAL_ROOT_DIRECTORY, folderName)
            self.INTERNAL_active_files.append(fullFolderPath)
            item = ResourcePack(fullFolderPath, folderName)
            item.propertygrid_on_duplicate = types.MethodType(ResourcePackRegistry.onDuplicateListItem, item)
            item.INTERNAL_FILEPATH_ID = fullFolderPath
            item.INTERNAL_FILENAME_ID = folderName
            item.INTERNAL_UUID_ID = folderName
            item.INTERNAL_FILESYSTEM_MANAGED = True
            self.presets.append(item)


    
    def save(self):

        found_files: list[str] = []

        def createFileDetails(item: ResourcePack):


            return uuid, name, path

        for item in self.presets:
            item: ResourcePack
    
            if not hasattr(item, "INTERNAL_FILESYSTEM_MANAGED"):
                name = FileExtensions.uniquify(f"{FileExtensions.fileStringify(item.metadata.registry_id)}.json")
                uuid = name[:-5]
                path = os.path.join(self.INTERNAL_ROOT_DIRECTORY, name)

                item.INTERNAL_FILEPATH_ID = path
                item.INTERNAL_FILENAME_ID = name
                item.INTERNAL_UUID_ID = uuid
                item.INTERNAL_FILESYSTEM_MANAGED = True

            filePath: str = item.INTERNAL_FILEPATH_ID
            print(item.INTERNAL_FILEPATH_ID)
            found_files.append(filePath)

            outputData = copy.deepcopy(item)
            
            if hasattr(item, "INTERNAL_FILEPATH_ID"):
                del outputData.INTERNAL_FILEPATH_ID
            if hasattr(item, "INTERNAL_FILENAME_ID"):
                del outputData.INTERNAL_FILENAME_ID
            if hasattr(item, "INTERNAL_FILESYSTEM_MANAGED"):
                del outputData.INTERNAL_FILESYSTEM_MANAGED
            if hasattr(item, "INTERNAL_UUID_ID"):
                del outputData.INTERNAL_UUID_ID
            if hasattr(item, "propertygrid_on_duplicate"):
                del outputData.propertygrid_on_duplicate

            item.save()
            

        removed_files: list[str] = list(set(self.INTERNAL_active_files).difference(found_files))
        for file in removed_files:
            if os.path.exists(file):
                os.remove(file)
            self.INTERNAL_active_files.remove(file)

    def onDuplicateListItem(self):
        if hasattr(self, "INTERNAL_FILESYSTEM_MANAGED"):
            del self.INTERNAL_FILEPATH_ID
            del self.INTERNAL_FILENAME_ID
            del self.INTERNAL_FILESYSTEM_MANAGED
            del self.INTERNAL_UUID_ID
            
    def propertygrid_hidden(self):
        return [ ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions
