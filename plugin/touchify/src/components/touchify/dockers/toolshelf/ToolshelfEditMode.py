from typing import TYPE_CHECKING
from krita import *
from touchify.src.variables import TOUCHIFY_WIDGETPROPS_EDITING_ALLOWED, TOUCHIFY_WIDGETPROPS_EDITING_SELECTED

if TYPE_CHECKING:
    from touchify.src.components.touchify.dockers.toolshelf.ToolshelfWidget import ToolshelfWidget

class ToolshelfEditMode(QObject):
    def __init__(self, toolshelf: "ToolshelfWidget"):
        super().__init__(toolshelf)
        self.toolshelf = toolshelf
        self.window = toolshelf.window()
        
        self.is_active = False
        self.selector_filter = ToolshelfEditMode.SelectorFilter(self, self.window)

        self.current_selection: QWidget = None
        self.parent_selection: QWidget = None

    def setEnabled(self, value: bool):
        self.is_active = value

        if self.is_active:
            qApp.installEventFilter(self.selector_filter)
        else:
            qApp.removeEventFilter(self.selector_filter)
            self.clearSelection()

    def findAncestor(self, ancestor, obj):
        if not hasattr(obj, 'parent'): return False

        parent = obj.parent()
        while True:
            if not parent:
                return False
            elif ancestor is parent:
                return True
            obj = parent
            parent = obj.parent()
            
    def findSelection(self, obj):
        if isinstance(obj, QWidget):
            widget: QWidget = obj
            allowedEditMode = widget.property(TOUCHIFY_WIDGETPROPS_EDITING_ALLOWED)
            if allowedEditMode != None and allowedEditMode == True:
                return obj
            else:
                if widget.parentWidget():
                    return self.findSelection(widget.parentWidget())

        return None


    def clearSelection(self):
        if self.current_selection:
            self.current_selection.setProperty(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED, False)
            self.current_selection.update()
            self.current_selection = None

    def setSelection(self, obj: QWidget):
        if obj and obj is not self.current_selection and obj is not self.parent_selection and self.findAncestor(self.toolshelf,obj):
            sel = self.findSelection(obj)
            if not sel: return

            if self.current_selection:
                self.current_selection.setProperty(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED, False)
                self.current_selection.update()

            sel.setProperty(TOUCHIFY_WIDGETPROPS_EDITING_SELECTED, True)
            sel.update()
            
            self.current_selection = sel
            self.parent_selection = obj
            

    class SelectorFilter(QObject):
        def __init__(self, connector: "ToolshelfEditMode", window: "QWidget"):
            super().__init__(window)
            self.connector = connector
            self.window = window

        def eventFilter(self, obj, event):
            etype = event.type()

            if etype == QEvent.Type.HoverMove or etype == QEvent.Type.MouseMove:
                pos = QCursor.pos()
                onWidget = QApplication.widgetAt(pos)
                self.connector.setSelection(onWidget)

            return False
                
                
