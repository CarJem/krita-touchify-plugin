import copy
from touchify.src.cfg.action.CfgTouchifyAction import CfgTouchifyAction
from touchify.src.cfg.resources.ResourcePack_Metadata import ResourcePack_Metadata
import os

from touchify.src.cfg.toolbox.CfgToolbox import CfgToolbox
from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
from touchify.src.cfg.widget_pad.CfgWidgetPadPreset import CfgWidgetPadPreset
from touchify.src.ext.JsonExtensions import JsonExtensions
from touchify.src.ext.types.TypedList import TypedList

HAS_ALREADY_LOADED: bool = False

class ResourcePack:
    metadata: ResourcePack_Metadata | None = None
    components: TypedList[CfgTouchifyAction] = TypedList(None, CfgTouchifyAction)
    toolshelves: TypedList[CfgToolshelf] = TypedList(None, CfgToolshelf)
    toolboxes: TypedList[CfgToolbox] = TypedList(None, CfgToolbox)
    widget_layouts: TypedList[CfgWidgetPadPreset] = TypedList(None, CfgWidgetPadPreset)

    def __init__(self, location: str) -> None:
        self.ROOT_DIRECTORY = location
        self.metadata = None
        self.has_loaded = False
        self.load()

    def isValid(self):
        return self.has_loaded
    
    def load(self):

        def loadItems(subpath: str, type: type):
            result = TypedList(None, type)
            files = [f for f in os.listdir(subpath) if os.path.isfile(os.path.join(subpath, f))]

            for fileName in files:
                filePath = os.path.join(subpath, fileName)
                if fileName.lower().endswith(".json"):
                    _item = JsonExtensions.loadClass(filePath, type)
                    _item.INTERNAL_FILEPATH_ID = filePath
                    result.append(_item)
                    
            return result


        self.has_loaded = False
        try:
            contents = os.listdir(self.ROOT_DIRECTORY)
            for contentName in contents:
                contentPath = os.path.join(self.ROOT_DIRECTORY, contentName)
                if os.path.isfile(contentPath) and contentName == "metadata.json":
                    self.metadata = JsonExtensions.loadClass(contentPath, ResourcePack_Metadata)

                elif os.path.isdir(contentPath) and contentName == "components":
                    self.components = loadItems(contentPath, CfgTouchifyAction)

                elif os.path.isdir(contentPath) and contentName == "toolboxes":
                    self.toolboxes = loadItems(contentPath, CfgToolbox)

                elif os.path.isdir(contentPath) and contentName == "toolshelves":
                    self.toolshelves = loadItems(contentPath, CfgToolshelf)

                elif os.path.isdir(contentPath) and contentName == "widget_layouts":
                    self.widget_layouts = loadItems(contentPath, CfgWidgetPadPreset)

            self.has_loaded = True
        except Exception as err:
            print(err)
            self.has_loaded = False
                

                


    def save(self):

        def saveItem(subItem: any):
            if hasattr(subItem, "INTERNAL_FILEPATH_ID"):
                filePath: str = subItem.INTERNAL_FILEPATH_ID
                outputData = copy.deepcopy(subItem)
                del outputData.INTERNAL_FILEPATH_ID
                JsonExtensions.saveClass(outputData, filePath)

        JsonExtensions.saveClass(self.metadata, os.path.join(self.ROOT_DIRECTORY, "metadata.json"))

        for component in self.components:
            saveItem(component)
            
        for toolbox in self.toolboxes:
            saveItem(toolbox)

        for toolshelf in self.toolshelves:
            saveItem(toolshelf)

        for layout in self.widget_layouts:
            saveItem(layout)



            

            
    def propertygrid_hidden(self):
        return [ "LAST_FILES", "ROOT_DIRECTORY" ]

    def propertygrid_labels(self):
        labels = {}
        labels["components"] = "Components"
        labels["metadata"] = "Metadata"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["metadata"] = {"type": "expandable"}
        return restrictions
