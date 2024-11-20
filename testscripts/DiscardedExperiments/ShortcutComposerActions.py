
from PyQt5.QtCore import QObject, QEvent

from krita import *
from PyQt5.QtWidgets import *

from touchify.src.settings import TouchifyConfig

try:
    from input_adapter import ActionManager
    SHORTCUT_COMPOSER_LOADED = True
except:
    SHORTCUT_COMPOSER_LOADED = False


class NtCanvasAction(QObject):
    mouseReleased = pyqtSignal()

    def __init__(self, window: QMainWindow):
        self.main_window = window
        super().__init__()

    def isFocused(self):
        cursor_pos = QCursor.pos()
        widget_under_cursor = QApplication.widgetAt(cursor_pos)
    
        if not isinstance(widget_under_cursor, QOpenGLWidget): return False
        if not widget_under_cursor.metaObject().className() == "KisOpenGLCanvas2": return False

        return True
    
    #def findShortcutComposer(self):
    #    sc = None
    #    for ext in Krita.instance().extensions():
    #        if str(ext.metaObject().className()) == "ShortcutComposer":
    #            sc = ext
    #            break
    #    return sc
    
    #def runAction(self, actionName: str, isRelease: bool = False):
        #actionRan = False
        #if SHORTCUT_COMPOSER_LOADED:
        #    sc = self.findShortcutComposer()
        #    if sc:
        #        for protector in sc._protectors:
        #            actionManager: ActionManager = protector.action_manager
        #            desiredAction = actionName
        #            if desiredAction in actionManager._stored_actions:
        #                action = actionManager._stored_actions[desiredAction]
        #                if isRelease: 
        #                    action.core_action.on_every_key_release()
        #                    action.core_action.on_short_key_release()
        #                    action.core_action.on_long_key_release()
        #                else: 
        #                    action.core_action.on_key_press()
        #                actionRan = True

    def runAction(self, actionName: str):
        if self.isFocused():             
            action = Krita.instance().action(actionName)
            if action: action.trigger()

    def isCanvasEvent(self, event: QEvent, btn: Qt.MouseButton):
        return (event.type() == QEvent.Type.MouseButtonPress and event.button() == btn) or (event.type() == QEvent.Type.TabletPress and event.button() == btn)

    def eventFilter(self, obj, event):
        if self.isCanvasEvent(event, Qt.MouseButton.LeftButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_LeftClickAction)
        elif self.isCanvasEvent(event, Qt.MouseButton.RightButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_RightClickAction)
        elif self.isCanvasEvent(event, Qt.MouseButton.MiddleButton):
            self.runAction(TouchifyConfig.instance().preferences().Canvas_MiddleClickAction)
        return super().eventFilter(obj, event)