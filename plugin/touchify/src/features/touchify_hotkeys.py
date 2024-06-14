from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
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
            hotkeyName = "touchify_hotkey" + str(i)
            hotkeyAction = window.createAction(hotkeyName, "Custom action: " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)