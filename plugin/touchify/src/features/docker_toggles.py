from functools import partial
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

from ..variables import *

from ..cfg.CfgDocker import CfgDocker
from ..config import *
from ..resources import *

from krita import *

class DockerToggles:

    pending_actions = []
    
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
            x = CfgDocker()
            x.display_name = docker.windowTitle()
            x.docker_name = docker.objectName()
            data.append(x)
        
        cfg.dockers = data
        cfg.save()

    def buildMenu(self, menu: QMenu):
        root_menu = QtWidgets.QMenu("Dockers", menu)
        menu.addMenu(root_menu)

        for action in self.pending_actions:
            root_menu.addAction(action)

    def createAction(self, window, docker: CfgDocker, actionPath):
        actionName ='{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_DOCKER, docker.docker_name)
        id = docker.docker_name
        iconName = docker.icon
        text ='{0} [Docker]'.format(docker.display_name)

        action = window.createAction(actionName, text, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)
        self.pending_actions.append(action)

        if not docker.hotkeyNumber == 0:
            ConfigManager.instance().getHotkeyAction(docker.hotkeyNumber).triggered.connect(lambda: self.toggleDocker(id))

        action.triggered.connect(lambda: self.toggleDocker(id))

    def createActions(self, window, actionPath):
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER
        subItemPath = actionPath + "/" + sectionName
        cfg = ConfigManager.instance().getJSON()

        for docker in cfg.dockers:
            self.createAction(window, docker, subItemPath)