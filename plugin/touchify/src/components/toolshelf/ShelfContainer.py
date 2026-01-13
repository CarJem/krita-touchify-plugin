
from typing import TYPE_CHECKING

from jemlib.alib_pyqtgraph.dockarea.Container import HContainer, TContainer, VContainer

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *





if TYPE_CHECKING:
    from touchify.src.components.toolshelf.ShelfDock import ShelfDockLabel, ShelfDock


class ShelfContainer(object):
    def __init__(self):
        self.isEditMode: bool = False
        self.parentAreaId: str = ""
        self.__isFolded = False

    def saveState(self):
        return {}
        
    def restoreState(self, state):
        pass

    def setParentAreaId(self, val: str):
        self.parentAreaId = val

    def setEditMode(self, state: bool):
        self.isEditMode = state
    
    def enterEvent(self, a0: QEvent):
        pass

    def leaveEvent(self, a0: QEvent):
        pass

    def setItemFold(self, item: "ShelfDock", state: bool):
        if self.__isFolded != state:
            self.__isFolded = True

    def getParentContainer(self):
        obj = ShelfContainer.asContainer(self)
        container = obj.parentWidget()
        if isinstance(container, ShelfHContainer) or isinstance(container, ShelfVContainer) or isinstance(container, ShelfTContainer):
            return ShelfContainer.asContainer(container)
        else:
            return None

    @staticmethod
    def isContainer(obj: object):
        return isinstance(obj, ShelfVContainer) or isinstance(obj, ShelfHContainer) or isinstance(obj, ShelfTContainer)

    @staticmethod
    def asContainer(obj: object):
        res: ShelfHContainer | ShelfVContainer | ShelfTContainer = obj
        return res
    
class ShelfSplitterContainer:

    class Handle(QSplitterHandle):
        def __init__(self, o, parent):
            super().__init__(o, parent)
            self.__parent: ShelfVContainer | ShelfHContainer = parent
            self.__enabled = True
            self.__index = 0
            self.__is_edit_mode = False

        def getIdx(self):
            return self.__index
        
        def setVisibilityState(self, index: int, is_visible: bool):
            self.__enabled = is_visible
            self.__index = index

            self.updateLayout()
            self.update()

        def updateLayout(self):
            if self.__enabled or self.__is_edit_mode: 
                self.setMaximumSize(QSize(QWIDGETSIZE_MAX,4) if isinstance(self.__parent, ShelfVContainer) else QSize(4,QWIDGETSIZE_MAX))
                if self.__index > 0:
                    self.__parent.setCollapsible(self.__index, True)
            else: 
                self.setMaximumSize(QSize(1,1))
                if self.__index > 0:
                    self.__parent.setCollapsible(self.__index, False)
        

        def paintEvent(self, a0):
            if not self.__is_edit_mode:
                return super().paintEvent(a0)
            
            if self.__enabled:
                return super().paintEvent(a0)
            
            p = QPainter(self)
            rgn = self.rect()

            p.setBrush(QBrush(QColor(100, 100, 255, 50)))
            p.setPen(QPen(QColor(50, 50, 150), 3))
            p.drawRect(rgn)
            p.end()    
            
        def setEditMode(self, state: bool):
            self.__is_edit_mode = state
            self.updateLayout()
            self.update()

        def mousePressEvent(self, event):
            if event.button() == Qt.RightButton:
                if self.__is_edit_mode:
                    ShelfSplitterContainer.showHandleContextMenu(self.__parent, self)
            super().mousePressEvent(event)

    @staticmethod
    def setItemFold(self: "ShelfVContainer | ShelfHContainer", item: "ShelfDock", state: bool):
        if state: item.show()
        else: item.hide()

        if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        else: self.show()

    @staticmethod
    def saveState(self: "ShelfVContainer | ShelfHContainer"):
        result = {}
        result["handles_hidden"] = self.handles_hidden
        return result
        
    def restoreState(self: "ShelfVContainer | ShelfHContainer", state: dict[str, any]):
        self.handles_hidden.clear()
        if "handles_hidden" in state:
            for i in state["handles_hidden"]:
                self.handles_hidden.append(i)

    @staticmethod
    def updateHandles(self: "ShelfVContainer | ShelfHContainer"):
        for idx in range(0, self.count()): 
            handle: ShelfSplitterContainer.Handle = self.handle(idx)
            if isinstance(handle, ShelfSplitterContainer.Handle):
                is_visible = (idx not in self.handles_hidden)
                handle.setVisibilityState(idx, is_visible)

    @staticmethod
    def createHandle(self: "ShelfVContainer | ShelfHContainer"):
        result = ShelfSplitterContainer.Handle(self.orientation(), self) 
        result.setEditMode(self.isEditMode)
        return result
    
    @staticmethod
    def onHandleVisibilityToggled(self: "ShelfVContainer | ShelfHContainer", idx: int):
        if idx in self.handles_hidden: self.handles_hidden.remove(idx)
        else: self.handles_hidden.append(idx)
        self.sigLayoutSaveRequest.emit()
        ShelfSplitterContainer.updateHandles(self)

    @staticmethod
    def setEditMode(self: "ShelfVContainer | ShelfHContainer", state: bool):
        for idx in range(0, self.count()): 
            handle: ShelfSplitterContainer.Handle = self.handle(idx)
            if isinstance(handle, ShelfSplitterContainer.Handle):
                handle.setEditMode(state)

    @staticmethod
    def showHandleContextMenu(self: "ShelfVContainer | ShelfHContainer", item: "ShelfSplitterContainer.Handle"):
        if not item: return
        idx = item.getIdx()

        menu = QMenu()
        toggle_visibility_action = menu.addAction("")
        toggle_visibility_action.setText("Hide Handle")
        toggle_visibility_action.setCheckable(True)
        toggle_visibility_action.setChecked(True if idx in self.handles_hidden else False)
        toggle_visibility_action.triggered.connect(lambda: ShelfSplitterContainer.onHandleVisibilityToggled(self, idx))

        menu.exec_(QCursor.pos())

