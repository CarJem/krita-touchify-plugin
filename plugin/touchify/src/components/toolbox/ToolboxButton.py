from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from touchify.src.config.toolbox.ToolboxDataItem import ToolboxDataItem

UNIQUE_DRAG_ID = "####touchify/toolbox_button###"

class ToolboxButton(TriggerButton):

    sigContextMenuRequested = pyqtSignal(str, str, QPoint)
    sigDragStarted = pyqtSignal(str, str)
    sigDragEnded = pyqtSignal(str, str)
    sigMouseOverChanged = pyqtSignal(bool)
        
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self._isEditMode = False
        self._isHovered = False
        self._mouseMoved = False
        self._pressPos: QPoint = QPoint()
        self._uuid = ""
        self._cuuid = ""
        self._data: ToolboxDataItem = ToolboxDataItem()
        self._dataIndex = 0
        self._isDragging = False
        self._hasDragDetection = False

        self.sigMouseOverChanged.connect(self.onMouseOverChanged)

    def setEditMode(self, enabled: bool):
        self._isEditMode = enabled

    def setData(self, data: ToolboxDataItem, data_index: int, item_uuid: str, cat_uuid: str):
        self._data = data
        self._dataIndex = data_index
        self._uuid = item_uuid
        self._cuuid = cat_uuid

    def getCuuid(self):
        return self._cuuid
    
    def getUuid(self):
        return self._uuid

    def matches(self, cat_uuid: str, item_uuid: str):
        return self._uuid == item_uuid and self._cuuid == cat_uuid


    #region Signals

    def onMouseOverChanged(self, state: bool):
        if self._isEditMode:
            self._isHovered = state
            self.repaint()

    #endregion

    #region Events

    def enterEvent(self, a0):
        self.sigMouseOverChanged.emit(True)
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        self.sigMouseOverChanged.emit(False)
        return super().leaveEvent(a0)

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        painter = QPainter(self)

        highlight = self.window().palette().highlight().color().lighter(125)

        painter.setOpacity(0.6 if self._isHovered else 0.0)
        painter.setBrush(highlight)
        painter.setPen(QPen(highlight))
        painter.drawRect(self.rect())

        painter.end()
    
    def mousePressEvent(self, ev):
        if self._isEditMode: self.editModeMousePressEvent(ev)
        else: return super().mousePressEvent(ev)
        
    def mouseMoveEvent(self, ev: QMouseEvent):
        if self._isEditMode: self.editModeMouseMoveEvent(ev)
        else: return super().mouseMoveEvent(ev)
    
    def mouseReleaseEvent(self, ev: QMouseEvent):
        self._isDragging = False
        if self._isEditMode: self.editModeMouseReleaseEvent(ev)
        else: return super().mouseReleaseEvent(ev)

    def editModeMouseMoveEvent(self, ev: QMouseEvent):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        self._pressPos = lpos
        self._mouseMoved = True
        ev.accept()

    def editModeMousePressEvent(self, ev: QMouseEvent):
        if not self._mouseMoved:
            lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
            self._mouseMoved = (lpos - self._pressPos).manhattanLength() > QApplication.startDragDistance()

        if self._mouseMoved and ev.buttons() == Qt.MouseButton.LeftButton:
            self.startDrag()

    def editModeMouseReleaseEvent(self, ev: QMouseEvent):
        if not self._mouseMoved:
            if ev.button() == Qt.MouseButton.RightButton:
                self.sigContextMenuRequested.emit(self._cuuid, self._uuid, ev.globalPos())

    #endregion

    #region Drag Functions

    def setDragDetection(self, state: bool):
        self._hasDragDetection = state

    def startDrag(self):
        if self._isDragging: return

        self._isDragging = True
        self.sigDragStarted.emit(self._cuuid, self._uuid)
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(UNIQUE_DRAG_ID)
        drag.setMimeData(mime_data)
        drag.setPixmap(self.icon().pixmap(32, 32))
        drag.setHotSpot(QPoint(10, 10))
        drag.exec_(Qt.DropAction.MoveAction)

        self._isDragging = False
        self.sigDragEnded.emit(self._cuuid, self._uuid)
        
        
    #endregion
        
