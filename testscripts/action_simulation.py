from krita import *
from shortcut_composer.shortcut_composer import ShortcutComposer
from shortcut_composer.input_adapter import ActionManager

sc: ShortcutComposer = None
for ext in Krita.instance().extensions():
    if str(ext.metaObject().className()) == "ShortcutComposer":
        sc: ShortcutComposer = ext
        break;


for protector in sc._protectors:
    actionManager: ActionManager = protector.action_manager
    desiredAction = 'Pick misc tools'
    if desiredAction in actionManager._stored_actions:
        action = actionManager._stored_actions[desiredAction]
        action.core_action.on_key_press()
        print(action)
                
#Krita.instance().action().trigger()