class ShelfVContainer(ShelfContainer, VContainer):
    sigLayoutSaveRequest = pyqtSignal()

    def __init__(self, area):
        VContainer.__init__(self, area)
        ShelfContainer.__init__(self)
        self.handles_hidden = []

    def saveState(self):
        return VContainer.saveState(self) | ShelfContainer.saveState(self) | ShelfSplitterContainer.saveState(self)

    def restoreState(self, state):
        VContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)
        ShelfSplitterContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        ShelfContainer.setItemFold(self, item, state)
        ShelfSplitterContainer.setItemFold(self, item, state)

    def createHandle(self):
        return ShelfSplitterContainer.createHandle(self)
    
    def setEditMode(self, state):
        ShelfContainer.setEditMode(self, state)
        ShelfSplitterContainer.setEditMode(self, state)

class ShelfHContainer(ShelfContainer, HContainer):
    sigLayoutSaveRequest = pyqtSignal()

    def __init__(self, area):
        HContainer.__init__(self, area)
        ShelfContainer.__init__(self)
        self.handles_hidden = []

    def saveState(self):
        return HContainer.saveState(self) | ShelfContainer.saveState(self)| ShelfSplitterContainer.saveState(self)

    def restoreState(self, state):
        HContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)
        ShelfSplitterContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        ShelfContainer.setItemFold(self, item, state)
        ShelfSplitterContainer.setItemFold(self, item, state)

    def createHandle(self):
        return ShelfSplitterContainer.createHandle(self)
    
    def setEditMode(self, state):
        ShelfContainer.setEditMode(self, state)
        ShelfSplitterContainer.setEditMode(self, state)

class ShelfTContainer(ShelfContainer, TContainer):
    def __init__(self, area):
        TContainer.__init__(self, area)
        ShelfContainer.__init__(self)

    def saveState(self):
        return TContainer.saveState(self) | ShelfContainer.saveState(self)
    
    def restoreState(self, state):
        TContainer.restoreState(self, state)
        ShelfContainer.restoreState(self, state)

    def setItemFold(self, item: "ShelfDock", state: bool):
        #if not ShelfContainer.setItemFold(self, item, state): return
        #if state: item.show()
        #else: item.hide()

        #if all(self.widget(x).isHidden() for x in range(self.count())) == True: self.hide()
        #else: self.show()
        pass

