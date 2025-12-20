import copy
import types
from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
from touchify.src.config.script.CustomScript import CustomScript
from touchify.src.config.toolshelf.Toolshelf import Toolshelf
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.resource_pack.ResourcePackMetadata import ResourcePackMetadata
import os

from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
from touchify.src.config.docker_group.DockerGroup import DockerGroup
from touchify.src.config.popup.PopupData import PopupData
from touchify.src.config.toolbox.ToolboxData import ToolboxData
from touchify.src.config.menu.TriggerMenu import TriggerMenu
from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.alib_datatypes.TypedList import TypedList

from touchify.__env__ import RESOURCE_PACKS_DIRECTORY
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

HAS_ALREADY_LOADED: bool = False

class ResourcePack:

    def __defaults__(self):
        self.metadata: ResourcePackMetadata | None = None
        self.triggers: TypedList[Trigger] = []
        self.menus: TypedList[TriggerMenu] = []
        self.popups: TypedList[PopupData] = []
        self.docker_groups: TypedList[DockerGroup] = []
        self.canvas_presets: TypedList[CanvasPreset] = []
        self.toolboxes: TypedList[ToolboxData] = []
        self.shelves: TypedList[Toolshelf] = []
        self.scripts: TypedList[CustomScript] = []
        self.pie_wheels: TypedList[PieWheelData] = []

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
        self.triggers = TypedList(self.triggers, Trigger)
        self.menus = TypedList(self.menus, TriggerMenu)
        self.popups = TypedList(self.popups, PopupData)
        self.docker_groups = TypedList(self.docker_groups, DockerGroup)
        self.canvas_presets = TypedList(self.canvas_presets, CanvasPreset)
        self.toolboxes = TypedList(self.toolboxes, ToolboxData)
        self.shelves = TypedList(self.shelves, Toolshelf)
        self.scripts = TypedList(self.scripts, CustomScript)
        self.pie_wheels = TypedList(self.pie_wheels, PieWheelData)


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
                    _item = JsonExtensions.loadClassFromFile(filePath, type)
                    self.INTERNAL_active_files.append(filePath)
                    _item.propertygrid_on_duplicate = types.MethodType(ResourcePack.onDuplicateListItem, _item)
                    _item.INTERNAL_FILEPATH_ID = filePath
                    _item.INTERNAL_FILENAME_ID = fileName
                    _item.INTERNAL_UUID_ID = fileName[:-5]
                    _item.INTERNAL_FILESYSTEM_MANAGED = True
                    result.append(_item)
                    
            return TypedList(sorted(result, key=lambda x: x.__str__()), type)


        self.INTERNAL_has_loaded = False
        try:
            contents = os.listdir(self.INTERNAL_ROOT_DIRECTORY)
            for contentName in contents:
                contentPath = os.path.join(self.INTERNAL_ROOT_DIRECTORY, contentName)
                if os.path.isfile(contentPath) and contentName == "metadata.json":
                    self.metadata = JsonExtensions.loadClassFromFile(contentPath, ResourcePackMetadata)

                elif os.path.isdir(contentPath) and contentName == "triggers":
                    self.triggers = loadItems(contentPath, Trigger)

                elif os.path.isdir(contentPath) and contentName == "menus":
                    self.menus = loadItems(contentPath, TriggerMenu)

                elif os.path.isdir(contentPath) and contentName == "toolboxes":
                    self.toolboxes = loadItems(contentPath, ToolboxData)

                elif os.path.isdir(contentPath) and contentName == "shelves":
                    self.shelves = loadItems(contentPath, Toolshelf)

                elif os.path.isdir(contentPath) and contentName == "docker_groups":
                    self.docker_groups = loadItems(contentPath, DockerGroup)

                elif os.path.isdir(contentPath) and contentName == "popups":
                    self.popups = loadItems(contentPath, PopupData)

                elif os.path.isdir(contentPath) and contentName == "canvas_presets":
                    self.canvas_presets = loadItems(contentPath, CanvasPreset)

                elif os.path.isdir(contentPath) and contentName == "scripts":
                    self.scripts = loadItems(contentPath, CustomScript)

                elif os.path.isdir(contentPath) and contentName == "pie_wheels":
                    self.pie_wheels = loadItems(contentPath, PieWheelData)

            self.INTERNAL_has_loaded = True
        except Exception as err:
            print("Loading Resource Pack: ", err)
            self.INTERNAL_has_loaded = False


    def save(self):

        if self.INTERNAL_ROOT_DIRECTORY == "":
            resource_pack_directory = RESOURCE_PACKS_DIRECTORY
            folder_name = FileExtensions.fileStringify(str(self.metadata.registry_id))
            self.INTERNAL_ROOT_DIRECTORY = FileExtensions.uniquify(os.path.join(resource_pack_directory, folder_name))
            self.metadata.registry_id = os.path.dirname(self.INTERNAL_ROOT_DIRECTORY)

        found_files: list[str] = []

        def createFileDetails(item: any, folderPath: str):
            if hasattr(item, "getFileName"):
                result: str = item.getFileName()
            else:
                result: str = FileExtensions.fileStringify(str(item))

            path = FileExtensions.uniquify(os.path.join(folderPath, f"{result}.json"))
            name = os.path.basename(path)
            uuid = name[:-5]

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
                #print(item.INTERNAL_FILEPATH_ID)
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

                JsonExtensions.saveClassToFile(outputData, filePath)
            


        JsonExtensions.saveClassToFile(self.metadata, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "metadata.json"))
        saveItems(self.triggers, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "triggers"))
        saveItems(self.menus, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "menus"))
        saveItems(self.toolboxes, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "toolboxes"))
        saveItems(self.shelves, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "shelves"))
        saveItems(self.popups, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "popups"))
        saveItems(self.docker_groups, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "docker_groups"))
        saveItems(self.canvas_presets, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "canvas_presets"))
        saveItems(self.scripts, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "scripts"))
        saveItems(self.pie_wheels, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "pie_wheels"))

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
    
    def propertygrid_view_type(self):
        return "tabs_vertical"
    
    def propertygrid_sorted(self):
        return [
            "metadata",
            "triggers",
            "menus",
            "toolboxes",
            "shelves",
            "popups",
            "docker_groups",
            "canvas_presets",
            "pie_wheels",
            "scripts"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["triggers"] = "Triggers"
        labels["menus"] = "Menus"
        labels["toolboxes"] = "Toolboxes"
        labels["shelves"] = "Toolshelves"
        labels["popups"] = "Popups"
        labels["docker_groups"] = "Docker Groups"
        labels["canvas_presets"] = "Canvas Presets"
        labels["metadata"] = "Metadata"
        labels["pie_wheels"] = "Pie Wheels"
        labels["scripts"] = "Scripts"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["metadata"] = RS.expandable()
        restrictions["triggers"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["menus"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["toolboxes"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["shelves"] =[RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["popups"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["docker_groups"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["canvas_presets"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["scripts"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        restrictions["pie_wheels"] = [RS.listMod(RS.ListMod.Inmovable), RS.listMod(RS.ListMod.NestedTabs)]
        return restrictions
