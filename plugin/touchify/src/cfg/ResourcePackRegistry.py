from touchify.src.cfg.ResourcePack import ResourcePack
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
import os
from touchify.paths import BASE_DIR
import shutil

HAS_ALREADY_LOADED: bool = False

class ResourcePackRegistry:

    def __defaults__(self):
        self.presets: TypedList[ResourcePack] = []

    def __init__(self) -> None:
        self.__defaults__()
        self.INTERNAL_ROOT_DIRECTORY = os.path.join(BASE_DIR, 'configs', 'resources')
        self.INTERNAL_active_files: list[str] = []
        self.load()

    def load(self):
        self.presets.clear()
        self.INTERNAL_active_files.clear()

        results = []

        directories = [f for f in os.listdir(self.INTERNAL_ROOT_DIRECTORY) if os.path.isdir(os.path.join(self.INTERNAL_ROOT_DIRECTORY, f))]
        for folderName in directories:
            fullFolderPath = os.path.join(self.INTERNAL_ROOT_DIRECTORY, folderName)
            self.INTERNAL_active_files.append(fullFolderPath)
            item = ResourcePack(fullFolderPath)
            if item.isValid():
                item.INTERNAL_FILEPATH_ID = fullFolderPath
                item.INTERNAL_FILENAME_ID = folderName
                item.INTERNAL_UUID_ID = folderName
                item.INTERNAL_FILESYSTEM_MANAGED = True
                results.append(item)
        
        self.presets = TypedList(results, ResourcePack)


    
    def save(self):

        found_files: list[str] = []

        for item in self.presets:
            item: ResourcePack
    
            if not hasattr(item, "INTERNAL_FILESYSTEM_MANAGED"):
                folderPath = os.path.join(BASE_DIR, 'configs', 'resources')
                registryName = FileExtensions.fileStringify(item.metadata.registry_id)

                path = FileExtensions.uniquify(os.path.join(folderPath, registryName))
                if os.path.exists(path): os.remove(path)
                name = os.path.basename(path)
                uuid = name

                os.mkdir(path)

                item.INTERNAL_ROOT_DIRECTORY = path
                item.INTERNAL_FILEPATH_ID = path
                item.INTERNAL_FILENAME_ID = name
                item.INTERNAL_UUID_ID = uuid
                item.INTERNAL_FILESYSTEM_MANAGED = True

            filePath: str = item.INTERNAL_ROOT_DIRECTORY
            found_files.append(filePath)
            item.save()
            

        removed_files: list[str] = list(set(self.INTERNAL_active_files).difference(found_files))
        for file in removed_files:
            if os.path.exists(file):
                shutil.rmtree(file)
            self.INTERNAL_active_files.remove(file)
            
    def propertygrid_hidden(self):
        return [ ]

    def propertygrid_labels(self):
        labels = {}
        labels["presets"] = "Presets"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["presets"] = {"type": "add_remove_edit_only"}
        return restrictions
