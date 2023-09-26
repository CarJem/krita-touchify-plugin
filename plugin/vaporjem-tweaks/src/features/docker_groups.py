from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *

custom_docker_states = {}
pending_actions = []

class DockerGroups:

    def toggleDockers(self, id):
        global custom_docker_states
        dockersList = Krita.instance().dockers()
        isVisible = not custom_docker_states[id]["enabled"]
        custom_docker_states[id]["enabled"] = isVisible

        for index, key in enumerate(custom_docker_states):
            if key is not id:
                sub_visibility = False
                custom_docker_states[key]["enabled"] = sub_visibility
                for path in custom_docker_states[key]["paths"]:
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
    
    def createAction(self, window, docker: Config_DockerGroup, actionPath):
        global custom_docker_states

        actionName = 'DockerToggles_Custom_{0}'.format(docker.id)
        groupId = docker.id
        paths = docker.docker_names
        text = '{0}'.format(docker.display_name)

        action = window.createAction(actionName, text, actionPath) 
        icon = ResourceManager.iconLoader(groupId, 'buttons', True)
        action.setIcon(icon)

        custom_docker_states[groupId] = {
            "enabled": False,
            "paths": paths,
        }

        if not docker.hotkeyNumber == -1:
            ConfigManager.getHotkeyAction(docker.hotkeyNumber).triggered.connect(lambda: self.toggleDockers(groupId))

        pending_actions.append(action)
        action.triggered.connect(lambda: self.toggleDockers(groupId))

    def createActions(self, window, actionPath):

        sectionName = "VaporJem_DockerGroups"
        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.getJSON()
        for docker in cfg.custom_dockers:
            self.createAction(window, docker, subItemPath)
