from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json
import os
from ..ext.extensions import *
    

class PopupInfo:
    text: str = ""
    action: str = ""
    icon: str = ""

    def create(args):
        obj = PopupInfo()
        Extensions.dictToObject(obj, args)
        return obj

    def __str__(self):
        return self.text.replace("\n", "\\n")
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
    
class Popup:
    id: str = ""
    btnName: str = ""
    popupType: str = "popup"
    icon: str = ""
    type: str = "actions"
    docker_id: str = ""
    opacity: float = 1.0
    grid_width: int = 3
    grid_padding: int = 2
    item_width: int = 100
    item_height: int = 100
    icon_width: int = 30
    icon_height: int = 30
    hotkeyNumber: int = 0
    items: TypedList[PopupInfo] = []


    def propertygrid_groups(self):
        action_mode_settings = [
            "opacity",
            "grid_width",
            "grid_padding",
            "icon_width", 
            "icon_height",
            "items", 
        ]

        docker_mode_settings = [
            "docker_id"
        ]

        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        groups["actions_mode"] = {"name": "Actions Mode Settings", "items": action_mode_settings}
        groups["docker_mode"] = {"name": "Docker Mode Settings", "items": docker_mode_settings}
        return groups

    def create(args):
        obj = Popup()
        Extensions.dictToObject(obj, args)
        items = Extensions.default_assignment(args, "items", [])
        obj.items = Extensions.list_assignment(items, PopupInfo)
        return obj
    
    def __str__(self):
        return self.btnName.replace("\n", "\\n")
    
    def forceLoad(self):
        self.items = TypedList(self.items, PopupInfo)
        pass
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": ["actions", "docker"]}
        restrictions["popupType"] = {"type": "values", "entries": ["popup", "window", "toolbox"]}
        restrictions["opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        return restrictions

class Docker:
    display_name: str = ""
    docker_name: str = ""
    icon: str = ""
    hotkeyNumber: int = 0

    def create(args):
        obj = Docker()
        Extensions.dictToObject(obj, args)
        return obj
    
    def forceLoad(self):
        pass
    
    def __str__(self):
        return self.display_name.replace("\n", "\\n")
    
    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["icon", "hotkeyNumber"]}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_name"] = {"type": "docker_selection"}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
    

class DockerGroupItems:
    id: str=""

    def create(args):
        obj = DockerGroupItems()
        Extensions.dictToObject(obj, args)
        return obj
    
    def __str__(self):
        return self.id.replace("\n", "\\n")
    
    def forceLoad(self):
        pass

    def propertygrid_ismodel(self):
        return True
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["id"] = {"type": "docker_selection"}
        return restrictions

class DockerGroup:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0
    tabsMode: bool = True
    groupId: str = ""
    docker_names: TypedList[DockerGroupItems] = []

    def create(args):
        obj = DockerGroup()
        Extensions.dictToObject(obj, args)
        docker_names = Extensions.default_assignment(args, "docker_names", [])
        obj.docker_names = Extensions.list_assignment(docker_names, DockerGroupItems)
        return obj
    
    def __str__(self):
        return self.display_name.replace("\n", "\\n")
    
    def forceLoad(self):
        self.docker_names = TypedList(self.docker_names, DockerGroupItems)

    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        return groups
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
    
class Workspace:
    display_name: str = ""
    id: str = ""
    icon: str = ""
    hotkeyNumber: int = 0

    def create(args):
        obj = Workspace()
        Extensions.dictToObject(obj, args)
        return obj
    
    def __str__(self):
        return self.display_name.replace("\n", "\\n")
    
    def forceLoad(self):
        pass

    def propertygrid_groups(self):
        groups = {}
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        return groups
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
    
class ConfigFile:
    dockers: TypedList[Docker] = []
    docker_groups: TypedList[DockerGroup] = []
    popups: TypedList[Popup] = []
    workspaces: TypedList[Workspace] = []

    def load_chunk(self, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            return jsonData["items"]

    def save_chunk(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.__base_dir__, 'configs', configName + ".json")
        jsonData = { "items": cfg }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)


    def propertygrid_groups(self):
        groups = {}
        groups["dockers"] = {"name": "Dockers", "items": ["dockers"]}
        groups["docker_groups"] = {"name": "Docker Groups", "items": ["docker_groups"]}
        groups["popups"] = {"name": "Popups", "items": ["popups"]}
        groups["workspaces"] = {"name": "Workspaces", "items": ["workspaces"]}
        return groups

    def save(self):
        self.save_chunk(self.dockers, "dockers")
        self.save_chunk(self.docker_groups, "docker_groups")
        self.save_chunk(self.popups, "popups")
        self.save_chunk(self.workspaces, "workspaces")
        self.load()

    def load(self):
        self.dockers = Extensions.list_assignment(self.load_chunk("dockers"), Docker)
        self.docker_groups = Extensions.list_assignment(self.load_chunk("docker_groups"), DockerGroup)
        self.popups = Extensions.list_assignment(self.load_chunk("popups"), Popup)
        self.workspaces = Extensions.list_assignment(self.load_chunk("workspaces"), Workspace)

    def __init__(self, base_dir):
        self.__base_dir__ = base_dir
        self.load()

class ConfigManager:

    def instance():
        return ConfigManager.root

    def init_instance(path):
        ConfigManager.root = ConfigManager(path)

    def __init__(self, path) -> None:
        self.hotkeys_storage = {}
        self.base_dir = path
        self.cfg = ConfigFile(self.base_dir)

    def getBaseDirectory(self):
        return self.base_dir

    def getResourceFolder(self):
        return os.path.join(self.base_dir, "resources")

    def getHotkeyAction(self, index):
        return self.hotkeys_storage[index]

    def addHotkey(self, index, action):
        self.hotkeys_storage[index] = action

    def getJSON(self) -> ConfigFile:
        return self.cfg