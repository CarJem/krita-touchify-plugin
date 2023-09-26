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

    def addDocker(self, window, actionName, id, text, actionPath):
        action = window.createAction(actionName, "Docker: " + text, actionPath)    
        icon = ResourceManager.iconLoader(id, 'dockers', True)
        action.setIcon(icon)
        pending_actions.append(action)
        action.triggered.connect(lambda: self.toggleDocker(id))

    def reloadDockers(self):
        cfg = ConfigManager.getJSON()
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


    def createActions(self, window, actionPath):
        sectionName = "VaporJem_Dockers"
        subItemPath = actionPath + "/" + sectionName
        cfg = ConfigManager.getJSON()

        for docker in cfg.auto_dockers:
            self.addDocker(window, 'DockerToggles_{0}'.format(docker.docker_name), docker.docker_name, '{0}'.format(docker.display_name), subItemPath)