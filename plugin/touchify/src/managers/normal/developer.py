from touchify.src.extensions.krita_extensions import *

from touchify.__env__ import *

from touchify.src.managers.shared.settings import *
from touchify.src.managers.shared.resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow


    
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





            
