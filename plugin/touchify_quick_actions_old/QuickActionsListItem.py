from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from touchify.src.config.triggers.Trigger import Trigger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.managers.ActionManager import ActionManager


class QuickActionsList(QListWidget):
    sigContextMenuRequested = pyqtSignal(int)
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setGridSize(QSize(64,64))
        self.setUniformItemSizes(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        #self.setAcceptDrops(True)
        #self.setDragEnabled(True)
        #self.setMovement(QListWidget.Movement.Snap)
        #self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        #self.setDefaultDropAction(Qt.DropAction.TargetMoveAction)

    def dragMoveEvent(self, event):
        if ((target := self.row(self.itemAt(event.pos()))) ==
            (current := self.currentRow()) + 1 or
            (current == self.count() - 1 and target == -1)):
            event.ignore()
        else:
            super().dragMoveEvent(event)


class QuickActionsListItem(QListWidgetItem):
    def __init__(self, parent: QListWidget, trigger_data: Trigger, action_manager:  "ActionManager") -> None:
        super().__init__(parent)
        self.__mgr_actions = action_manager
        self.__trigger_data: Trigger = None
        self.setSizeHint(QSize(64,64))
        self.setTrigger(trigger_data)

    def listWidget(self) -> QuickActionsList:
        return super().listWidget()

    def getPreview(self):
        return self.listWidget().itemWidget(self)
        
    def getTrigger(self):
        return self.__trigger_data
    
    def setTrigger(self, data: Trigger):
        self.__trigger_data = data

        list_widget = self.listWidget()
        last_preview = self.getPreview()

        if last_preview:
            old_preview = list_widget.itemWidget(self)
            del old_preview

        preview: QuickActionsListItemPreview = self.__mgr_actions.Create_Button(list_widget.parentWidget(), self.__trigger_data, QuickActionsListItemPreview)
        if not preview: preview = QuickActionsListItemPreview(list_widget)
        preview.setListItem(self)
        list_widget.setItemWidget(self, preview)
    
    def onContextMenu(self):
        index = self.listWidget().row(self)
        self.listWidget().sigContextMenuRequested.emit(index)

class QuickActionsListItemPreview(TriggerButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__listItem: QuickActionsListItem = None
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def setListItem(self, item: "QuickActionsListItem"):
        self.__listItem = item
        self.setFixedSize(self.__listItem.sizeHint())

    def contextMenuEvent(self, a0):
        self.__listItem.onContextMenu()
        return super().contextMenuEvent(a0)
    
    def mousePressEvent(self, event: QMouseEvent):
        event.ignore()
        #self.__mousePressPos = None
        #if event.button() == Qt.MouseButton.LeftButton:
            #self.__mousePressPos = event.globalPos()

        #super(QuickActionsListItemPreview, self).mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        event.ignore()
        #if event.buttons() == Qt.MouseButton.LeftButton:
        #super(QuickActionsListItemPreview, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        event.ignore()
        #if self.__mousePressPos is not None:
            #moved = event.globalPos() - self.__mousePressPos 
            #if moved.manhattanLength() > 3:
                #event.ignore()
                #return

        #super(QuickActionsListItemPreview, self).mouseReleaseEvent(event)
