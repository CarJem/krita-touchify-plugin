from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..docker_manager import DockerManager

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class TouchifyHotkeys:

    def createActions(self, window, subItemPath):
        for i in range(1, 10):
            hotkeyName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_HOTKEY, str(i))
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)
