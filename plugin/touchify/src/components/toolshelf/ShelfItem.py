from uuid import uuid4
from touchify.src.components.special.DockerContainer import DockerContainer
from touchify.src.components.toolshelf.ShelfItemOverlay import ShelfItemOverlay
from touchify.src.config.toolshelf.ToolshelfDock import ToolshelfDock
from touchify.src.alib_pyqtgraph.dockarea.Dock import Dock, DockLabel
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ShelfItem(Dock):

    sigDuplicateRequested = QtCore.pyqtSignal(str)
    sigEditRequested = QtCore.pyqtSignal(str)
    sigDeleteRequested = QtCore.pyqtSignal(str)

    def __init__(self, _config: ToolshelfDock, uuid:str | None = None, area=None, size=(10, 10), widget=None, hideTitle=False, autoOrientation=True, label=None, **kargs):
        _uuid = str(uuid4()) if uuid == None else uuid
        super().__init__(_uuid, area, size, widget, hideTitle, autoOrientation, ShelfLabel(_uuid, **kargs), **kargs)
        self.label.hide()

        self._name = _uuid
        self.dock_settings = _config
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.editableDragArea = ShelfItemOverlay()
        self.editableDragArea.dock = self
        self.editableDragArea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.topLayout.addWidget(self.editableDragArea, 1, 1)

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

        self.setEditMode(False)

        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction("Edit", self.onEditShelfItemRequested)
        self.context_menu.addAction("Clone", self.onDuplicateShelfItemRequested)
        self.context_menu.addSeparator()
        self.context_menu.addAction("Delete Item", self.onDeleteShelfItemRequested)


    def hideTitleBar(self):
        self.updateStyle()

    def showTitleBar(self):
        self.updateStyle()


    def updateStyle(self):
        ## updates orientation and appearance of title bar
        if self.container() is None:
            self.label.hide()
            self.widgetArea.setStyleSheet(self.nStyle)
        elif self.container().type() == 'tab':
            self.label.show()
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
            self.label.hide()
            self.widgetArea.setStyleSheet(self.nStyle)

    def setEditMode(self, enabled: bool):
        self.editableDragArea.setVisible(enabled)
        self.editableDragArea.setEnabled(enabled)
        self.updateStyle()

    def onDuplicateShelfItemRequested(self):
        self.sigDuplicateRequested.emit(self._name)

    def onEditShelfItemRequested(self):
        self.sigEditRequested.emit(self._name)
    
    def onDeleteShelfItemRequested(self):
        self.sigDeleteRequested.emit(self._name)

    def onContextMenu(self):
        self.context_menu.exec_(QCursor.pos())

    def startDrag(self):
        if self.editableDragArea.isEnabled():
            return super().startDrag()
        
    def startDrag(self):
        if self.editableDragArea.isEnabled():
            return super().startDrag()

    def float(self):
        #return super().float()
        pass

    def close(self) -> None:
        children = self.findChildren(DockerContainer)
        for child in children:
            child.shutdownWidget()

        return super().close()

    def name(self):
        return self._name

    def setUUID(self, uuid: str):
        self._name = uuid

class ShelfLabel(DockLabel):

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