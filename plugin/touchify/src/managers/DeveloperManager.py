from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
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
    
        if len(self.root_menu.actions()) == 0:
            testUIAction = self.root_menu.addAction("No Actions")
            testUIAction.setEnabled(False)

    def onZooRequested(self, type: DataConstraints.StrMod):

        def copyItemToClipboard():
            clipboard = QApplication.clipboard()
            clipboard.setText(dlg.selected_item)

        dlg = PropertyGrid_SelectorDialog(None)
        dlg.header_buttons.buttons()[0].setText("Copy to Clipboard...")
        dlg.header_buttons.buttons()[1].setText("Exit...")
        dlg.header_buttons.accepted.connect(copyItemToClipboard)
        dlg.header_buttons.rejected.connect(lambda: dlg.reject())
        dlg.load_list(type)
        dlg.exec_()





            
