from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

from ..variables import *

from ..cfg.CfgDockerGroup import CfgDockerGroup
from ..config import *
from ..resources import *

from krita import *

custom_docker_states = {}
pending_actions = []

class DockerGroups:

    def toggleDockers(self, id):
        global custom_docker_states
        dockersList = Krita.instance().dockers()
        dockerGroup = custom_docker_states[id]

        isVisible = not dockerGroup["enabled"]
        dockerGroup["enabled"] = isVisible

        if dockerGroup["tabsMode"]:
            for index, key in enumerate(custom_docker_states):
                entry = custom_docker_states[key]
                if key is not id and dockerGroup["groupId"] == entry["groupId"] and entry["tabsMode"]:
                    sub_visibility = False
                    entry["enabled"] = sub_visibility
                    for path in entry["paths"]:
                        for docker in dockersList:
                            if (docker.objectName() == path):
                                docker.setVisible(sub_visibility)

        for path in custom_docker_states[id]["paths"]:
            for docker in dockersList:
                if (docker.objectName() == path):
                    docker.setVisible(isVisible)

    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Docker Groups", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)

    def setState(self, cfg: CfgDockerGroup):
        paths = []
        for dockerName in cfg.docker_names:
            paths.append(str(dockerName))

        custom_docker_states[cfg.id] = {
            "enabled": False,
            "paths": paths,
            "groupId": cfg.groupId,
            "tabsMode": cfg.tabsMode
        }
    
    def createAction(self, window, cfg: CfgDockerGroup, actionPath):
        global custom_docker_states

        actionName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_DOCKER_GROUP, cfg.id)



        setId = cfg.id
        iconName = cfg.icon

        text = '{0}'.format(cfg.display_name)

        action = window.createAction(actionName, text, actionPath) 
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)

        self.setState(cfg)

        if not cfg.hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(cfg.hotkeyNumber).triggered.connect(lambda: self.toggleDockers(setId))

        pending_actions.append(action)
        action.triggered.connect(lambda: self.toggleDockers(setId))

    def createActions(self, window, actionPath):

        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER_GROUP
        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.instance().getJSON()
        for docker in cfg.docker_groups:
            self.createAction(window, docker, subItemPath)

    def onConfigUpdated(self):
        cfg: ConfigFile = ConfigManager.instance().getJSON()
        for item in cfg.docker_groups:
            newDockerGroupData: CfgDockerGroup = item
            if newDockerGroupData.id in custom_docker_states:
                self.setState(newDockerGroupData)