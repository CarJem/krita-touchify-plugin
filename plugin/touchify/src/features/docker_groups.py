from PyQt5 import QtWidgets, QtGui
from ..variables import *
from ..cfg.CfgDockerGroup import CfgDockerGroup
from ..settings.TouchifyConfig import *
from ..resources import *
from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance

class DockerGroups(object):

    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance
        self.custom_docker_states = {}

    def toggleDockers(self, id):
        dockersList = Krita.instance().dockers()
        dockerGroup = self.custom_docker_states[id]

        isVisible = not dockerGroup["enabled"]
        dockerGroup["enabled"] = isVisible

        if dockerGroup["tabsMode"]:
            for index, key in enumerate(self.custom_docker_states):
                entry = self.custom_docker_states[key]
                if key is not id and dockerGroup["groupId"] == entry["groupId"] and entry["tabsMode"]:
                    sub_visibility = False
                    entry["enabled"] = sub_visibility
                    for path in entry["paths"]:
                        for docker in dockersList:
                            if (docker.objectName() == path):
                                docker.setVisible(sub_visibility)

        for path in self.custom_docker_states[id]["paths"]:
            for docker in dockersList:
                if (docker.objectName() == path):
                    docker.setVisible(isVisible)

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def setState(self, cfg: CfgDockerGroup):
        paths = []
        for dockerName in cfg.docker_names:
            paths.append(str(dockerName))

        self.custom_docker_states[cfg.id] = {
            "enabled": False,
            "paths": paths,
            "groupId": cfg.groupId,
            "tabsMode": cfg.tabsMode
        }
    
    def createAction(self, window: Window, cfg: CfgDockerGroup, actionPath: str):
        actionName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_DOCKER_GROUP, cfg.id)

        setId = cfg.id
        iconName = cfg.icon

        text = '{0} [Docker Group]'.format(cfg.display_name)

        action = window.createAction(actionName, text, actionPath) 
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)
        action.triggered.connect(lambda: self.toggleDockers(setId))

        self.setState(cfg)

        if not cfg.hotkeyNumber == 0:
            self.appEngine.touchify_hotkeys.getHotkeyAction(cfg.hotkeyNumber).triggered.connect(lambda: self.toggleDockers(setId))

        self.root_menu.addAction(action)

    def createActions(self, window: Window, actionPath):
        self.root_menu = QtWidgets.QMenu("Docker Groups")
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER_GROUP
        subItemPath = actionPath + "/" + sectionName

        cfg = TouchifyConfig.instance().getJSON()
        for docker in cfg.docker_groups:
            self.createAction(window, docker, subItemPath)

    def onConfigUpdated(self):
        cfg: TouchifyConfig.ConfigFile = TouchifyConfig.instance().getJSON()
        for item in cfg.docker_groups:
            newDockerGroupData: CfgDockerGroup = item
            if newDockerGroupData.id in self.custom_docker_states:
                self.setState(newDockerGroupData)