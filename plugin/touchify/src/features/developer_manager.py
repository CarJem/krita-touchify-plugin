from touchify.src.components.krita.extensions import *

from touchify.src.variables import *

from touchify.src.settings import *
from touchify.src.features.resource_manager import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow


    
class DeveloperManager(object):
    
    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance  


    def Actions_Post(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def Actions_Init(self, window: Window, actionPath: str):
        subItemPath = actionPath + "/" + "developer"
        self.root_menu = QtWidgets.QMenu("Developer...")
    
        if len(self.root_menu.actions()) == 0:
            testUIAction = self.root_menu.addAction("No Actions")
            testUIAction.setEnabled(False)





            
