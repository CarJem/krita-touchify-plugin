from touchify.src.components.krita.extensions import *

from touchify.src.variables import *

from touchify.src.settings import *
from touchify.src.resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow
    
class TouchifyRegisteredActions(object):
    
    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance  

    def Actions_Post(self, menu: QMenu):
        menu.addMenu(self.root_menu)

    def Actions_Init(self, window: Window, actionPath: str):
        self.root_menu = self.appEngine.mgr_actions.createRegisteredActions(window, actionPath)
            
