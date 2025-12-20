from typing import Any

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions



class SubViewSettings:

    class Tab:
        def __init__(self, **args) -> None:
            self.filepath = ""
            self.viewer_state: dict[str, Any] = {}

            JsonExtensions.dictToObject(self, args)

            self.__image: QImage = None

        def getImageData(self):
            if self.__image != None:
                return self.__image
            
            image: QImage | None = None
            try:
                reader = QImageReader(self.filepath)
                # Automatically use rotation metadata (typically found in photographs)
                reader.setAutoTransform(True)
                image = reader.read()
                if image.isNull():
                    image = None
            except:
                image = None

            self.__image = image
            
            return image

    def __init__(self, **args) -> None:
        self.lastBrowsedFolder = ""
        self.lastImageIndex = 0
        self.lastPopupWidth = 0
        self.lastPopupHeight = 0
        self.tabs: list[SubViewSettings.Tab] = []
        JsonExtensions.dictToObject(self, args)
        self.tabs = JsonExtensions.init_list(args, "tabs", SubViewSettings.Tab)

    def forceLoad(self):
        self.tabs = TypedList(self.tabs, SubViewSettings.Tab)



