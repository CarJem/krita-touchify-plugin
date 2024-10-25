
from touchify.src.ext.types.TypedList import TypedList
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
    

class JsonExtensions:

    def tryCast(jsonData, type, defaultValue):
        if not jsonData:
            return defaultValue
        else:
            result = jsonData
            return result

    def tryGetListAssignment(jsonData, key, type, defaultValue):
        if not jsonData:
            return JsonExtensions.list_assignment(defaultValue, type)
        if key in jsonData:
            result = jsonData[key]
            return JsonExtensions.list_assignment(result, type)
        else:
            return JsonExtensions.list_assignment(defaultValue, type)

    def tryGetEntry(jsonData, key, type, defaultValue):
        if not jsonData:
            return defaultValue
        if key in jsonData:
            result = jsonData[key]
            return result
        else:
            return defaultValue
    
    def dictToObject(obj, args: dict[str, any], extraTypes: list[type] = []):
        if args is not None:
            for key, value in args.items():
                if hasattr(obj, key):
                    if type(getattr(obj, key)) == type(value):
                        setattr(obj, key, value)
                    else:
                        for cls in extraTypes:
                            if isinstance(getattr(obj, key), cls):
                                setattr(obj, key, cls(**value))
                            
    def default_assignment(args, attributeName, defaultValue):
        if attributeName in args:
            return args[attributeName]
        else:
            return defaultValue
        
    def list_assignment(array, classSrc):
        arraySrc = TypedList(None, classSrc)
        for i in array:
            arraySrc.append(classSrc(**i))
        return arraySrc