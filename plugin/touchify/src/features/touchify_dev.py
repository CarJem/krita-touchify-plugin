from touchify.src.ext.KritaExtensions import *

from touchify.src.variables import *

from touchify.src.settings import *
from touchify.src.resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow
    
class TouchifyDev(object):
    
    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance  

    def buildMenu(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def createActions(self, window: Window, actionPath: str):
        subItemPath = actionPath + "/" + "developer"
        self.root_menu = QtWidgets.QMenu("Developer...")


        testUIAction = self.root_menu.addAction("No Actions")
        testUIAction.setEnabled(False)





            
