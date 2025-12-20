
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
from touchify.src.api_krita import KritaAPI
from touchify.src.api_krita.wrappers.window import WindowAPI


class KritaExtensions:

    @staticmethod
    def moveActionTo(action_id: str, source: QMenu, dest: QMenu, after: str):
        actionToMove = KritaAPI.get_action(action_id)

        afterAct = None
        for index, action in enumerate(dest.actions()):
            #print(action.objectName())
            if action.objectName() == after:
                afterAct = dest.actions()[index+1]
                break

        if afterAct is not None:
            source.removeAction(actionToMove)
            dest.insertAction(afterAct, actionToMove)

        return actionToMove
    
    @staticmethod
    def getDockerMenu(window: WindowAPI):
        for m in window.qwindow.actions():
            if m.objectName() == "settings_dockers_menu":
                return m
        return None

    @staticmethod
    def showQuickMessage(message: str):
        view = KritaAPI.get_active_view()
        view.showFloatingMessage(message, KritaAPI.get_icon('move_layer_up'), 1000, 0)

    @staticmethod
    def formatActionText(text: str):
        seperator = " "
        segments = text.split(seperator)
        edited_segments = []

        for seg in segments:
            if seg.startswith("&") and len(seg) != 1:
                edited_segments.append(seg[1:])
            else:
                edited_segments.append(seg)
            

        return seperator.join(edited_segments)
