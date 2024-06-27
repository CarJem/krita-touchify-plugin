import inspect
from .typedlist import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys


from krita import *

class Extensions:

    def nameof(exp):
        frame = sys._getframe(1)
        i = frame.f_lasti
        code = frame.f_code
        index = code.co_code[i - 1] * 256 + code.co_code[i - 2]
        op = code.co_code[i - 3]
        if op == 124: # local var
            return code.co_varnames[index]
        elif op == 116: # global var
            return code.co_names[index]
        else: #argument is not an identifier, fallback on source code extraction
            fname = frame.f_code.co_filename
            line = frame.f_lineno
            try:
                with open(fname) as f:
                    line = f.read().split('\n')[line - 1]
            except IOError:
                pass
            else:
                start = line.find('nameof(') + 7
                end = line.find(')', start)
                return line[start:end]
    
    def extend(class_to_extend):
        def decorator(extending_class):
            class_to_extend.__dict__.update(extending_class.__dict__)
            return class_to_extend
        return decorator

    def dictToObject(obj, dict):
        if dict is not None:
            for key, value in dict.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

    def getClassVariables(obj):
        return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__") and not attr.startswith("_"  + type(obj).__name__ + "__")]
    
    def getVariable(obj, varName):
        return getattr(obj, varName)
    
    def setVariable(obj, varName, data):
        return setattr(obj, varName, data)
    
    def default_assignment(args, attributeName, defaultValue):
        if attributeName in args:
            return args[attributeName]
        else:
            return defaultValue
        
    def list_assignment(array, classSrc):
        arraySrc = TypedList(None, classSrc)
        for i in array:
            arraySrc.append(classSrc.create(i))
        return arraySrc
    
class KritaExtensions:

    def showQuickMessage(message):
        Krita.instance().activeWindow().activeView().showFloatingMessage(message, Krita.instance().icon('move_layer_up'), 1000, 0)

    def getMainWindow():
        return Krita.instance().activeWindow().qwindow()

    def getDocker(name):
        dockers = Krita.instance().dockers()
        for docker in dockers:
            if docker.objectName() == name:
                return docker
        return None

    def loadIcon(iconName):
        return Krita.instance().icon(iconName)

    def getIconList():
        result = []

        iconFormats = ["*.svg","*.svgz","*.svz","*.png"]

        iconList = QDir(":/pics/").entryList(iconFormats, QDir.Files)
        iconList += QDir(":/").entryList(iconFormats, QDir.Files)

        for iconName in iconList:
            name = iconName.split('_',1)
            if any(iconSize == name[0] for iconSize in [ '16', '22', '24', '32', '48', '64', '128', '256', '512', '1048' ]):
                iconName = name[1]

            name = iconName.split('_',1)
            if any(iconSize == name[0] for iconSize in [ 'light', 'dark' ]):
                iconName = name[1]

            name = iconName.split('.')
            iconName = name[0]
            if iconName not in result: 
                result.insert(0, iconName)

        iconList = QDir(":/icons/").entryList(iconFormats, QDir.Files)
        #iconList += QDir(":/images/").entryList(iconFormats, QDir.Files)

        for iconName in iconList:
            name = iconName.split('.')
            iconName = name[0]
            if iconName not in result: 
                result.insert(0, iconName)

        #with open( os.path.dirname(os.path.realpath(__file__)) + '/ThemeIcons.txt' ) as f:
        #    for iconName in f.readlines():
        #        result.insert(0, iconName.rstrip())
             
        return sorted(result)

    def getDockerData():
        result = []
        dockers = Krita.instance().dockers()
        for docker in dockers:
            result.insert(0, {
                "id": docker.objectName(),
                "name": docker.windowTitle(),
                "icon": docker.windowIcon()
            })
        return result

class PyQtExtensions:

    def quickDialog(parent, text):
        dlg = QMessageBox(parent)
        dlg.setText(text)
        dlg.show()

    def clearLayout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    PyQtExtensions.clearLayout(child.layout())

class JsonExtensions:

    def tryCast(jsonData, type, defaultValue):
        if not jsonData:
            return defaultValue
        else:
            result: type = jsonData
            return result


    def tryGetListAssignment(jsonData, key, type, defaultValue):
        if not jsonData:
            return Extensions.list_assignment(defaultValue, type)
        if key in jsonData:
            result: type = jsonData[key]
            return Extensions.list_assignment(result, type)
        else:
            return Extensions.list_assignment(defaultValue, type)

    def tryGetEntry(jsonData, key, type, defaultValue):
        if not jsonData:
            return defaultValue
        if key in jsonData:
            result: type = jsonData[key]
            return result
        else:
            return defaultValue