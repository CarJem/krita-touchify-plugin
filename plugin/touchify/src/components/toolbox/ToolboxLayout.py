"""
SPDX-FileCopyrightText: 2005-2009 Thomas Zander <zander@kde.org>
SPDX-FileCopyrightText: 2009 Peter Simonsson <peter.simonsson@gmail.com>
SPDX-FileCopyrightText: 2010 Cyrille Berger <cberger@cberger.net>

SPDX-License-Identifier: LGPL-2.0-or-later
"""

from enum import Flag, auto
from typing import Optional
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtWidgets import QLayout, QWidget, QAbstractButton, QLayoutItem, QWidgetItem, QFrame, QToolButton

from jemlib.alib_pyqtgraph.Qt import QtCore

class ToolboxEmptySpace(QToolButton):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._cuuid = None

    def setCuuid(self, val: str):
        self._cuuid = val

    def getCuuid(self):
        return self._cuuid
    
    def paintEvent(self, a0):
        a0.ignore()
        #return super().paintEvent(a0)

class SectionLayout(QLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.m_orientation = Qt.Vertical
        self.m_buttonSize = QSize()
        self.m_priorities: dict[QAbstractButton, int] = {}  # QMap<QAbstractButton*, int>
        self.m_items: list[QWidgetItem] = []  # QList<QWidgetItem*>

    def __del__(self):
        # qDeleteAll( m_items );
        # In Python, we need to manually delete items
        while self.m_items:
            item = self.m_items.pop()
            del item
        self.m_items.clear()

    def addButton(self, button: QAbstractButton, priority: int):
        self.addChildWidget(button)
        if priority in self.m_priorities.values():
            print(f"Warning: Button {button} has a conflicting priority")

        self.m_priorities[button] = priority
        index = 1
        # Q_FOREACH (QWidgetItem *item, m_items)
        for item in self.m_items:
            if self.m_priorities.get(item.widget(), 0) > priority:
                break
            index += 1
        self.m_items.insert(index - 1, QWidgetItem(button))

    def sizeHint(self) -> QSize:
        # This is implemented just to not freak out GammaRay, in practice
        # this doesn't have any effect on the layout.
        if self.m_orientation == Qt.Vertical:
            return QSize(self.m_buttonSize.width(), self.m_buttonSize.height() * self.count())
        else:
            return QSize(self.m_buttonSize.width() * self.count(), self.m_buttonSize.height())

    def addItem(self, item: QLayoutItem):
        assert False, "addItem should not be called directly"

    def itemAt(self, i: int) -> Optional[QLayoutItem]:
        if self.m_items.__len__() <= i:
            return None
        return self.m_items[i]

    def takeAt(self, i: int) -> QLayoutItem:
        return self.m_items.pop(i)

    def count(self) -> int:
        return self.m_items.__len__()

    def setGeometry(self, rect: QRect):
        x = 0
        y = 0
        size = self.buttonSize()
        if self.m_orientation == Qt.Vertical:
            # foreach (QWidgetItem* w, m_items)
            for w in self.m_items:
                if w.isEmpty():
                    continue
                if self.parentWidget().isLeftToRight():
                    realX = x
                else:
                    realX = rect.width() - x - size.width()
                w.widget().setGeometry(QRect(realX, y, size.width(), size.height()))
                x += size.width()
                if x + size.width() > rect.width():
                    x = 0
                    y += size.height()
        else:
            # foreach (QWidgetItem* w, m_items)
            for w in self.m_items:
                if w.isEmpty():
                    continue
                if self.parentWidget().isLeftToRight():
                    realX = x
                else:
                    realX = rect.width() - x - size.width()
                w.widget().setGeometry(QRect(realX, y, size.width(), size.height()))
                y += size.height()
                if y + size.height() > rect.height():
                    x += size.width()
                    y = 0

    def update(self):
        return super().update()

    def setButtonSize(self, size: QSize):
        self.m_buttonSize = size
        for item in self.m_items:
            item.invalidate()

    def buttonSize(self) -> QSize:
        return self.m_buttonSize

    def setOrientation(self, orientation: Qt.Orientation):
        self.m_orientation = orientation

class Section(QFrame):

    sigContextMenuRequested = QtCore.pyqtSignal(str, QPoint)

    class SeparatorFlag(Flag):
        SeparatorTop = auto()  # 0x0001
        SeparatorBottom = auto()  # 0x0002
        SeparatorRight = auto()  # 0x0004
        SeparatorLeft = auto()  # 0x0008

    # Type alias for Separators
    Separators = SeparatorFlag

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.m_layout = SectionLayout(self)
        self.m_name = ""
        self.m_separators = Section.SeparatorFlag(0)
        self._isEditMode = False
        self._blockNextContextMenu = False
        
        # Re-enable this when we need to debug the section layout again.
        # setAutoFillBackground(true);
        # static int i = 0;
        # switch(i) {
        # case 0:
        #     setStyleSheet("background-color:red");
        #     break;
        # case 1:
        #     setStyleSheet("background-color:blue");
        #     break;
        # case 2:
        #     setStyleSheet("background-color:green");
        #     break;
        # case 3:
        #     setStyleSheet("background-color:yellow");
        #     break;
        # case 4:
        #     setStyleSheet("background-color:white");
        #     break;
        # case 5:
        #     setStyleSheet("background-color:gray");
        #     break;
        # case 6:
        #     setStyleSheet("background-color:lime");
        #     break;
        # case 7:
        #     setStyleSheet("background-color:silver");
        #     break;
        # case 8:
        #     setStyleSheet("background-color:purple");
        #     break;
        # default:
        #     setStyleSheet("background-color:maroon");
        #     break;
        # }
        # i++;

    def setEditMode(self, val: bool):
        self._isEditMode = val

    def contextMenuEvent(self, a0):
        if self._isEditMode: 
            self.sigContextMenuRequested.emit(self.m_name, a0.globalPos())
            a0.accept()
            return
        return super().contextMenuEvent(a0)

    def addButton(self, button: QAbstractButton, priority: int):
        self.m_layout.addButton(button, priority)

    def setName(self, name: str):
        self.setObjectName(name)
        self.m_name = name

    def name(self) -> str:
        return self.m_name

    def setButtonSize(self, size: QSize):
        self.m_layout.setButtonSize(size)

    def iconSize(self) -> QSize:
        return self.m_layout.buttonSize()

    def visibleButtonCount(self) -> int:
        count = 0
        for i in range(self.m_layout.count() - 1, -1, -1):
            if not self.m_layout.itemAt(i).isEmpty():
                count += 1
        return count

    def setSeparator(self, separators):
        self.m_separators = separators

    def separators(self):
        return self.m_separators

    def setOrientation(self, orientation: Qt.Orientation):
        self.m_layout.setOrientation(orientation)

class ToolboxLayout(QLayout):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.m_orientation = Qt.Vertical
        self.m_sections: list[QWidgetItem] = []
        self.m_idealRowCount = 2
        self.setSpacing(6)

    def setPreferredRowCount(self, val: int):
        self.m_idealRowCount = val

    def __del__(self):
        while self.m_sections:
            item = self.m_sections.pop()
            del item
        self.m_sections.clear()

    def sizeHint(self) -> QSize:
        # Prefer showing two rows/columns by default
        twoIcons = self.m_sections[0].widget().iconSize() * self.m_idealRowCount
        length = self.doLayout(QRect(QPoint(), twoIcons), False)
        if self.m_orientation == Qt.Vertical:
            return QSize(twoIcons.width(), length)
        else:
            return QSize(length, twoIcons.height())

    def minimumSize(self) -> QSize:
        if not self.m_sections:
            return QSize()
        oneIcon = self.m_sections[0].widget().iconSize()
        return oneIcon

    def addSection(self, section: Section):
        self.addChildWidget(section)

        iterator_index = 0
        defaults = 2  # skip the first two as they are the 'main' and 'dynamic' sections.
        while iterator_index < len(self.m_sections):
            if defaults < 0 and self.m_sections[iterator_index].widget().name() > section.name():
                break
            defaults -= 1
            iterator_index += 1
        self.m_sections.insert(iterator_index, QWidgetItem(section))

    def addItem(self, item: QLayoutItem):
        assert False, "addItem should not be called directly"  # don't let anything else be added. (code depends on this!)

    def itemAt(self, i: int) -> Optional[QLayoutItem]:
        if 0 <= i < len(self.m_sections):
            return self.m_sections[i]
        return None

    def takeAt(self, i: int) -> QLayoutItem:
        return self.m_sections.pop(i)

    def count(self) -> int:
        return len(self.m_sections)

    def setGeometry(self, rect: QRect):
        QLayout.setGeometry(self, rect)
        self.doLayout(rect, True)

    def hasHeightForWidth(self) -> bool:
        return self.m_orientation == Qt.Vertical

    def heightForWidth(self, width: int) -> int:
        if self.m_orientation == Qt.Vertical:
            height = self.doLayout(QRect(0, 0, width, 0), False)
            return height
        else:
            return -1

    def widthForHeight(self, height: int) -> int:
        """
        For calculating the width from height by KoToolBoxScrollArea.
        QWidget doesn't actually support trading width for height, so it needs to
        be handled specifically.
        """
        if self.m_orientation == Qt.Horizontal:
            width = self.doLayout(QRect(0, 0, 0, height), False)
            return width
        else:
            return -1

    def setOrientation(self, orientation: Qt.Orientation):
        self.m_orientation = orientation
        self.invalidate()

    def doLayout(self, rect: QRect, notDryRun: bool) -> int:
        if not self.m_sections:
            return 0

        # the names of the variables assume a vertical orientation,
        # but all calculations are done based on the real orientation
        isVertical = self.m_orientation == Qt.Vertical

        iconSize = self.m_sections[0].widget().iconSize()

        maxWidth = rect.width() if isVertical else rect.height()
        # using min 1 as width to e.g. protect against div by 0 below
        iconWidth = max(1, iconSize.width() if isVertical else iconSize.height())
        iconHeight = max(1, iconSize.height() if isVertical else iconSize.width())

        maxColumns = max(1, maxWidth // iconWidth)

        x = 0
        y = 0
        firstSection = True
        for wi in self.m_sections:
            section = wi.widget()
            buttonCount = section.visibleButtonCount()
            if buttonCount == 0:
                # move out of view, not perfect TODO: better solution
                if notDryRun:
                    section.setGeometry(1000, 1000, 0, 0)
                continue

            # rows needed for the buttons (calculation gets the ceiling value of the plain div)
            neededRowCount = ((buttonCount - 1) // maxColumns) + 1

            if firstSection:
                firstSection = False
            else:
                # start on a new row, set separator
                x = 0
                y += iconHeight + self.spacing()
                if notDryRun:
                    separator = Section.SeparatorFlag.SeparatorTop if isVertical else Section.SeparatorFlag.SeparatorLeft
                    section.setSeparator(separator)

            if notDryRun:
                usedColumns = min(buttonCount, maxColumns)
                narrowSide = usedColumns * iconWidth
                longSide = neededRowCount * iconHeight
                if isVertical:
                    if self.parentWidget().isLeftToRight():
                        realX = x
                    else:
                        realX = rect.width() - x - narrowSide
                    section.setGeometry(realX, y, narrowSide, longSide)
                else:
                    if self.parentWidget().isLeftToRight():
                        realX = y
                    else:
                        realX = rect.width() - y - longSide
                    section.setGeometry(realX, x, longSide, narrowSide)

            # advance by the icons in the last row
            lastRowColumnCount = buttonCount - ((neededRowCount - 1) * maxColumns)
            x += (lastRowColumnCount * iconWidth) + self.spacing()
            # advance by all but the last used row
            y += (neededRowCount - 1) * iconHeight

        # cache total height (or width), adding the iconHeight for the current row
        return y + iconHeight
