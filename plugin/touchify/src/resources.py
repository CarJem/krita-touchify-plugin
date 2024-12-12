
from PyQt5 import QtGui
import os


from touchify.paths import BASE_DIR
from touchify.src.components.pyqt.icon_engines.QSvgIconEngine import QSvgIconEngine


from touchify.src.settings import *
from zipfile import ZipFile

from krita import *


ICON_PACKS_LOADED = False
RESOURCE_PACK_ICONS_INIT = False

class ResourceManager:


    material_icons: dict[str, QIcon] = {}
    resource_pack_icons: dict[str, dict[str, QIcon]] = {}

    def __is_vaild_custom_icon__(fileName: str):
        return fileName.lower().endswith(".svg")
    
    def __get_icon_name_from_file__(fileName: str):
        if fileName.lower().endswith(".svg"):
            return fileName[:-4]
        return fileName

    def __resourcesDir__():
        return os.path.join(BASE_DIR, "resources")
    
    def __resourcePacksDir__():
        return os.path.join(BASE_DIR, "configs", "resources")

    def loadResourcePackIcons(isStartup: bool = False):
        global RESOURCE_PACK_ICONS_INIT
        if RESOURCE_PACK_ICONS_INIT and isStartup == True:
            return
        
        ResourceManager.resource_pack_icons.clear()

        resource_pack_dir = ResourceManager.__resourcePacksDir__()
        directories = [f for f in os.listdir(resource_pack_dir) if os.path.isdir(os.path.join(resource_pack_dir, f))]
        for resource_pack in directories:
            pack_icons_path = os.path.join(resource_pack_dir, resource_pack, "icons")
            if os.path.exists(pack_icons_path) and os.path.isdir(pack_icons_path):

                if resource_pack not in ResourceManager.resource_pack_icons:
                    ResourceManager.resource_pack_icons[resource_pack] = {}

                files = [f for f in os.listdir(pack_icons_path) if os.path.isfile(os.path.join(pack_icons_path, f))]
                for icon_filename in files:
                    icon_filepath = os.path.join(pack_icons_path, icon_filename)

                    if ResourceManager.__is_vaild_custom_icon__(icon_filename):
                        icon_name = ResourceManager.__get_icon_name_from_file__(icon_filename)
                        icon_data = QtGui.QIcon(icon_filepath)
                        print(icon_name)
                        ResourceManager.resource_pack_icons[resource_pack][icon_name] = icon_data





        RESOURCE_PACK_ICONS_INIT = True

    def loadIconPacks():
        global ICON_PACKS_LOADED
        if ICON_PACKS_LOADED:
            return
        
        material_icon_zip = os.path.join(ResourceManager.__resourcesDir__(), "builtin", 'material-icons.zip')
        with ZipFile(material_icon_zip, 'r') as zip:
            for item in zip.filelist:
                if item.filename.startswith('MaterialDesign-master/svg/') and item.filename.endswith('.svg'):
                    actualName = item.filename.removeprefix('MaterialDesign-master/svg/').removesuffix('.svg')
                    iconBytes = zip.read(item)
                    ResourceManager.material_icons[actualName] = QIcon(QSvgIconEngine(iconBytes))
        ICON_PACKS_LOADED = True

    #region Icon Retrival

    def resourcePackIcon(iconName: str):
        try:
            routes = iconName.split(":", 1)
            pack_name = routes[0]
            icon_name = routes[1]

            if pack_name in ResourceManager.resource_pack_icons:
                icon_directory = ResourceManager.resource_pack_icons[pack_name]
                if icon_name in icon_directory:
                    return icon_directory[icon_name]
        except:
            pass    
        
        return ResourceManager.fallbackIcon()

    def materialIcon(iconName: str):
        if iconName in ResourceManager.material_icons:
            return ResourceManager.material_icons[iconName]
        else:
            return ResourceManager.fallbackIcon()

    def actionIcon(action_id: str):
        target_action = Krita.instance().action(action_id)
        if target_action: return target_action.icon()
        else: return QIcon()
        
    def brushIcon(brushName: str):
        brush_presets = Krita.instance().resources('preset')
        if brushName in brush_presets:
            preset = brush_presets[brushName]
            return QIcon(QPixmap.fromImage(preset.image()))
        else:
            return ResourceManager.fallbackIcon()
   
    def kritaIcon(iconName: str):
        return Krita.instance().icon(iconName)
    
    def fallbackIcon():
        return QtGui.QIcon(os.path.join(ResourceManager.__resourcesDir__(), 'builtin', 'default.svg'))

    #endregion

    #region Other Retrival

    def brushPresets():
        return Krita.instance().resources('preset')
    
    def actionText(action_id: str):
        target_action = Krita.instance().action(action_id)
        if target_action: return target_action.text()
        else: return ""

    #endregion


    def iconList(directory_type: str):
        def custom_registry():
            result = []

            for packName in ResourceManager.resource_pack_icons:
                for iconName in ResourceManager.resource_pack_icons[packName]:
                    result.insert(0, f'resource_pack:{packName}:{iconName}')

            for iconName in ResourceManager.material_icons:
                result.insert(0, f'material:{iconName}')
            
            return result

        def krita_registry():
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

        match directory_type:
            case "custom":
                return custom_registry()
            case "krita" | _:
                return krita_registry()

    def iconLoader(iconName: str):
        if str(iconName).startswith("material:"):
            materialName = str(iconName)[len("material:"):]
            return ResourceManager.materialIcon(materialName)
        elif str(iconName).startswith("resource_pack:"):
            resource_pack_name = str(iconName)[len("resource_pack:"):]
            return ResourceManager.resourcePackIcon(resource_pack_name)
        else:
            return ResourceManager.kritaIcon(iconName)

    

    
ResourceManager.loadIconPacks()
ResourceManager.loadResourcePackIcons()