from typing import List
import json
import os

def default_assignment(args, attributeName, defaultValue):
    if attributeName in args:
        return args[attributeName]
    else:
        return defaultValue


class Config_PopupInfo:
    text: str
    action: str
    icon: str
    customIcon: bool

    def __init__(self, **args):
        self.text = default_assignment(args, 'text', '')
        self.action = default_assignment(args, 'action', '')
        self.icon = default_assignment(args, 'icon', '')
        self.customIcon = default_assignment(args, 'customIcon', False)

class Config_Popup:
    id: str
    btnName: str
    grid_width: int
    grid_padding: int
    item_width: int
    item_height: int
    icon_width: int
    icon_height: int
    items: List[Config_PopupInfo]

    def __init__(self, **args):
        self.id = default_assignment(args, 'id', '')
        self.btnName = default_assignment(args, 'btnName', '')
        self.grid_width = default_assignment(args, 'grid_width', 3)
        self.grid_padding = default_assignment(args, 'grid_padding', 2)
        self.item_width = default_assignment(args, 'item_width', 100)
        self.item_height = default_assignment(args, 'item_height', 100)
        self.icon_width = default_assignment(args, 'icon_width', 30)
        self.icon_height = default_assignment(args, 'icon_height', 30)
        self.items = default_assignment(args, 'items', [])

class Config_Docker:
    display_name: str
    docker_name: str

    def __init__(self, display_name='', docker_name=''):
        self.display_name = display_name
        self.docker_name = docker_name

class Config_DockerGroup:
    display_name: str
    id: str
    docker_names: List[str]

    def __init__(self, display_name='', id='', docker_names: List[str]=[]):
        self.display_name = display_name
        self.id = id
        self.docker_names = docker_names

class Config_Workspace:
    display_name: str
    id: str

    def __init__(self, display_name='', id=''):
        self.display_name = display_name
        self.id = id

class ConfigFile:
    auto_dockers: List[Config_Docker]
    custom_dockers: List[Config_DockerGroup]
    workspaces: List[Config_Workspace]
    popups: List[Config_Popup]

    def __init__(self, **args):
        self.auto_dockers = default_assignment(args, 'auto_dockers', [])
        self.custom_dockers = default_assignment(args, 'custom_dockers', [])
        self.workspaces = default_assignment(args, 'workspaces', [])
        self.popups = default_assignment(args, 'popups', [])

class ConfigManager:

    def init(path):
        global base_dir
        base_dir = path

    def getBaseDirectory():
        global base_dir
        return base_dir

    def getResourceFolder():
        global base_dir
        return os.path.join(base_dir, 'resources')




    def loadJSON() -> ConfigFile:
        global base_dir
        CONFIG_FILE = os.path.join(base_dir, 'config.json')
        with open(CONFIG_FILE) as f:
            jsonData = json.load(f)
            return ConfigFile(**jsonData)

    def saveJSON(cfg):
        global base_dir
        CONFIG_FILE = os.path.join(base_dir, 'config.json')
        with open(CONFIG_FILE, 'w') as f:
            json.dump(cfg, f, default=lambda o: o.__dict__, indent=4)

    def getJSON() -> ConfigFile:
        try:
            return ConfigManager.loadJSON()
        except:
            return ConfigFile() 