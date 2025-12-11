from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from touchify.src.components.toolbox.ToolboxDocker import ToolboxDocker
    from touchify.src.components.toolbox.ToolboxWidget import ToolboxWidget

class ToolboxScrollArea(QScrollArea):
    def __init__(self, parent: "ToolboxDocker", toolbox: "ToolboxWidget"):
        super().__init__(parent)
        self._docker: "ToolboxDocker"  = parent
        self._toolbox: "ToolboxWidget" = toolbox

        self.m_orientation = Qt.Orientation.Vertical
        self.m_scrollPrev = QToolButton(self)
        self.m_scrollNext = QToolButton(self)

        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        

        self.m_scrollPrev.setAutoRepeat(True)
        self.m_scrollPrev.setAutoFillBackground(True)
        self.m_scrollPrev.setFocusPolicy(Qt.NoFocus)
        self.m_scrollPrev.clicked.connect(self.doScrollPrev)
        self.m_scrollNext.setAutoRepeat(True)
        self.m_scrollNext.setAutoFillBackground(True)
        self.m_scrollNext.setFocusPolicy(Qt.NoFocus)
        self.m_scrollNext.clicked.connect(self.doScrollNext)
        
        self.m_scrollPrev.installEventFilter(self)
        self.m_scrollNext.installEventFilter(self)

        scroller = QScroller.scroller(self.viewport())
        QScroller.grabGesture(self.viewport(), QScroller.MiddleMouseButtonGesture)
        sp = scroller.scrollerProperties()

        sp.setScrollMetric(QScrollerProperties.MaximumVelocity, 0.0)
        sp.setScrollMetric(QScrollerProperties.OvershootDragResistanceFactor, 0.1)
        sp.setScrollMetric(QScrollerProperties.OvershootDragDistanceFactor, 0.1)
        sp.setScrollMetric(QScrollerProperties.OvershootScrollDistanceFactor, 0.0)
        sp.setScrollMetric(QScrollerProperties.OvershootScrollTime, 0.4)

        scroller.setScrollerProperties(sp)
        scroller.stateChanged.connect(self.slotScrollerStateChange)
        self.setWidget(toolbox)

    def setOrientation(self, orientation):
        if orientation == self.m_orientation:
            return
        self.m_orientation = orientation
        self._toolbox.setOrientation(orientation)
        self.layoutItems()

    def orientation(self):
        return self.m_orientation

    def minimumSizeHint(self):
        margin = 0
        return self._toolbox.minimumSizeHint().grownBy(QMargins(margin,margin,margin,margin))

    def sizeHint(self):
        margin = 0
        return self._toolbox.sizeHint().grownBy(QMargins(margin,margin,margin,margin))

    def slotScrollerStateChange(self, state):
        pass

    def event(self, event):
        if event.type() == QEvent.Type.LayoutRequest:
            self.layoutItems()
            self.updateGeometry()
        return super().event(event)

    def eventFilter(self, watched, event):
        if (watched in [self.m_scrollPrev, self.m_scrollNext]) and event.type() == QEvent.Wheel:
            self.wheelEvent(event)
            return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        self.layoutItems()
        super().resizeEvent(event)
        self.updateScrollButtons()

    def wheelEvent(self, event):
        if self.m_orientation == Qt.Vertical:
            QApplication.sendEvent(self.verticalScrollBar(), event)
        else:
            QApplication.sendEvent(self.horizontalScrollBar(), event)

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.updateScrollButtons()

    def doScrollPrev(self):
        if self.m_orientation == Qt.Vertical:
            self.verticalScrollBar().triggerAction(QScrollBar.SliderSingleStepSub)
        else:
            self.horizontalScrollBar().triggerAction(QScrollBar.SliderSingleStepSub)

    def doScrollNext(self):
        if self.m_orientation == Qt.Vertical:
            self.verticalScrollBar().triggerAction(QScrollBar.SliderSingleStepAdd)
        else:
            self.horizontalScrollBar().triggerAction(QScrollBar.SliderSingleStepAdd)

    def scrollButtonWidth(self):
        opt = QStyleOption()
        opt.initFrom(self)
        return self.style().pixelMetric(QStyle.PM_TabBarScrollButtonWidth, opt, self)

    def layoutItems(self):
        self.updateScrollButtons()

    def updateScrollButtons(self):
        scrollButtonWidth = self.scrollButtonWidth()
        scrollbar = self.verticalScrollBar() if self.m_orientation == Qt.Vertical else self.horizontalScrollBar()
        canPrev = scrollbar.value() != scrollbar.minimum()
        canNext = scrollbar.value() != scrollbar.maximum()
        self.m_scrollPrev.setEnabled(canPrev)
        self.m_scrollNext.setEnabled(canNext)
        if self.m_orientation == Qt.Vertical:
            self.m_scrollPrev.setArrowType(Qt.UpArrow)
            self.m_scrollPrev.setGeometry(0 if canPrev else -self.width(), 0, self.width(), scrollButtonWidth)
            self.m_scrollNext.setArrowType(Qt.DownArrow)
            self.m_scrollNext.setGeometry(0 if canNext else -self.width(), self.height() - scrollButtonWidth, self.width(), scrollButtonWidth)
        elif self.isLeftToRight():
            self.m_scrollPrev.setArrowType(Qt.LeftArrow)
            self.m_scrollPrev.setGeometry(0, 0 if canPrev else -self.height(), scrollButtonWidth, self.height())
            self.m_scrollNext.setArrowType(Qt.RightArrow)
            self.m_scrollNext.setGeometry(self.width() - scrollButtonWidth, 0 if canNext else -self.height(), scrollButtonWidth, self.height())
        else:
            self.m_scrollPrev.setArrowType(Qt.RightArrow)
            self.m_scrollPrev.setGeometry(self.width() - scrollButtonWidth, 0 if canPrev else -self.height(), scrollButtonWidth, self.height())
            self.m_scrollNext.setArrowType(Qt.LeftArrow)
            self.m_scrollNext.setGeometry(0, 0 if canNext else -self.height(), scrollButtonWidth, self.height())

