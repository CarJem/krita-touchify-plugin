from functools import partial
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


pending_actions = []

class DockerToggles:
    def toggleDocker(self, path):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())

    def reloadDockers(self):
        cfg = ConfigManager.instance().getJSON()
        dockersList = Krita.instance().dockers()
        data = []

        for docker in dockersList:
            x = Config_Docker()
            x.display_name = docker.windowTitle()
            x.docker_name = docker.objectName()
            data.append(x)
        
        cfg.auto_dockers = data
        cfg.save()


    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Dockers", menu)
        menu.addMenu(root_menu)

        for action in pending_actions:
            root_menu.addAction(action)

    def createAction(self, window, docker: Config_Docker, actionPath):
        actionName ='DockerToggles_{0}'.format(docker.docker_name)
        id = docker.docker_name
        text ='{0}'.format(docker.display_name)

        action = window.createAction(actionName, "Docker: " + text, actionPath)    
        icon = ResourceManager.iconLoader(id, 'dockers', True)
        action.setIcon(icon)
        pending_actions.append(action)

        if not docker.hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(docker.hotkeyNumber).triggered.connect(lambda: self.toggleDocker(id))

        action.triggered.connect(lambda: self.toggleDocker(id))

    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Dockers"
        subItemPath = actionPath + "/" + sectionName
        cfg = ConfigManager.instance().getJSON()

        for docker in cfg.auto_dockers:
            self.createAction(window, docker, subItemPath)