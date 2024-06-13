from PyQt5 import QtWidgets, QtGui
import os
from .config import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ext.PyKrita import *
else:
    from krita import *

class ResourceManager:

    def getCustomIconList():
        result = []
        PATH_RESOURCES = os.path.join(ConfigManager.instance().getResourceFolder(), "custom")

        # Custom Icon Code
        try:
            custom_icon_formats =  [".svg"]
            for f in os.listdir(PATH_RESOURCES):
                iconName = os.path.splitext(f)[0]
                ext = os.path.splitext(f)[1]
                if ext.lower() not in custom_icon_formats:
                    continue
                result.insert(0, 'custom:' + iconName)
        except:
            pass
        
        return result
        

    def customIcon(iconName):
        PATH_RESOURCES = os.path.join(ConfigManager.instance().getResourceFolder(), "custom")

        filename = '{0}.svg'.format(iconName)
        
        if os.path.exists(os.path.join(PATH_RESOURCES, filename)):
            icon = QtGui.QIcon(os.path.join(PATH_RESOURCES, filename))
            return icon
        else:
            icon = ResourceManager.getFallbackIcon()
            return icon
        
    def iconLoader(iconName):
        if not str(iconName).startswith("custom:"):
            return ResourceManager.kritaIcon(iconName)
        else:
            customName = str(iconName)[len("custom:"):]
            return ResourceManager.customIcon(customName)
    
    def kritaIcon(iconName):
        return Krita.instance().icon(iconName)
    
    def getFallbackIcon():
        return QtGui.QIcon(os.path.join(ConfigManager.instance().getResourceFolder(), 'builtin', 'default.svg'))