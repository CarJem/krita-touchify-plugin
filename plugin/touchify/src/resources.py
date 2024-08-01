
from PyQt5 import QtWidgets, QtGui, QtCore
import os


from .components.QSvgIconEngine import QSvgIconEngine


from .settings.TouchifyConfig import *
from zipfile import ZipFile

from krita import *


ICON_PACKS_LOADED = False

class ResourceManager:


    material_icons: dict[str, QIcon] = {}

    def getResourceFolder():
        return os.path.join(BASE_DIR, "resources")
        
        
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

    def getCustomIconList():
        result = []
        PATH_RESOURCES = os.path.join(ResourceManager.getResourceFolder(), "custom")

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
        
        MATERIAL_ICONS = os.path.join(ResourceManager.getResourceFolder(), "builtin", 'material-icons.zip')
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
        PATH_RESOURCES = os.path.join(ResourceManager.getResourceFolder(), "custom")

        filename = '{0}.svg'.format(iconName)
        
        if os.path.exists(os.path.join(PATH_RESOURCES, filename)):
            icon = QtGui.QIcon(os.path.join(PATH_RESOURCES, filename))
            return icon
        else:
            icon = ResourceManager.getFallbackIcon()
            return icon
        
    def getBrushPresets():
        return Krita.instance().resources('preset')
        
    def brushIcon(brushName):
        brush_presets = Krita.instance().resources('preset')
        if brushName in brush_presets:
            preset = brush_presets[brushName]
            return QIcon(QPixmap.fromImage(preset.image()))
        else:
            return ResourceManager.getFallbackIcon()
        
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
        return QtGui.QIcon(os.path.join(ResourceManager.getResourceFolder(), 'builtin', 'default.svg'))
    
ResourceManager.loadIconPacks()