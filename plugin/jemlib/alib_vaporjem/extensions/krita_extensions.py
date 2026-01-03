
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.wrappers.window import WindowAPI


class KritaExtensions:


    @staticmethod
    def getActionData(action: QAction):
        #shortcut = KritaAPI.get_action_shortcut(actionData.objectName())
        #print(actionData.property("menulocation"))
        if isinstance(action, QWidgetAction):
            print(f"""Action Name: {action.objectName()}
                  Action Data: {str(action.dynamicPropertyNames())}""")

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
    def getActionText(action_id: str):
        action = KritaAPI.get_action(action_id)
        if not action: return action_id
        
        action_text = KritaExtensions.formatActionText(action.text())
        action_tooltip = KritaExtensions.formatActionText(action.toolTip())

        if action_text != "":
            return action_text
        elif action_tooltip != "":
            return action_tooltip
        else:
            return action_id

    @staticmethod
    def formatActionText(text: str):
        seperator = " "
        segments = text.split(seperator)
        edited_segments = []

        for seg in segments:
            if seg.startswith("&") and len(seg) != 1:
                edited_segments.append(seg[1:])
            elif "&" in seg and len(seg) != 1:
                new_seg = seg.replace("&", "")
                edited_segments.append(new_seg)
            else:
                edited_segments.append(seg)
            

        return seperator.join(edited_segments)
