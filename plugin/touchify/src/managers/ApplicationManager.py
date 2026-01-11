from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.src.settings.TouchifySettings import TouchifySettings


class ApplicationManager(QObject):

    def __init__(self, parent: QObject):
        super().__init__(parent)

        self.__allowScalingWorkarounds = TouchifySettings.preferences().Application_EnableScalingWorkarounds
        self.__allowMenuIcons = TouchifySettings.preferences().Application_EnableMenuIcons

        self.__useFakeHighDpiScaling = TouchifySettings.preferences().Scaling_UseFakeHighDpiScaling
        self.__useHighDpiPixmaps = TouchifySettings.preferences().Scaling_UseHighDpiPixmaps
        self.__use96DPI = TouchifySettings.preferences().Scaling_Use96Dpi
        self.__adjustFontScale = TouchifySettings.preferences().Scaling_UseAdjustedFontScale
        self.__fontScaleOffset = TouchifySettings.preferences().Scaling_AdjustedFontScale
        

    def onApplicationLoad(self):

        if self.__allowMenuIcons:
            qApp.instance().setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

        if self.__allowScalingWorkarounds and self.__useFakeHighDpiScaling:
            qApp.instance().setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if self.__allowScalingWorkarounds and self.__useHighDpiPixmaps:
            qApp.instance().setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        if self.__allowScalingWorkarounds and self.__use96DPI:
            qApp.instance().setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi, True)
        self.onFontChanged()

    def onFontChanged(self, font: QFont = None):
        
        try: qApp.fontChanged.disconnect(self.onFontChanged)
        except: pass
        
        if self.__allowScalingWorkarounds and self.__adjustFontScale:
            current_font = qApp.font()
            current_font.setPointSizeF(current_font.pointSize() + self.__fontScaleOffset)
            qApp.setFont(current_font)

        try: qApp.fontChanged.connect(self.onFontChanged)
        except: pass
    
    def onWindowLoaded(self, qWin: QMainWindow):
        pass

    @staticmethod
    def instance():
        try:
            return ApplicationManager.__instance
        except AttributeError:
            ApplicationManager.__instance = ApplicationManager(qApp)
            return ApplicationManager.__instance

