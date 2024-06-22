
from PyQt5 import QtWidgets, QtGui, QtCore
import os


from touchify.src.components.QSvgIconEngine import QSvgIconEngine


from .config import *
from zipfile import ZipFile

from krita import *


ICON_PACKS_LOADED = False

class ResourceManager:


    material_icons: dict[str, QIcon] = {}

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

        for iconName in ResourceManager.material_icons:
            result.insert(0, 'material:' + iconName)
        
        return result
        
    def loadIconPacks():
        global ICON_PACKS_LOADED
        if ICON_PACKS_LOADED:
            return
        
        MATERIAL_ICONS = os.path.join(ConfigManager.instance().getResourceFolder(), "builtin", 'material-icons.zip')
        with ZipFile(MATERIAL_ICONS, 'r') as zip:
            for item in zip.filelist:
                if item.filename.startswith('MaterialDesign-master/svg/') and item.filename.endswith('.svg'):
                    actualName = item.filename.removeprefix('MaterialDesign-master/svg/').removesuffix('.svg')
                    iconBytes = zip.read(item)
                    ResourceManager.material_icons[actualName] = QIcon(QSvgIconEngine(iconBytes))
        ICON_PACKS_LOADED = True

    def materialIcon(iconName):
        if iconName in ResourceManager.material_icons:
            return ResourceManager.material_icons[iconName]
        else:
            return ResourceManager.getFallbackIcon()

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
        if str(iconName).startswith("material:"):
            materialName = str(iconName)[len("material:"):]
            return ResourceManager.materialIcon(materialName)
        elif str(iconName).startswith("custom:"):
            customName = str(iconName)[len("custom:"):]
            return ResourceManager.customIcon(customName)
        else:
            return ResourceManager.kritaIcon(iconName)
            
    def kritaIcon(iconName):
        return Krita.instance().icon(iconName)
    
    def getFallbackIcon():
        return QtGui.QIcon(os.path.join(ConfigManager.instance().getResourceFolder(), 'builtin', 'default.svg'))
    
ResourceManager.loadIconPacks()