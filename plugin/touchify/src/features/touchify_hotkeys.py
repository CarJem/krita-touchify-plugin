from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *

from ..docker_manager import DockerManager

from ..variables import *
from ..config import *
from .. import stylesheet
from PyQt5.QtWidgets import QMessageBox



from krita import *
    
class TouchifyHotkeys:


    def showPopupPalette(self):
        qwin = Krita.instance().activeWindow().qwindow()
        viewIndex = Krita.instance().activeWindow().views().index(Krita.instance().activeWindow().activeView())
        pobj = qwin.findChild(QWidget,'view_' + str(viewIndex))
        mobj = next((w for w in pobj.findChildren(QWidget) if w.metaObject().className() == 'KisPopupPalette'), None)
        if not mobj.isVisible():
            parentWidget = mobj.parentWidget()
            center_x = int(parentWidget.width() / 2) - int(mobj.width() / 2)
            center_y = int(parentWidget.height() / 2) - int(mobj.height() / 2)
            mobj.show()
            mobj.move(center_x, center_y)
        else:
            mobj.hide()

    def createActions(self, window: Window, subItemPath):
        # Global Hotkey Assignments
        for i in range(1, 10):
            hotkeyName = '{0}_{1}'.format(TOUCHIFY_ID_ACTION_PREFIX_HOTKEY, str(i))
            hotkeyAction = window.createAction(hotkeyName, "Touchify: Action " + str(i), subItemPath)
            ConfigManager.instance().addHotkey(i, hotkeyAction)

        # Show Popup Palette
        hotkeyAction = window.createAction(TOUCHIFY_ID_ACTION_SHOW_POPUP_PALETTE, "Show Popup Palette", subItemPath)
        hotkeyAction.triggered.connect(self.showPopupPalette)

        

        
