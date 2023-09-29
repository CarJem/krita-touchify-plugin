import inspect
from .typedlist import *
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Extensions:
    def dictToObject(obj, dict):
        if dict is not None:
            for key, value in dict.items():
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