
from PyQt5 import QtGui, QtSvg
import os

from jemlib.__env__ import JEMLIB_ASSETS_DIRECTORY, TOUCHIFY_RESOURCE_PACKS_DIRECTORY

import xml.etree.ElementTree as ET

from jemlib.alib_vaporjem import Logger
from jemlib.api_krita import KritaAPI
from jemlib.alib_vaporjem.extensions.pyqt_extensions import QPainterTools
from zipfile import ZipFile
from krita import *


ICON_PACKS_LOADED = False
RESOURCE_PACK_ICONS_INIT = False

class IconRepository:

    class PaddedIcon(QIconEngine):
        def __init__(self, icon: QIcon, padding: int):
            super().__init__()
            self.icon = icon
            self.padding = padding
            self.margins = QMargins(self.padding, self.padding, self.padding, self.padding)

        def pixmap(self, size, mode, state):
            if size:
                return self.icon.pixmap(size.shrunkBy(self.margins), mode, state)
            else:
                return self.icon.pixmap(size, mode, state)
        
        def paint(self, painter, rect, mode, state):
            self.icon.paint(painter, rect.marginsRemoved(self.margins), mode=mode, state=state)

    class IconEngine(QIconEngine):
        def __init__(self, svgData: bytes, autoColorMode: bool = True):
            super().__init__()
            self.svgData = ET.fromstring(svgData)
            self.autoColorMode = autoColorMode

            if self.autoColorMode:
                for child in self.svgData:
                    if child.get("style"):
                        child.set("ignore-krita-style", "true")
                    else:
                        child.set("ignore-krita-style", "false")

            self.currentColor = None
            self.renderer = QtSvg.QSvgRenderer()

        def iconColor(self, mode: QIcon.Mode, state: QIcon.State):
            background = qApp.palette().window().color()
            is_dark = background.value() > 100
            if is_dark: base_color = QColor(55,55,55) # dark icons
            else: base_color = QColor(202, 202, 202) # light icons

            if mode == QIcon.Mode.Disabled:
                base_color.setAlpha(128)
                return QPainterTools.blendColors(base_color, background)
            else:
                return base_color
    
        def updateData(self, mode: QIcon.Mode, state: QIcon.State):
            if self.autoColorMode:
                color = self.iconColor(mode, state).name().split("#")[1]
                for child in self.svgData:
                    if child.get("ignore-krita-style") == "false":
                        child.set("style", f"fill:#{color};fill-opacity:1")
            self.renderer.load(ET.tostring(self.svgData))


        def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State):
            img = QPixmap(size)
            img.fill(Qt.GlobalColor.transparent)
            painter = QPainter(img)
            self.updateData(mode, state)
            self.renderer.render(painter, QRectF(img.rect()))
            painter.end()
            return img

        def paint(self, painter: QPainter, rect: QRect, mode: QIcon.Mode, state: QIcon.State):
            self.updateData(mode, state)
            self.renderer.render(painter, QRectF(rect))

    material_icons: dict[str, QIcon] = {}
    resource_pack_icons: dict[str, dict[str, QIcon]] = {}

    def __is_vaild_custom_icon__(fileName: str):
        return fileName.lower().endswith(".svg")
    
    def __get_icon_name_from_file__(fileName: str):
        if fileName.lower().endswith(".svg"):
            return fileName[:-4]
        return fileName

    def __resourcesDir__():
        return JEMLIB_ASSETS_DIRECTORY
    
    def __resourcePacksDir__():
        return TOUCHIFY_RESOURCE_PACKS_DIRECTORY

    def loadResourcePackIcons(isStartup: bool = False):
        global RESOURCE_PACK_ICONS_INIT
        if RESOURCE_PACK_ICONS_INIT and isStartup == True:
            return
        
        Logger.logDebug("JemLib","IconRepository", "unknown", "load_resourcepack_icons")
        
        IconRepository.resource_pack_icons.clear()

        resource_pack_dir = IconRepository.__resourcePacksDir__()
        directories = [f for f in os.listdir(resource_pack_dir) if os.path.isdir(os.path.join(resource_pack_dir, f))]
        for resource_pack in directories:
            pack_icons_path = os.path.join(resource_pack_dir, resource_pack, "icons")
            if os.path.exists(pack_icons_path) and os.path.isdir(pack_icons_path):

                if resource_pack not in IconRepository.resource_pack_icons:
                    IconRepository.resource_pack_icons[resource_pack] = {}

                files = [f for f in os.listdir(pack_icons_path) if os.path.isfile(os.path.join(pack_icons_path, f))]
                for icon_filename in files:
                    icon_filepath = os.path.join(pack_icons_path, icon_filename)

                    if IconRepository.__is_vaild_custom_icon__(icon_filename):
                        icon_name = IconRepository.__get_icon_name_from_file__(icon_filename)
                        icon_data = QtGui.QIcon(icon_filepath)
                        #print(icon_name)
                        IconRepository.resource_pack_icons[resource_pack][icon_name] = icon_data





        RESOURCE_PACK_ICONS_INIT = True
        Logger.logDebug("JemLib","IconRepository", "unknown", "load_resourcepack_icons_done")

    def loadIconPacks():
        global ICON_PACKS_LOADED
        if ICON_PACKS_LOADED:
            return
        
        Logger.logDebug("JemLib","IconRepository", "unknown", "load_icon_packs")
        
        material_icon_zip = os.path.join(IconRepository.__resourcesDir__(), 'material-icons.zip')
        with ZipFile(material_icon_zip, 'r') as zip:
            for item in zip.filelist:
                if item.filename.startswith('MaterialDesign-master/svg/') and item.filename.endswith('.svg'):
                    actualName = item.filename.removeprefix('MaterialDesign-master/svg/').removesuffix('.svg')
                    iconBytes = zip.read(item)
                    IconRepository.material_icons[actualName] = QIcon(IconRepository.IconEngine(iconBytes))
        ICON_PACKS_LOADED = True
        Logger.logDebug("JemLib","IconRepository", "unknown", "load_icon_packs_done")

    #region Icon Retrival

    def resourcePackIcon(iconName: str):
        try:
            routes = iconName.split(":", 1)
            pack_name = routes[0]
            icon_name = routes[1]

            if pack_name in IconRepository.resource_pack_icons:
                icon_directory = IconRepository.resource_pack_icons[pack_name]
                if icon_name in icon_directory:
                    return icon_directory[icon_name]
        except:
            pass    
        
        return IconRepository.fallbackIcon()

    def materialIcon(iconName: str):
        if iconName in IconRepository.material_icons:
            return IconRepository.material_icons[iconName]
        else:
            return IconRepository.fallbackIcon()

    def actionIcon(action_id: str):
        target_action = KritaAPI.get_action(action_id)
        if target_action: return target_action.icon()
        else: return QIcon()
        
    def brushIcon(brushName: str, presets_cache: dict[str, any] = None):
        brush_presets = KritaAPI.get_presets() if not presets_cache else presets_cache
        if brushName in brush_presets:
            preset = brush_presets[brushName]
            return QIcon(QPixmap.fromImage(preset.image()))
        else:
            return IconRepository.fallbackIcon()
   
    def kritaIcon(iconName: str):
        return KritaAPI.get_icon(iconName)
    
    def fallbackIcon():
        return QtGui.QIcon(os.path.join(IconRepository.__resourcesDir__(), 'default.svg'))

    #endregion


    def iconList(directory_type: str):
        def custom_registry():
            result = []

            for packName in IconRepository.resource_pack_icons:
                for iconName in IconRepository.resource_pack_icons[packName]:
                    result.insert(0, f'resource_pack:{packName}:{iconName}')

            for iconName in IconRepository.material_icons:
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
            return IconRepository.materialIcon(materialName)
        elif str(iconName).startswith("resource_pack:"):
            resource_pack_name = str(iconName)[len("resource_pack:"):]
            return IconRepository.resourcePackIcon(resource_pack_name)
        else:
            return IconRepository.kritaIcon(iconName)

    

    
IconRepository.loadIconPacks()
IconRepository.loadResourcePackIcons()