from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .GridViewItem import GridViewItem
import copy
import math
import os.path
from ...classes.variables import *
from ...classes.settings import Settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .GridSection import GridSection



class GridView(QWidget):

    pageChanged = pyqtSignal(int,int)

    def __init__(self, parent: "GridSection" = None):
        super().__init__(parent)
        self.GridSection = parent

        self.directoryPath = ""


        self.allImages: list[str] = []
        self.imagesButtons: list[GridViewItem] = []
        self.foundImages: list[str] = []
        self.favouriteImages: list[str] = []
        self.Cache_Images: dict[str, QImage] = {}
        self.Cache_Paths: list[str] = []

        self.bg_alpha = str("background-color: rgba(0, 0, 0, 50); ")
        self.bg_hover = str("background-color: rgba(0, 0, 0, 100); ")

        self.cache_limit = 0
        self.item_size = 0
        self.item_export_scale = 0
        self.item_export_fit_canvas = False

        self.zoom_scale = 1
        self.current_page = 0
        
        self.column_count = 1
        self.row_count = 1


        self.grid_view_layout = QGridLayout(self)
        self.setLayout(self.grid_view_layout)

    def readOptions(self):
        options = Settings.getGridPreferences()
        self.cache_limit: int = options["GRID_MAX_CACHED_IMAGES"]
        self.item_size: int = options["GRID_ITEM_SIZE"]        
        self.item_export_scale: int = options["GRID_ITEM_EXPORT_SCALE"]
        self.item_export_fit_canvas: int = options["GRID_ITEM_EXPORT_FIT_CANVAS"]

    def initalize(self):
        self.readOptions()
        self.resizeView()
        self.reorganizeImages()
        self.refreshImages()

    def resizeView(self):


        def fitToFavor(favored: int, flexible: int, restriction: int):
                if favored >= restriction:
                    return restriction, 1, restriction
                else:
                    final_restriction = (restriction * flexible)
                    while final_restriction > restriction:
                        flexible -= 1
                        final_restriction = (restriction * flexible)
                    return restriction, flexible, final_restriction

        def updateButtonCount(iip: int):
            if iip == len(self.imagesButtons):
                pass
            elif iip > len(self.imagesButtons):
                iip_last = len(self.imagesButtons)
                for i in range(iip_last, iip): 
                    imageButton = GridViewItem(self)
                    imageButton.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred,QSizePolicy.Policy.Preferred))
                    imageButton.setGridIndex(i)
                    imageButton.SIGNAL_HOVER.connect(self.Item_OnHover)
                    imageButton.SIGNAL_LMB.connect(self.Item_OnClick)
                    imageButton.SIGNAL_LMB_DOUBLE.connect(self.Item_OnDoubleClick)
                    imageButton.SIGNAL_WUP.connect(lambda: self.navigateFromIncrement(-1))
                    imageButton.SIGNAL_WDN.connect(lambda: self.navigateFromIncrement(1))
                    imageButton.SIGNAL_PREVIEW.connect(self.GridSection.openPreview)
                    imageButton.SIGNAL_FAVOURITE.connect(self.Action_PinToFavourites)
                    imageButton.SIGNAL_UN_FAVOURITE.connect(self.Action_UnpinFromFavourites)
                    imageButton.SIGNAL_OPEN_NEW.connect(self.GridSection.NativeFn.openNewDocument)
                    imageButton.SIGNAL_REFERENCE.connect(self.GridSection.NativeFn.placeReference)
                    self.grid_view_layout.addWidget(imageButton)
                    self.imagesButtons.append(imageButton)
            else:
                while len(self.imagesButtons) != iip: 
                    imageButton: GridViewItem = self.imagesButtons[-1]
                    imageButton.SIGNAL_HOVER.disconnect()
                    imageButton.SIGNAL_LMB.disconnect()
                    imageButton.SIGNAL_LMB_DOUBLE.disconnect()
                    imageButton.SIGNAL_WUP.disconnect()
                    imageButton.SIGNAL_WDN.disconnect()
                    imageButton.SIGNAL_PREVIEW.disconnect()
                    imageButton.SIGNAL_FAVOURITE.disconnect()
                    imageButton.SIGNAL_UN_FAVOURITE.disconnect()
                    imageButton.SIGNAL_OPEN_NEW.disconnect()
                    imageButton.SIGNAL_REFERENCE.disconnect()
                    self.grid_view_layout.removeWidget(imageButton)
                    self.imagesButtons.pop()

        item_size = round(self.item_size * self.zoom_scale)
        max_columns = round(self.width() / item_size)
        max_rows = round(self.height() / item_size)
        max_items = max_columns * max_rows

        if max_items >= self.cache_limit: # Don't allow more than the cache limit premits
            if max_rows > max_columns: # Distribute in Favor of Rows
                max_rows, max_columns, max_items = fitToFavor(max_rows, max_columns, self.cache_limit)
            elif max_rows < max_columns: # Distribute in Favor of Columns
                max_columns, max_rows, max_items = fitToFavor(max_columns, max_rows, self.cache_limit)
            else: #Equal Number of Columns and Rows, Distribute Equally
                count = round(math.sqrt(self.cache_limit))
                max_columns = count; max_rows = count; max_items = self.cache_limit

        if self.column_count == max_columns or self.row_count == max_rows:
            self.max_items = max_items
            return


        updateButtonCount(max_items)
        self.max_items = max_items
        
        current_col = 0
        current_row = 0

        for i in range(0, max_items):
            self.grid_view_layout.addWidget(self.imagesButtons[i], current_row, current_col)
            current_col += 1
            if current_col == max_columns:
                current_col = 0
                current_row += 1

        self.reorganizeImages()
        self.refreshImages()

    #region Widget Methods

    def navigateFromIncrement(self, increment: int):
        if (self.current_page == 0 and increment == -1) or \
            ((self.current_page + 1) * len(self.imagesButtons) > len(self.foundImages) and increment == 1) or \
            len(self.foundImages) == 0:
            return

        self.current_page += increment
        maxNumPage = math.ceil(len(self.foundImages) / self.max_items)
        self.current_page = max(0, min(self.current_page, maxNumPage - 1))
        self.refreshImages()

    def navigateToIndex(self, pageNum: int):
        maxNumPage = math.ceil(len(self.foundImages) / self.max_items)
        self.current_page = max(0, min(pageNum, maxNumPage - 1))
        self.refreshImages()

    def setFilter(self, filter: str):
        stringsInText = filter.lower().split(" ")
        if filter.lower() == "":
            self.foundImages = copy.deepcopy(self.allImages)
            self.reorganizeImages()
            self.refreshImages()
            return 

        newImages = []
        for word in stringsInText:
            for path in self.allImages:
                # exclude path outside from search
                if word in path.replace(self.directoryPath, "").lower() and not path in newImages and word != "" and word != " ":
                    newImages.append(path)

        self.foundImages = newImages
        self.reorganizeImages()
        self.refreshImages()
    
    def setDirectoryPath(self, path: str):
        self.directoryPath = path
        self.favouriteImages = []
        self.foundImages = []
        self.updateImages()
    
    def setZoom(self, zoom_scale: int):
        self.zoom_scale = float(zoom_scale / 100)        
        self.resizeView()

    #endregion        

    #region Image Methods

    def refreshImages(self):

        def checkPath(path):
            if not os.path.isfile(path):
                if path in self.foundImages:
                    self.foundImages.remove(path)
                if path in self.allImages:
                    self.allImages.remove(path)
                if path in self.favouriteImages:
                    self.favouriteImages.remove(path)

                dlg = QMessageBox(self)
                dlg.setWindowTitle("Missing Image!")
                dlg.setText("This image you tried to open was not found. Removing from the list.")
                dlg.exec()

                return False

            return True

        def checkValidImages():
            found = 0
            max_items = self.max_items
            for path in self.foundImages:
                if found == max_items:
                    return

                if checkPath(path):
                    found = found + 1


        checkValidImages()
        buttonsSize = len(self.imagesButtons)

        # don't try to access image that isn't there
        maxRange = min(len(self.foundImages) - self.current_page * buttonsSize, buttonsSize)

        for i in range(0, len(self.imagesButtons)):
            if i < maxRange:
                # image is within valid range, apply it
                path = self.foundImages[i + buttonsSize * self.current_page]
                self.imagesButtons[i].setFavourite(path in self.favouriteImages)
                self.imagesButtons[i].setImage(path)
                self.imagesButtons[i].setExportOptions(self.item_export_fit_canvas, self.item_export_scale)
            else:
                # image is outside the range
                self.imagesButtons[i].setFavourite(False)
                self.imagesButtons[i].setImage("")
                self.imagesButtons[i].setExportOptions(self.item_export_fit_canvas, self.item_export_scale)

        # update text for pagination
        if len(self.foundImages) == 0 or self.max_items == 0:
            maxNumPage = 0
        else:
            maxNumPage = math.ceil(len(self.foundImages) / self.max_items)
        self.pageChanged.emit(maxNumPage, self.current_page)

    def updateImages(self):
        newImages = []
        self.current_page = 0

        if self.directoryPath == "":
            self.foundImages = []
            self.favouriteImages = []
            self.refreshImages()
            return 

        it = QDirIterator(self.directoryPath, QDirIterator.Subdirectories)


        while(it.hasNext()):
            if (".webp" in it.filePath() or ".png" in it.filePath() or ".jpg" in it.filePath() or ".jpeg" in it.filePath()) and \
                (not ".webp~" in it.filePath() and not ".png~" in it.filePath() and not ".jpg~" in it.filePath() and not ".jpeg~" in it.filePath()):
                newImages.append(it.filePath())

            it.next()

        self.foundImages = copy.deepcopy(newImages)
        self.allImages = copy.deepcopy(newImages)
        self.reorganizeImages()
        self.refreshImages()

    def reorganizeImages(self):
        # organize images, taking into account favourites
        # and their respective order
        favouriteFoundImages = []
        for image in self.favouriteImages:
            if image in self.foundImages:
                self.foundImages.remove(image)
                favouriteFoundImages.append(image)

        self.foundImages = favouriteFoundImages + self.foundImages

    #endregion

    #region Item Event Methods

    def Item_OnHover(self, SIGNAL_HOVER):
        # normal images
        for i in range(0, len(self.imagesButtons)):
            self.imagesButtons[i].setStyleSheet(self.bg_alpha)

            if SIGNAL_HOVER == str(i):
                self.imagesButtons[i].setStyleSheet(self.bg_hover)

    def Item_OnClick(self, position):
        pass

    def Item_OnDoubleClick(self, position):
        if position < len(self.foundImages) - len(self.imagesButtons) * self.current_page:
            self.GridSection.openPreview(self.foundImages[position + len(self.imagesButtons) * self.current_page])

    #endregion

    #region Action Methods
    
    def Action_UnpinFromFavourites(self, path):
        if path in self.favouriteImages:
            self.favouriteImages.remove(path)
        # resets order to the default, but checks if foundImages is only a subset
        # in case it is searching
        orderedImages = []
        for image in self.allImages:
            if image in self.foundImages:
                orderedImages.append(image)

        self.foundImages = orderedImages
        self.reorganizeImages()
        self.refreshImages()

    def Action_PinToFavourites(self, path):
        self.current_page = 0
        self.favouriteImages = [path] + self.favouriteImages
        self.reorganizeImages()
        self.refreshImages()

    #endregion

    #region Event Methods

    def resizeEvent(self, a0):
        self.resizeView()
        return super().resizeEvent(a0)

    #endregion
