from dataclasses import dataclass
import os
from typing import Any
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.__env__ import Env
from jemlib.api_krita import KritaAPI
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify.src.settings.KritaSettings import KritaSettings

from touchify.src.components.sub_view.SubViewSettings import SubViewSettings

class SubViewLoader(QObject):

    @dataclass
    class ImageClip:
        state: bool
        cl: int
        ct: int
        cw: int
        ch: int

    sigOnTabsChanged = pyqtSignal()

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._fileFilter = SubViewLoader.generateFiletypeFilter()
        self._settings_cache: SubViewSettings = SubViewSettings()
        self.load()

    #region Saving / Loading

    def load(self):
        self._settings_cache = JsonExtensions.loadClass(KritaSettings.readSetting(Env.SettingsPath.SUB_VIEW, "json", ""), SubViewSettings)

    def save(self, no_override: bool = False):
        jsonData = JsonExtensions.saveClass(self._settings_cache)
        KritaSettings.writeSetting(Env.SettingsPath.SUB_VIEW, "json", jsonData, False)

    #endregion

    #region Tab Functions

    def addToTabList(self, items: list[SubViewSettings.Tab]):
        for item in items:
            self._settings_cache.tabs.append(item)
        self.save()
        self.sigOnTabsChanged.emit()

    def removeFromTabList(self, items: list[SubViewSettings.Tab]):
        current_files: list[str] = [x.filepath for x in items]
        current_tabs: list[SubViewSettings.Tab] = [x for x in self._settings_cache.tabs]
        removed_tabs: list[SubViewSettings.Tab] = [x for x in current_tabs if x.filepath in current_files]

        for item in removed_tabs:
            self._settings_cache.tabs.remove(item)
        self.save()
        self.sigOnTabsChanged.emit()

    def saveTabState(self, input: dict[str, Any]):
        self._settings_cache.tabs[self._settings_cache.lastImageIndex].viewer_state = input

    def clearTabList(self):
        self._settings_cache.tabs.clear()
        self._settings_cache.tabs = []
        self.save()
        self.sigOnTabsChanged.emit()
    
    def getTabList(self):
        return self._settings_cache.tabs

    def getTab(self, filepath: str):
        item = SubViewSettings.Tab()
        item.filepath = filepath
        return item
    
    #endregion

    #region Get / Set Functions

    def getLastIndex(self):
        return self._settings_cache.lastImageIndex
    
    def setLastIndex(self, index: int):
        self._settings_cache.lastImageIndex = index
        self.save()

    def getImageListSize(self):
        return QSize(self._settings_cache.lastPopupWidth, self._settings_cache.lastPopupHeight)

    def setImageListSize(self, size: QSize):
        self._settings_cache.lastPopupWidth = size.width()
        self._settings_cache.lastPopupHeight = size.height()
        self.save()

    def getCurrentFolder(self):
        return self._settings_cache.lastBrowsedFolder
    
    def setCurrentFolder(self, filePath: str):
        self._settings_cache.lastBrowsedFolder = filePath
        self.save()
    
    #endregion

    #region Other

    def importImages(self):
        filePaths, _filter = QFileDialog.getOpenFileNames(self.parent(), "Open an image", filter=self._fileFilter, directory=self.getCurrentFolder())
        self.setCurrentFolder(QFileDialog().directoryUrl().toLocalFile())

        if not filePaths or len(filePaths) == 0:
            return
            
        imports = []
        known_files = [x.filepath for x in self._settings_cache.tabs]

        for path in filePaths:
            if path in known_files: continue
            reader = QImageReader(path)
            reader.setAutoTransform(True) # Automatically use rotation metadata (typically found in photographs)
            image = reader.read()
            if not image.isNull(): imports.append(self.getTab(path))
        
        if len(imports) > 0:
            self.addToTabList(imports)
           
    # Generate the formats filter for the file dialog.
    @staticmethod
    def generateFiletypeFilter():
        # Ask QImage what files it can load.
        # With Krita, this will return more formats than standard Qt.
        imgFormats = QImageReader.supportedImageFormats()

        formatList = []
        filterList = []
        db = QMimeDatabase()

        for formatBytes in imgFormats:
            # convert QByteArray to string and prepend "*."
            formatList.append(f"*.{str(formatBytes, 'utf-8')}")

        for format in formatList:
            formatDesc = db.mimeTypeForFile(format).comment()
            # Some formats (camera raw) don't have proper entries, so hide those.
            # They're still listed in "All supported formats".
            if formatDesc != "unknown":
                # "Krita document (*.kra)", etc
                filterList.append(f"{formatDesc} ({format})")

        formatAllString = " ".join(formatList)
        # Alphabetical by description,
        # then "All supported formats (*.bmp *.kra *.png ...)" first.
        filterList.sort()
        filterList.insert(0, f"All supported formats ({formatAllString})")

        return ";;".join(filterList)
    
    #endregion

    #region Krita API

    @staticmethod
    def clipImage( image_path: str, clip: ImageClip, insert_size: bool = False, insert_scale: int = 1 ):
        qimage = QImage( image_path )
        if qimage.isNull() == False:
            if clip.state == True:
                w = qimage.width()
                h = qimage.height()
                qimage = qimage.copy( int( w * clip.cl ), int( h * clip.ct ), int( w * clip.cw ), int( h * clip.ch ) )
            if ( insert_size == False ):
                ad = KritaAPI.get_active_document()
                iw = ad.width
                ih = ad.height
            else:
                size = max( qimage.size().width(), qimage.size().height() )
                iw = size
                ih = size
            qimage = qimage.scaled( iw * insert_scale, ih * insert_scale, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation )
        return qimage

    @staticmethod
    def createDocumentForImage(image_path: str):
        document = KritaAPI.open_document( image_path )
        KritaAPI.get_active_window().add_view( document )

    @staticmethod
    def insertImage(image_path: str):
        # Variables
        basename = os.path.basename( image_path )
        # Create Layer
        ad = KritaAPI.get_active_document()
        rn = ad.internal.rootNode()
        pl = ad.internal.createNode( basename, "paintLayer" )
        rn.addChildNode( pl, None )
        # Qimage Data
        qimage = SubViewLoader.clipImage( image_path, SubViewLoader.ImageClip(False,0,0,0,0), True )
        ptr = qimage.constBits()
        ptr.setsize( qimage.byteCount() )
        pl.setPixelData( bytes( ptr.asarray() ), 0, 0, qimage.width(), qimage.height() )
        ad.refresh_projection()