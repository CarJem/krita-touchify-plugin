from krita import *
from touchify.src.api_krita import KritaAPI
from .variables import *

class Settings:

    def getFileDialogState():
        return KritaAPI.read_setting(APPLICATION_NAME, SETTING_LAST_SELECTED_FOLDER, "")

    def setFileDialogState(folder: str):
        KritaAPI.write_setting(APPLICATION_NAME, SETTING_LAST_SELECTED_FOLDER, folder)

    def getGridPreferences():
        return {
            'GRID_MAX_CACHED_IMAGES': 256,
            'GRID_ITEM_SIZE': 100,
            'GRID_ITEM_EXPORT_SCALE': 100,
            'GRID_ITEM_EXPORT_FIT_CANVAS': False
        }
