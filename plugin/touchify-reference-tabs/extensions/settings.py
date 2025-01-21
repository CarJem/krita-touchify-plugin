from krita import *
from .variables import *

class Settings:

    def getFileDialogState():
        return Krita.instance().readSetting(APPLICATION_NAME, SETTING_LAST_SELECTED_FOLDER, "")

    def setFileDialogState(folder: str):
        Krita.instance().writeSetting(APPLICATION_NAME, SETTING_LAST_SELECTED_FOLDER, folder)

    def getGridPreferences():
        return {
            'GRID_MAX_CACHED_IMAGES': 256,
            'GRID_ITEM_SIZE': 100,
            'GRID_ITEM_EXPORT_SCALE': 100,
            'GRID_ITEM_EXPORT_FIT_CANVAS': False
        }
