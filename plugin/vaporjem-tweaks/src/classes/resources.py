from PyQt5 import QtWidgets, QtGui
import os
from .config import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *

class ResourceManager:
    def customIcon(path, iconName):
        PATH_RESOURCES = os.path.join(ConfigManager.getResourceFolder(), path)

        filename = '{0}.svg'.format(iconName)
        
        if os.path.exists(os.path.join(PATH_RESOURCES, filename)):
            icon = QtGui.QIcon(os.path.join(PATH_RESOURCES, filename))
            return icon
        else:
            icon = ResourceManager.getFallbackIcon()
            return icon
        
    def iconLoader(iconName, type, isCustom):
        if not isCustom:
            return ResourceManager.kritaIcon(iconName)
        else:
            return ResourceManager.customIcon(type, iconName)
    
    def kritaIcon(iconName):
        return Krita.instance().icon(iconName)
    
    def getFallbackIcon():
        return QtGui.QIcon(os.path.join(ConfigManager.getResourceFolder(), 'builtin', 'default.svg'))