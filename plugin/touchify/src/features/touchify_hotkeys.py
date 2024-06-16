from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..variables import TOUCHIFY_ID_ACTIONS_HOTKEY
from ..config import *
from ..components.nu_tools.NtToolbox import NtToolbox
from ..components.nu_tools.NtToolOptions import NtToolOptions
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox

# For autocomplete
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..ext.PyKrita import *
else:
    from krita import *
    
class TouchifyHotkeys:

    def createActions(self, window, subItemPath):
        for i in range(1, 10):
            hotkeyName = '{0}_{1}'.format(TOUCHIFY_ID_ACTIONS_HOTKEY, str(i))
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)