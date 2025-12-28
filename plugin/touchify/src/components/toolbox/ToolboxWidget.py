# SPDX-FileCopyrightText: 2005-2009 Thomas Zander <zander@kde.org>
# SPDX-FileCopyrightText: 2009 Peter Simonsson <peter.simonsson@gmail.com>
# SPDX-FileCopyrightText: 2010 Cyrille Berger <cberger@cberger.net>
# SPDX-FileCopyrightText: 2022 Alvin Wong <alvin@alvinhc.com>
#
# SPDX-License-Identifier: LGPL-2.0-or-later

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.alib_pyqtgraph.Qt import QtWidgets
from touchify.src.components.toolbox.ToolboxButton import ToolboxButton
from touchify.src.components.toolbox.ToolboxLayout import ToolboxEmptySpace, ToolboxLayout, Section
from touchify.src.components.widgets.triggers.TriggerButton import TriggerButton
from jemlib.alib_vaporjem.extensions import pyqt_extensions  as PyQtExt

BUTTON_MARGIN = 10


class ToolboxWidget(QWidget):

    sigToolContextMenuRequested = pyqtSignal(str, str, QPoint)
    sigDragStarted = pyqtSignal(str, str)
    sigDragEnded = pyqtSignal(str, str)
    sigSectionContextMenuRequested = pyqtSignal(str, QPoint)
    sigContextMenuRequested = pyqtSignal(QPoint)

    def __init__(self):
        super(ToolboxWidget, self).__init__()
        
        self._toolboxLayout = ToolboxLayout(self)
        self.buttons: list[QtWidgets.QToolButton] = []
        self.selectedButton = None
        self.buttonsByToolId = {}
        self.sections: dict[str, Section] = {}
        self.buttonGroup = QButtonGroup(self)
        self.visibilityCodes = {}
        self.floating = False
        self.iconSize = 16
        self.contextIconSizes = {}
        self.defaultIconSizeAction = None
        self.orientation = Qt.Orientation.Vertical
        self._isEditMode = False
        self._blockNextContextMenu = False

        self.addSection(Section(self), "main")
        self.addSection(Section(self), "dynamic")
        
        self.applyIconSize()
        self.setButtonsVisible([])
    
    def __del__(self):
        del self.d
    
    def reset(self):
        PyQtExt.CommonHelpers.clearLayout(self._toolboxLayout)

        for btn in self.buttons:
            btn.deleteLater()
        self.buttons.clear()
        self.buttons = []

        self.sections: dict[str, Section] = {}
        self.visibilityCodes = {}

        self.addSection(Section(self), "main")
        self.addSection(Section(self), "dynamic")

    def setIconSize(self, iconSize: int):
        self.iconSize = iconSize
        self.applyIconSize()

    def applyIconSize(self):
        for button in self.buttons:
            button.setIconSize(QSize(self.iconSize, self.iconSize))
        
        for section in self.sections.values():
            section.setButtonSize(QSize(self.iconSize + BUTTON_MARGIN, self.iconSize + BUTTON_MARGIN))
    
    def addButton(self, button: ToolboxButton | ToolboxEmptySpace, section: str, priority: int, item_id: str):
        button.setObjectName(item_id)
        self.buttons.append(button)

        if isinstance(button, ToolboxButton):
            button.sigContextMenuRequested.connect(self.onToolContextMenu)
            button.sigDragStarted.connect(self.onToolDragStarted)
            button.sigDragEnded.connect(self.onToolDragEnded)
        
        sectionToBeAddedTo = None
        section = section
        if QApplication.applicationName() in section:
            sectionToBeAddedTo = "main"
        elif "main" in section:
            sectionToBeAddedTo = "main"
        elif "dynamic" in section:
            sectionToBeAddedTo = "dynamic"
        else:
            sectionToBeAddedTo = section
        
        sectionWidget = self.sections.get(sectionToBeAddedTo)
        if sectionWidget is None:
            sectionWidget = Section(self)
            self.addSection(sectionWidget, sectionToBeAddedTo)
        sectionWidget.addButton(button, priority)
        
        self.buttonGroup.addButton(button)
        self.buttonsByToolId[item_id] = button
        
        self.visibilityCodes[button] = "/always"
    
    def setDesiredRowCount(self, val: int):
        self._toolboxLayout.setPreferredRowCount(val)
    
    def addSection(self, section: Section, name: str):
        section.setEditMode(self._isEditMode)
        section.sigContextMenuRequested.connect(self.onSectionContextMenu)
        section.sigItemContextMenuRequested.connect(self.onToolContextMenu)
        section.setName(name)
        self._toolboxLayout.addSection(section)
        self.sections[name] = section

    def setButtonsVisible(self, codes: list[str]):
        for button in self.visibilityCodes.keys():
            code = self.visibilityCodes[button]
            
            if code.startswith("flake/"):
                continue
            
            if code.endswith("/always"):
                button.setVisible(True)
                button.setEnabled(True)
            elif not code:
                button.setVisible(True)
                button.setEnabled(len(codes) != 0)
            else:
                button.setVisible(code in codes)
        
        self.layout().invalidate()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)

        if self.layout() == None:
            return
        
        sections = list(self.sections.values())
        halfSpacing = self.layout().spacing()
        if halfSpacing > 0:
            halfSpacing //= 2
        
        for section in sections:
            styleoption = QStyleOption()
            styleoption.palette = self.palette()
            
            if section.separators() & Section.Separators.SeparatorTop:
                y = section.y() - halfSpacing
                styleoption.state = QStyle.State_None
                styleoption.rect = QRect(section.x(), y - 1, section.width(), 2)
                
                self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorToolBarSeparator, styleoption, painter)
            
            if section.separators() & Section.Separators.SeparatorLeft and section.isLeftToRight():
                x = section.x() - halfSpacing
                styleoption.state = QStyle.State_Horizontal
                styleoption.rect = QRect(x - 1, section.y(), 2, section.height())
                
                self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorToolBarSeparator, styleoption, painter)
            elif section.separators() & Section.Separators.SeparatorLeft and section.isRightToLeft():
                x = section.x() + section.width() + halfSpacing
                styleoption.state = QStyle.State_Horizontal
                styleoption.rect = QRect(x - 1, section.y(), 2, section.height())
                
                self.style().drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorToolBarSeparator, styleoption, painter)
        
        painter.end()
    
    def changeEvent(self, event: QEvent):
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:
            for button in self.buttons:
                toolBoxButton = button
                if isinstance(toolBoxButton, TriggerButton):
                    pass
    
    def setOrientation(self, orientation: Qt.Orientation):
        self.orientation = orientation
        self._toolboxLayout.setOrientation(orientation)
        QTimer.singleShot(0, self.update)
        for section in self.sections.values():
            section.setOrientation(orientation)

    def setEditMode(self, enabled: bool):
        self._isEditMode = enabled
        for key, value in self.sections.items():
            value.setEditMode(enabled)

    def onSectionContextMenu(self, uuid: str, pos: QPoint):
        print("Section Context Menu")
        self.sigSectionContextMenuRequested.emit(uuid, pos)

    def onToolContextMenu(self, section_uuid: str, tool_uuid: str, pos: QPoint):
        print("Tool Context Menu")
        self.sigToolContextMenuRequested.emit(section_uuid, tool_uuid, pos)

    def onToolDragStarted(self, section_uuid: str, tool_uuid: str):
        self.sigDragStarted.emit(section_uuid, tool_uuid)

    def onToolDragEnded(self, section_uuid: str, tool_uuid: str):
        self.sigDragEnded.emit(section_uuid, tool_uuid)
    
    def setFloating(self, v: bool):
        self.floating = v

    def toolBoxLayout(self):
        return self._toolboxLayout
    
    def contextMenuEvent(self, a0):
        print("Context Menu")
        self.sigContextMenuRequested.emit(a0.globalPos())
        a0.accept()
        return

