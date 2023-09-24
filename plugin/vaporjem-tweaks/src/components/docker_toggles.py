from krita import Krita, Extension
from PyQt5 import QtWidgets, QtGui
import os
import json
import sys
import importlib.util
from ..classes.config import *
from ..classes.resources import *

class DockerToggles:
    def toggleDocker(self, path):
        dockersList = Krita.instance().dockers()
        for docker in dockersList:
            if (docker.objectName() == path):
                docker.setVisible(not docker.isVisible())

    def addDocker(self, window, menu, actionName, id, text, actionPath):
        action = window.createAction(actionName, "Docker: " + text, actionPath)    
        icon = ResourceManager.iconLoader(id, 'dockers', True)
        action.setIcon(icon)

        menu.addAction(action)
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
            
    def createActions(self, window, actionPath):

        sectionName = "VaporJem_Dockers"
        root = window.createAction(sectionName, "Dockers", actionPath)
        root_menu = QtWidgets.QMenu(sectionName, window.qwindow())
        root.setMenu(root_menu)

        subItemPath = actionPath + "/" + sectionName

        cfg = ConfigManager.getJSON()

        for docker in cfg.auto_dockers:
            self.addDocker(window, root_menu, 'DockerToggles_{0}'.format(docker.docker_name), docker.docker_name, '{0}'.format(docker.display_name), subItemPath)