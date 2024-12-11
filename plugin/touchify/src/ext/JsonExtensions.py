
import copy
import json
from touchify.src.ext.types.TypedList import TypedList
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
    

class JsonExtensions:

    def loadClass(filePath: str, type: type):
        try:
            with open(filePath) as f:
                return type(**json.load(f))
        except:
            return copy.deepcopy(type())
            
    def saveClass(data: any, filePath: str):
        with open(filePath, "w") as f:
            json.dump(data, f, default=lambda o: o.__dict__, indent=4)

    def tryCast(jsonData, type, defaultValue):
        if not jsonData:
            return defaultValue
        else:
            result = jsonData
            return result


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

    def init_list(args: dict[str, any], attributeName: str, classSrc: type):
        val = []
        if attributeName in args:
            val = args[attributeName]

        arraySrc = TypedList(None, classSrc)
        for i in val:
            arraySrc.append(classSrc(**i))
        return arraySrc
