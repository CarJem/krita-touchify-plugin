from typing import List
import json
import os

def default_assignment(args, attributeName, defaultValue):
    if attributeName in args:
        return args[attributeName]
    else:
        return defaultValue
    
def list_assignment(array, classSrc, arraySrc):
    for i in array:
        arraySrc.append(classSrc.create(i))



class Config_PopupInfo:
    text: str
    action: str
    icon: str
    customIcon: bool

    def create(args):
        obj = Config_PopupInfo()
        obj.text = default_assignment(args, "text", "")
        obj.action = default_assignment(args, "action", "")
        obj.icon = default_assignment(args, "icon", "")
        obj.customIcon = default_assignment(args, "customIcon", False)
        return obj

class Config_Popup:
    id: str
    btnName: str
    isIconCustom: bool
    icon: str
    type: str
    docker_id: str
    grid_width: int
    grid_padding: int
    item_width: int
    item_height: int
    icon_width: int
    icon_height: int
    items: List[Config_PopupInfo]


    def __init__(self):
        pass

    def create(args):
        obj = Config_Popup()
        obj.id = default_assignment(args, "id", "")
        obj.btnName = default_assignment(args, "btnName", "")
        obj.icon = default_assignment(args, "icon", "")
        obj.type = default_assignment(args, "type", "actions")
        obj.docker_id = default_assignment(args, "docker_id", "")
        obj.isIconCustom = default_assignment(args, "isIconCustom", True)
        obj.grid_width = default_assignment(args, "grid_width", 3)
        obj.grid_padding = default_assignment(args, "grid_padding", 2)
        obj.item_width = default_assignment(args, "item_width", 100)
        obj.item_height = default_assignment(args, "item_height", 100)
        obj.icon_width = default_assignment(args, "icon_width", 30)
        obj.icon_height = default_assignment(args, "icon_height", 30)
        obj.items = []
        items = default_assignment(args, "items", [])
        list_assignment(items, Config_PopupInfo, obj.items)
        return obj

class Config_Docker:
    display_name: str
    docker_name: str

    def create(args):
        obj = Config_Docker()
        obj.display_name = default_assignment(args, "display_name", "")
        obj.docker_name = default_assignment(args, "docker_name", "")
        return obj

class Config_DockerGroup:
    display_name: str
    id: str
    docker_names: List[str]

    def create(args):
        obj = Config_DockerGroup()
        obj.display_name = default_assignment(args, "display_name", "")
        obj.id = default_assignment(args, "id", "")
        obj.docker_names = default_assignment(args, "docker_names", [])
        return obj

class Config_Workspace:
    display_name: str
    id: str

    def create(args):
        obj = Config_Workspace()
        obj.display_name = default_assignment(args, "display_name", "")
        obj.id = default_assignment(args, "id", "")
        return obj

class ConfigFile:
    auto_dockers: List[Config_Docker] = []
    custom_dockers: List[Config_DockerGroup] = []
    popups: List[Config_Popup] = []
    workspaces: List[Config_Workspace] = []



    def load_chunk(self, configName):
        CONFIG_FILE = os.path.join(self.base_dir, 'configs', configName + ".json")
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            return jsonData["items"]

    def save_chunk(self, cfg, configName):
        CONFIG_FILE = os.path.join(self.base_dir, 'configs', configName + ".json")
        jsonData = { "items": cfg }
        with open(CONFIG_FILE, "w") as f:
            json.dump(jsonData, f, default=lambda o: o.__dict__, indent=4)


    def save(self):
        self.save_chunk(self.auto_dockers, "dockers")
        self.save_chunk(self.custom_dockers, "docker_groups")
        self.save_chunk(self.popups, "popups")
        self.save_chunk(self.workspaces, "workspaces")

    def __init__(self, base_dir):
        self.base_dir = base_dir
        list_assignment(self.load_chunk("dockers"), Config_Docker, self.auto_dockers)
        list_assignment(self.load_chunk("docker_groups"), Config_DockerGroup, self.custom_dockers)
        list_assignment(self.load_chunk("popups"), Config_Popup, self.popups)
        list_assignment(self.load_chunk("workspaces"), Config_Workspace, self.workspaces)

class ConfigManager:

    def init(path):
        global base_dir
        global cfg
        base_dir = path
        cfg = ConfigFile(base_dir)

    def getBaseDirectory():
        global base_dir
        return base_dir

    def getResourceFolder():
        global base_dir
        return os.path.join(base_dir, "resources")

    def getJSON() -> ConfigFile:
        global cfg
        return cfg