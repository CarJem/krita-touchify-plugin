from typing import TYPE_CHECKING
from uuid import uuid4

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPaintEvent, QPainter, QPen
from touchify.src.components.widgets.other.DockerContainer import DockerContainer
from touchify.src.components.toolshelf.ShelfContainer import ShelfContainer
from touchify.src.components.toolshelf.ShelfDockDrop import ShelfDropDock
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.alib_pyqtgraph.dockarea.Dock import Dock, DockLabel
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from touchify.src.extensions import pyqt_extensions as PyQtExt



class ShelfDock(Dock):

    sigContextMenuRequested = QtCore.pyqtSignal(QPoint, str)
    sigContainerHoverUpdated = QtCore.pyqtSignal(bool, str)

    def __init__(self, _config: ToolshelfDock, uuid:str | None = None, area=None, size=(10, 10), widget=None, hideTitle=False, autoOrientation=True, label=None, **kargs):
        _uuid = str(uuid4()) if uuid == None else uuid
        super().__init__(_uuid, area, size, widget, hideTitle, autoOrientation, ShelfDockLabel(_uuid), **kargs)
        self.dockdrop = ShelfDropDock(self)
        self._titleText = _uuid
        self._folded = False
        self.label: ShelfDockLabel
        self.hideTitleBar(False)


        self._name = _uuid
        self._dockSettings = _config
        self._parentAreaId: str = ""
        self._currentTool: str = ""
        self._isCollapsible = True
        self._isEditMode = False


        __requiredTools = _config.requires_specific_tool.split(",")
        if "" in __requiredTools: __requiredTools.remove("")
        self._requiredTools: list[str] = __requiredTools
        self._invertRequiredTools: bool = _config.invert_required_tools


        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.editableDragArea = ShelfDockOverlay()
        self.editableDragArea.sigMouseOverChanged.connect(self.onMouseOverChanged)
        self.editableDragArea.dock = self
        self.editableDragArea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.topLayout.addWidget(self.editableDragArea, 1, 1)

        self.dockdrop.raiseOverlay()
        self.hStyle = """
        Dock > QWidget {
            border: 0px solid transparent;
            border-radius: 0px;
        }"""
        self.vStyle = """
        Dock > QWidget {
            border: 0px solid transparent;
            border-radius: 0px;
        }"""
        self.nStyle = """
        Dock > QWidget {
            border: 0px solid transparent;
            border-radius: 0px;
        }"""
        self.dragStyle = """
        Dock > QWidget {
            border: 0px solid transparent;
            border-radius: 0px;
        }"""

        self.editableDragArea.sigRightClicked.connect(self.onContextMenu)
        self.editableDragArea.sigClicked.connect(self.onClicked)

        self.setEditMode(False)

    def isSelected(self):
        return self.editableDragArea.isSelected
    
    def setParentAreaId(self, value: str):
        self._parentAreaId = value
        self.dockdrop.setParentAreaId(value)

    def accessible(self, id: str):
        return id == self._parentAreaId

    def title(self):
        return self._titleText

    def setTitle(self, text):
        self._titleText = text
        if not PyQtExt.CommonHelpers.isDeleted(self.label):
            self.label.setText(self._titleText)

    def revalidateTitlebar(self):
        if PyQtExt.CommonHelpers.isDeleted(self.label):
            self.label = ShelfDockLabel(self._titleText)
            self.label.dock = self

    def hideTitleBar(self, updateStyle = True):
        self.revalidateTitlebar()
        self.label.hide()
        self.labelHidden = True
        if updateStyle: self.updateStyle()

    def showTitleBar(self, updateStyle = True):
        self.revalidateTitlebar()
        self.label.show()
        self.labelHidden = False
        if updateStyle: self.updateStyle()

    def updateStyle(self):
        ## updates orientation and appearance of title bar
        if self.container() is None:
            self.hideTitleBar(False)
            self.widgetArea.setStyleSheet(self.nStyle)
        elif self.container().type() == 'tab':
            self.showTitleBar(False)
            if self.orientation == 'vertical':
                self.label.setOrientation('vertical')
                if self.moveLabel:
                    self.topLayout.addWidget(self.label, 1, 0)
                self.widgetArea.setStyleSheet(self.vStyle)
            else:
                self.label.setOrientation('horizontal')
                if self.moveLabel:
                    self.topLayout.addWidget(self.label, 0, 1)
                self.widgetArea.setStyleSheet(self.hStyle)
        else:
            self.hideTitleBar(False)
            self.widgetArea.setStyleSheet(self.nStyle)

    def setEditMode(self, enabled: bool):
        self._isEditMode = enabled
        container = self.container()
        if isinstance(container, ShelfContainer):
            container: ShelfContainer
            container.setEditMode(enabled)
        self.editableDragArea.setEditMode(enabled)
        self.updateStyle()
        self.sync()

    def matchesCurrentTool(self):
        if self._invertRequiredTools:
            return self._currentTool not in self._requiredTools and self._currentTool != "" and len(self._requiredTools) != 0
        else:
            return self._currentTool in self._requiredTools or self._currentTool == "" or len(self._requiredTools) == 0

    def onToolChanged(self, current_tool: str):
        self._currentTool = current_tool
        self.sync()

    def onMouseOverChanged(self, state: bool):
        self.sigContainerHoverUpdated.emit(state, self._name)

    def onContextMenu(self):
        self.sigContextMenuRequested.emit(QCursor.pos(), self._name)

    def onClicked(self):
        pass

    def setFold(self, state: bool):
        if self._folded != state:
            self._folded = state
            if(ShelfContainer.isContainer(self.container())):
                cnt = ShelfContainer.asContainer(self.container())
                cnt.setItemFold(self, self._folded)

    def sync(self):
        if self.matchesCurrentTool() or self._isEditMode: self.setFold(True)
        else: self.setFold(False)

    def setOrientation(self, o='auto', force=False):
        self.revalidateTitlebar()
        return super().setOrientation(o, force)

    def startDrag(self):
        if self.editableDragArea.isEnabled():
            return super().startDrag()

    def float(self):
        pass

    def close(self) -> None:
        self.revalidateTitlebar()
        
        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        return super().close()
    
    def showEvent(self, a0):
        return super().showEvent(a0)
    
    def hideEvent(self, a0):      
        return super().hideEvent(a0)

    def name(self):
        return self._name

    def setUUID(self, uuid: str):
        self._name = uuid

