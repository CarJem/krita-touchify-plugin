from PyQt5 import *
from PyQt5.QtWidgets import *
from krita import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .extension import TouchifyExtension

class TouchifyHelpers:

    def getExtension() -> "TouchifyExtension":
        extensions = Krita.instance().extensions()
        for ext in extensions:
            if hasattr(ext, "DEV_HOOK_FIND_PLUGIN"):
                if getattr(ext, "DEV_HOOK_FIND_PLUGIN") == "TOUCHIFY":
                    return ext
        return None
    
    def moveActionTo(action_id: str, source: QMenu, dest: QMenu, after: str):
        actionToMove = Krita.instance().action(action_id)

        afterAct = None
        for index, action in enumerate(dest.actions()):
            print(action.objectName())
            if action.objectName() == after:
                afterAct = dest.actions()[index+1]
                break

        if afterAct is not None:
            source.removeAction(actionToMove)
            dest.insertAction(afterAct, actionToMove)

        return actionToMove