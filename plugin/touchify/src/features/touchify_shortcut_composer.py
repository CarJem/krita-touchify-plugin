
from touchify.src.components.touchify.shortcut_composer.PieActionController import PieActionController
from touchify.src.components.touchify.shortcut_composer.PieMenu import PieMenu
from touchify.src.ext.KritaExtensions import *

from touchify.src.variables import *

from touchify.src.settings import *
from touchify.src.resources import *

from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.window import TouchifyWindow

try:
    from input_adapter import ActionManager
    import templates
    SHORTCUT_COMPOSER_LOADED = True
except:
    SHORTCUT_COMPOSER_LOADED = False

FEATURE_ENABLED = False
    
class TouchifyShortcutComposer(object):
    


    def __init__(self, instance: "TouchifyWindow"):
        self.appEngine = instance  
        if not SHORTCUT_COMPOSER_LOADED: return
        if not FEATURE_ENABLED: return
        
        self.action_manager: ActionManager = None


    def buildMenu(self, menu: QMenu):
        if not SHORTCUT_COMPOSER_LOADED: return
        if not FEATURE_ENABLED: return

        for name, container in self.action_manager._stored_actions.items():
            self.root_menu.addAction(container.krita_action)
            
        if len(self.root_menu.actions()) == 0:
            testUIAction = self.root_menu.addAction("No Actions")
            testUIAction.setEnabled(False)

        menu.addMenu(self.root_menu)

    def createActions(self, window: Window, actionPath: str):
        if not SHORTCUT_COMPOSER_LOADED: return
        if not FEATURE_ENABLED: return

        def createInstructions() -> list[templates.RawInstructions]:

            return [
                PieMenu(
                    name="[Touchify] Pie Menu #1",
                    controller=PieActionController(),
                    pie_radius_scale=1.5,
                    icon_radius_scale=1.5,
                    values=[
                        #"ACTION_ID::TOUCHIFY_ICON_PATH::TOUCHIFY_CUSTOM_TEXT"
                        "selection_tool_mode_add::selection_add",
                        "selection_tool_mode_replace::selection_replace",
                        "selection_tool_mode_subtract::selection_subtract",
                        "selection_tool_mode_intersect::selection_intersect",
                        "file_new::folder-documents",
                        "file_new::material:file",
                        "file_new::material:facebook",
                        "file_new::material:facebook-messenger",
                        "file_new::material:google",
                        "file_new::material:google-play",
                        "file_new::material:google-drive",
                        "file_new::material:apple",
                        "file_new::material:apple-ios",
                        "file_new::material:microsoft",
                        "file_new::material:microsoft-xbox",
                        "file_new::material:github",
                        "file_new::material:minecraft",
                        "file_new::material:sony-playstation",
                        "file_new::material:microsoft-windows",
                        "file_new::material:microsoft-visual-studio-code",
                        "file_new::material:nintendo-switch",
                        "file_new::material:nintendo-game-boy",
                        "file_new::material:nintendo-wii",
                        "file_new::material:microsoft-windows-classic",
                    ]
                )
            ]

        self.root_menu = QtWidgets.QMenu("Shortcut Composer...")
    
        self.action_manager = ActionManager(window)

        for action in createInstructions():
            self.action_manager.bind_action(action)





            
