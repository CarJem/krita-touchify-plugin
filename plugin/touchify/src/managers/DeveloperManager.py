from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_vaporjem.extensions import pyqt_extensions
from jemlib.alib_vaporjem.extensions.krita_extensions import *

from jemlib.api_touchify.env import *

from touchify.src.settings.TouchifySettings import *
from jemlib.managers.IconRepository import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow


    
class DeveloperManager(object):
    
    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance  
        self.__testType = "none"

        self.__timer = QTimer()
        self.__timer.setInterval(150)
        self.__timer.timeout.connect(self.onRapidTestInterval)

        self.dlg = None


    def Actions_Post(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def Actions_Init(self, window: WindowAPI, actionPath: str):
        subItemPath = actionPath + "/" + "developer"
        self.root_menu = QtWidgets.QMenu("Developer...")

        self.iconZoo = QAction("Icon Zoo...")
        self.iconZoo.triggered.connect(lambda: self.onZooRequested(DataConstraints.StrMod.IconSelection))
        self.root_menu.addAction(self.iconZoo)

        self.actionZoo = QAction("Action Zoo...")
        self.actionZoo.triggered.connect(lambda: self.onZooRequested(DataConstraints.StrMod.ActionSelection))
        self.root_menu.addAction(self.actionZoo)

        self.brushesZoo = QAction("Brushes Zoo...")
        self.brushesZoo.triggered.connect(lambda: self.onZooRequested(DataConstraints.StrMod.BrushSelection))
        self.root_menu.addAction(self.brushesZoo)

        self.root_menu.addSeparator()

        self.danger_menu = self.root_menu.addMenu("Danger Zone")

        self.rapidSaveLoadTest1 = QAction("Toggle Rapid Save/Load Test...")
        self.rapidSaveLoadTest1.triggered.connect(lambda: self.onRapidTestRequested("io"))
        self.danger_menu.addAction(self.rapidSaveLoadTest1)

        self.rapidSaveLoadTest2 = QAction("Toggle Rapid PropertyGrid_Window Test...")
        self.rapidSaveLoadTest2.triggered.connect(lambda: self.onRapidTestRequested("pg"))
        self.danger_menu.addAction(self.rapidSaveLoadTest2)

        self.rapidSaveLoadTest3 = QAction("Toggle Rapid ToolshelfDock Editor Test...")
        self.rapidSaveLoadTest3.triggered.connect(lambda: self.onRapidTestRequested("tsdpg"))
        self.danger_menu.addAction(self.rapidSaveLoadTest3)
    
        if len(self.root_menu.actions()) == 0:
            testUIAction = self.root_menu.addAction("No Actions")
            testUIAction.setEnabled(False)

    def onRapidTestRequested(self, type: str):
        if self.__testType != type:
            if self.__timer.isActive(): self.__timer.stop()
            self.__testType = type
            match self.__testType:
                case "io":
                    self.__timer.setInterval(150)
                case "pg":
                    self.__timer.setInterval(500)
                case "tsdpg":
                    self.__timer.setInterval(500)
                case _:
                    self.__timer.setInterval(150)
        
        if self.__timer.isActive(): 
            self.__timer.stop()
        else: 
            self.__timer.start()

    def onRapidTestInterval(self):
        self.__timer.stop()

        match self.__testType:
            case "io":
                self.appEngine.ReloadSettings()
            case "pg":
                if self.appEngine.dlg and not pyqt_extensions.CommonHelpers.isDeleted(self.appEngine.dlg):
                    print("closing")
                    self.appEngine.dlg.close()
                else:
                    print("opening")
                    self.appEngine.OpenSettings()
            case _:
                pass

        
        self.__timer.start()

    def onZooRequested(self, type: DataConstraints.StrMod):

        def copyItemToClipboard(result: str):
            clipboard = QApplication.clipboard()
            clipboard.setText(result)

        self.dlg = PropertyGrid_SelectorDialog.Setup(self.dlg, None, "zoo", {
            'button_names': [ "Copy to Clipboard...", "Exit..." ],
            'close_on_save': False
        })
        self.dlg.onAcceptFunction = copyItemToClipboard
        self.dlg.load_list(type)
        self.dlg.exec()





            
