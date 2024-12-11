import copy
import types
from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.cfg.ResourcePackMetadata import ResourcePackMetadata
import os

from touchify.src.cfg.canvas_preset.CfgTouchifyActionCanvasPreset import CfgTouchifyActionCanvasPreset
from touchify.src.cfg.docker_group.CfgTouchifyActionDockerGroup import CfgTouchifyActionDockerGroup
from touchify.src.cfg.popup.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.cfg.toolbox.CfgToolbox import CfgToolbox
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
from touchify.src.cfg.widget_pad.CfgWidgetPadPreset import CfgWidgetPadPreset
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions
from touchify.src.ext.types.TypedList import TypedList

from touchify.paths import BASE_DIR

HAS_ALREADY_LOADED: bool = False

class ResourcePack:

    def __defaults__(self):
        self.metadata: ResourcePackMetadata | None = None
        self.components: TypedList[CfgTouchifyAction] = []
        self.toolshelves: TypedList[CfgToolshelf] = []
        self.toolboxes: TypedList[CfgToolbox] = []
        self.widget_layouts: TypedList[CfgWidgetPadPreset] = []
        self.popups: TypedList[CfgTouchifyActionPopup] = []
        self.canvas_presets: TypedList[CfgTouchifyActionCanvasPreset] = []
        self.docker_groups: TypedList[CfgTouchifyActionDockerGroup] = []

    def __init__(self, location: str = "") -> None:
        self.__defaults__()
        if location == "":
            self.metadata = ResourcePackMetadata()
            self.INTERNAL_ROOT_DIRECTORY = ""
            self.INTERNAL_has_loaded = True
            self.INTERNAL_active_files: list[str] = []
        else:
            self.INTERNAL_has_loaded = False
            self.INTERNAL_ROOT_DIRECTORY = location
            self.INTERNAL_active_files: list[str] = []

            self.metadata = None
            self.load()

    def forceLoad(self):
        pass


    def __str__(self):
        if self.INTERNAL_has_loaded:
            if self.metadata != None:
                return self.metadata.registry_name
        
        return "Unknown Resource Pack"

    def isValid(self):
        return self.INTERNAL_has_loaded and self.metadata != None
    
    def load(self):

        def loadItems(subpath: str, type: type):
            result = []
            files = [f for f in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, f))]

            for fileName in files:
                filePath = os.path.join(subpath, fileName)
                if fileName.lower().endswith(".json"):
                    _item = JsonExtensions.loadClass(filePath, type)
                    self.INTERNAL_active_files.append(filePath)
                    _item.propertygrid_on_duplicate = types.MethodType(ResourcePack.onDuplicateListItem, _item)
                    _item.INTERNAL_FILEPATH_ID = filePath
                    _item.INTERNAL_FILENAME_ID = fileName
                    _item.INTERNAL_UUID_ID = fileName[:-4]
                    _item.INTERNAL_FILESYSTEM_MANAGED = True
                    result.append(_item)
                    
            return TypedList(result, type)


        self.INTERNAL_has_loaded = False
        try:
            contents = os.listdir(self.INTERNAL_ROOT_DIRECTORY)
            for contentName in contents:
                contentPath = os.path.join(self.INTERNAL_ROOT_DIRECTORY, contentName)
                if os.path.isfile(contentPath) and contentName == "metadata.json":
                    self.metadata = JsonExtensions.loadClass(contentPath, ResourcePackMetadata)

                elif os.path.isdir(contentPath) and contentName == "components":
                    self.components = loadItems(contentPath, CfgTouchifyAction)

                elif os.path.isdir(contentPath) and contentName == "toolboxes":
                    self.toolboxes = loadItems(contentPath, CfgToolbox)

                elif os.path.isdir(contentPath) and contentName == "toolshelves":
                    self.toolshelves = loadItems(contentPath, CfgToolshelf)

                elif os.path.isdir(contentPath) and contentName == "widget_layouts":
                    self.widget_layouts = loadItems(contentPath, CfgWidgetPadPreset)

                elif os.path.isdir(contentPath) and contentName == "docker_groups":
                    self.docker_groups = loadItems(contentPath, CfgTouchifyActionDockerGroup)

                elif os.path.isdir(contentPath) and contentName == "popups":
                    self.popups = loadItems(contentPath, CfgTouchifyActionPopup)

                elif os.path.isdir(contentPath) and contentName == "canvas_presets":
                    self.canvas_presets = loadItems(contentPath, CfgTouchifyActionCanvasPreset)

            self.INTERNAL_has_loaded = True
        except Exception as err:
            print(err)
            self.INTERNAL_has_loaded = False


    def save(self):

        if self.INTERNAL_ROOT_DIRECTORY == "":
            resource_pack_directory = os.path.join(BASE_DIR, 'configs', 'resources')
            folder_name = FileExtensions.fileStringify(str(self.metadata.registry_id))
            self.INTERNAL_ROOT_DIRECTORY = FileExtensions.uniquify(os.path.join(resource_pack_directory, folder_name))

        found_files: list[str] = []

        def createFileDetails(item: any, folderPath: str):
            if hasattr(item, "getFileName"):
                result: str = item.getFileName()
            else:
                result: str = FileExtensions.fileStringify(str(item))

            path = FileExtensions.uniquify(os.path.join(folderPath, f"{result}.json"))
            name = os.path.basename(path)
            uuid = name[:-4]

            return uuid, name, path

        def saveItems(list: TypedList, folderPath: str):
            if not os.path.exists(folderPath):
                os.mkdir(folderPath)

            for item in list:
                if not hasattr(item, "INTERNAL_FILESYSTEM_MANAGED"):

                    uuid, name, path = createFileDetails(item, folderPath)

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

                JsonExtensions.saveClass(outputData, filePath)
            


        JsonExtensions.saveClass(self.metadata, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "metadata.json"))
        saveItems(self.components, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "components"))
        saveItems(self.toolboxes, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "toolboxes"))
        saveItems(self.toolshelves, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "toolshelves"))
        saveItems(self.widget_layouts, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "widget_layouts"))
        saveItems(self.popups, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "popups"))
        saveItems(self.docker_groups, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "docker_groups"))
        saveItems(self.canvas_presets, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "canvas_presets"))

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
        return [  ]

    def propertygrid_labels(self):
        labels = {}
        labels["components"] = "Components"
        labels["metadata"] = "Metadata"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["metadata"] = {"type": "expandable"}
        return restrictions
