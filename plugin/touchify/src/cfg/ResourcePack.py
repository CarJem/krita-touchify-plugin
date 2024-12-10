import copy
from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.cfg.ResourcePackMetadata import ResourcePackMetadata
import os

from touchify.src.cfg.canvas_preset.CfgTouchifyActionCanvasPreset import CfgTouchifyActionCanvasPreset
from touchify.src.cfg.docker_group.CfgTouchifyActionDockerGroup import CfgTouchifyActionDockerGroup
from touchify.src.cfg.popup.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.cfg.toolbox.CfgToolbox import CfgToolbox
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
from touchify.src.cfg.widget_pad.CfgWidgetPadPreset import CfgWidgetPadPreset
from touchify.src.ext.JsonExtensions import JsonExtensions
from touchify.src.ext.types.TypedList import TypedList

HAS_ALREADY_LOADED: bool = False

class ResourcePack:
    metadata: ResourcePackMetadata | None = None
    components: TypedList[CfgTouchifyAction] = TypedList(None, CfgTouchifyAction)
    toolshelves: TypedList[CfgToolshelf] = TypedList(None, CfgToolshelf)
    toolboxes: TypedList[CfgToolbox] = TypedList(None, CfgToolbox)
    widget_layouts: TypedList[CfgWidgetPadPreset] = TypedList(None, CfgWidgetPadPreset)
    popups: TypedList[CfgTouchifyActionPopup] = TypedList(None, CfgTouchifyActionPopup)
    canvas_presets: TypedList[CfgTouchifyActionCanvasPreset] = TypedList(None, CfgTouchifyActionCanvasPreset)
    docker_groups: TypedList[CfgTouchifyActionDockerGroup] = TypedList(None, CfgTouchifyActionDockerGroup)

    def __init__(self, location: str, name: str) -> None:
        self.INTERNAL_ROOT_DIRECTORY = location
        self.INTERNAL_FILEPATH_ID = location
        self.INTERNAL_FILENAME_ID = name
        self.INTERNAL_UUID_ID = name

        self.INTERNAL_has_loaded = False
        self.INTERNAL_active_files: list[str] = []

        self.metadata = None
        self.load()

    def __str__(self):
        if self.INTERNAL_has_loaded:
            if self.metadata != None:
                return self.metadata.registry_name
        
        return "Unknown Resource Pack"

    def isValid(self):
        return self.INTERNAL_has_loaded
    
    def load(self):

        def loadItems(subpath: str, type: type):
            result = TypedList(None, type)
            files = [f for f in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, f))]

            for fileName in files:
                filePath = os.path.join(subpath, fileName)
                if fileName.lower().endswith(".json"):
                    _item = JsonExtensions.loadClass(filePath, type)
                    self.INTERNAL_active_files.append(filePath)
                    _item.INTERNAL_FILEPATH_ID = filePath
                    _item.INTERNAL_FILENAME_ID = fileName
                    _item.INTERNAL_UUID_ID = fileName[:-4]
                    _item.INTERNAL_FILESYSTEM_MANAGED = True
                    result.append(_item)
                    
            return result


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

        found_files: list[str] = []

        def saveItems(list: TypedList):
            for item in list:
                if hasattr(item, "INTERNAL_FILESYSTEM_MANAGED"):
                    filePath: str = item.INTERNAL_FILEPATH_ID
                    found_files.append(filePath)

                    outputData = copy.deepcopy(item)
                    del outputData.INTERNAL_FILEPATH_ID
                    del outputData.INTERNAL_FILENAME_ID
                    del outputData.INTERNAL_FILESYSTEM_MANAGED
                    del outputData.INTERNAL_UUID_ID
                    JsonExtensions.saveClass(outputData, filePath)
            


        JsonExtensions.saveClass(self.metadata, os.path.join(self.INTERNAL_ROOT_DIRECTORY, "metadata.json"))
        saveItems(self.components)
        saveItems(self.toolboxes)
        saveItems(self.toolshelves)
        saveItems(self.widget_layouts)
        saveItems(self.popups)
        saveItems(self.docker_groups)
        saveItems(self.canvas_presets)

        removed_files: list[str] = list(set(self.INTERNAL_active_files)(found_files))
        for file in removed_files:
            found_files



            

            
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