class ShelfDockLabel(DockLabel):
    def __init__(self, text, closable=False, fontSize="12px"):
        super().__init__(text, closable, fontSize)

    def updateStyle(self):
        r = '0px'
        if self.dim:
            fg = 'palette(text)'
            bg = 'palette(alternate-base)'
            border = 'palette(alternate-base)'
        else:
            fg = 'palette(text)'
            bg = 'palette(highlight)'
            border = 'palette(highlight)'

        if self.orientation == 'vertical':
            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 0px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
                font-size: %s;
            }""" % (bg, fg, r, r, border, self.fontSize)
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 0px solid %s;
                padding-left: 3px;
                padding-right: 3px;
                font-size: %s;
            }""" % (bg, fg, r, r, border, self.fontSize)
            self.setStyleSheet(self.hStyle)

class ShelfDockOverlay(QtWidgets.QWidget):
    sigClicked = QtCore.pyqtSignal()
    sigMouseOverChanged = QtCore.pyqtSignal(bool)
    sigRightClicked = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget = None):
        QtWidgets.QWidget.__init__(self, parent)

        self.dock = None
        self.isMouseOver = False
        self.isSelected = False
        self.isEditMode = False

        self.personallayout = QtWidgets.QGridLayout()
        self.personallayout.setContentsMargins(0, 0, 0, 0)
        self.personallayout.setSpacing(0)

        self.sigMouseOverChanged.connect(self.onMouseOverChanged)

        self.setLayout(self.personallayout)

    def setEditMode(self, enabled: bool):
        self.isEditMode = enabled
        self.setVisible(enabled)
        self.setEnabled(enabled)
        if enabled == False and self.isSelected:
            self.isSelected = False
    
    def toggleSelection(self):
        if self.isEditMode:
            self.isSelected = not self.isSelected
            self.repaint()

    def onMouseOverChanged(self, state: bool):
        self.isMouseOver = state
        self.repaint()

    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        painter = QPainter(self)

        if self.isSelected:
            painter.setOpacity(0.2)
            painter.setBrush(Qt.GlobalColor.blue)
            painter.setPen(QPen(Qt.GlobalColor.blue))
            painter.drawRect(event.rect())

        
        painter.setOpacity(0.2 if self.isMouseOver else 0.0)
        painter.setBrush(Qt.GlobalColor.blue)
        painter.setPen(QPen(Qt.GlobalColor.blue))
        painter.drawRect(event.rect())

        painter.end()

    def enterEvent(self, a0):
        self.sigMouseOverChanged.emit(True)
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        self.sigMouseOverChanged.emit(False)
        return super().leaveEvent(a0)

    def mousePressEvent(self, ev):
        lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
        self.pressPos = lpos
        self.mouseMoved = False
        ev.accept()

    def mouseMoveEvent(self, ev):
        if not self.mouseMoved:
            lpos = ev.position() if hasattr(ev, 'position') else ev.localPos()
            self.mouseMoved = (lpos - self.pressPos).manhattanLength() > QtWidgets.QApplication.startDragDistance()

        if self.mouseMoved and ev.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.dock.startDrag()
        ev.accept()

    def mouseReleaseEvent(self, ev):
        ev.accept()
        if not self.mouseMoved:
            if ev.button() == QtCore.Qt.MouseButton.RightButton:
                self.sigRightClicked.emit()
            else:
                self.sigClicked.emit()

    def mouseDoubleClickEvent(self, ev):
        super(ShelfDockOverlay,self).mouseDoubleClickEvent(ev)

    def resizeEvent (self, ev):
        super(ShelfDockOverlay,self).resizeEvent(ev)

