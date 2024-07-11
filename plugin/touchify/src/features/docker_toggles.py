from functools import partial
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util

from ..variables import *

from ..cfg.CfgDocker import CfgDocker
from ..settings.TouchifyConfig import *
from ..resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..touchify import TouchifyInstance
    
class DockerToggles(object):
    def __init__(self, instance: "TouchifyInstance"):
        self.appEngine = instance

    def toggleDocker(self, path):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())

    def reloadDockers(self):
        cfg = TouchifyConfig.instance().getJSON()
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
        menu.addMenu(self.root_menu)

    def createAction(self, window: Window, docker: CfgDocker, actionPath: str):
        actionName ='{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_DOCKER, docker.docker_name)
        id = docker.docker_name
        iconName = docker.icon
        text ='{0} [Docker]'.format(docker.display_name)

        action = window.createAction(actionName, text, actionPath)    
        icon = ResourceManager.iconLoader(iconName)
        action.setIcon(icon)


        if not docker.hotkeyNumber == 0:
            self.appEngine.touchify_hotkeys.getHotkeyAction(docker.hotkeyNumber).triggered.connect(lambda: self.toggleDocker(id))

        action.triggered.connect(lambda: self.toggleDocker(id))
        self.root_menu.addAction(action)

    def createActions(self, window: Window, actionPath: str):
        sectionName = TOUCHIFY_ID_ACTIONS_DOCKER
        subItemPath = actionPath + "/" + sectionName
        cfg = TouchifyConfig.instance().getJSON()
        self.root_menu = QtWidgets.QMenu("Dockers")

        for docker in cfg.dockers:
            self.createAction(window, docker, subItemPath)