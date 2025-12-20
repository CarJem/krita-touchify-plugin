from typing import TYPE_CHECKING
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.alib_widgets.containers.SideGripContainer import SideGripContainer
from jemlib.alib_widgets.painters.CheckerPainter import CheckerPainter
from jemlib.alib_vaporjem.extensions.pyqt_extensions import QPainterTools
from jemlib.managers.IconRepository import IconRepository

from touchify.src.components.sub_view.SubViewLoader import SubViewLoader
from touchify.src.components.sub_view.SubViewSettings import SubViewSettings
if TYPE_CHECKING:
    from touchify.src.components.sub_view.SubViewWidget import SubViewWidget


ITEM_SIZE = QSize(128,128)
ITEM_SPACING = 12
TOOLBAR_ITEM_SIZE = QSize(20,20)
TOOLBAR_HEIGHT = 32
SCROLLBAR_WIDTH = 16
IMAGE_PADDING = 4
INDICATOR_SIZE = 36
CHECKBOX_SCALE = 2.6

class SubViewTabList(SideGripContainer):
    sigImageSelectionChanged = pyqtSignal()

    def __init__(self, loader: SubViewLoader, widget: "SubViewWidget", parent: QWidget = None):
        super().__init__()

        self._widget = widget
        self._loader = loader
        self._loader.sigOnTabsChanged.connect(self.onTabsChanged)
        self._widgets: list[SubViewTabWidget] = []
        self._currentIndex: QModelIndex | None = None
        self._newFileImported = False
        self._preloading = True
        self._checkboxMode = False

        self.setContentsMargins(0,0,0,0)

        self.setMinimumWidth(ITEM_SIZE.width() + (ITEM_SPACING * 2) + SCROLLBAR_WIDTH)
        self.setMinimumHeight(ITEM_SIZE.height() + (ITEM_SPACING * 2) + TOOLBAR_HEIGHT)

        self.resize(self._loader.getImageListSize())

        self.resize_timer = QTimer(self)
        self.resize_timer.setInterval(200) # milliseconds delay
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.onResizeEnd)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.view = QListWidget(self)
        self.view.itemClicked.connect(self.onItemClicked)
        self.view.setResizeMode(QListView.ResizeMode.Adjust)
        self.view.setMovement(QListView.Movement.Static)
        self.view.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.view.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)
        self.view.setSpacing(ITEM_SPACING)
        self.view.setUniformItemSizes(True)
        self.view.setViewMode(QListWidget.ViewMode.IconMode)
        layout.addWidget(self.view, 0, 0)

        self.toolbar = QToolBar(self)
        self.toolbar.setAutoFillBackground(True)
        self.toolbar.setFixedHeight(TOOLBAR_HEIGHT)
        self.toolbar.setIconSize(TOOLBAR_ITEM_SIZE)
        layout.addWidget(self.toolbar, 1, 0)

        self.showHideSettingCheckboxesAction = QAction(IconRepository.iconLoader("material:checkbox-multiple-outline"), "Show/hide setting checkboxes", self)
        self.showHideSettingCheckboxesAction.setCheckable(True)
        self.showHideSettingCheckboxesAction.toggled.connect(self.onCheckboxModeUpdated)
        self.toolbar.addAction(self.showHideSettingCheckboxesAction)

        self.selectAllAction = QAction(IconRepository.iconLoader("material:select-all"), "Select all", self)
        self.selectAllAction.triggered.connect(self.selectAll)
        self.toolbar.addAction(self.selectAllAction)

        self.importAction = QAction(IconRepository.iconLoader("material:folder-multiple-plus-outline"), "Import", self)
        self.importAction.triggered.connect(self.importImages)
        self.toolbar.addAction(self.importAction)

        self.clearAction = QAction(IconRepository.iconLoader("material:trash-can-outline"), "Clear", self)
        self.clearAction.triggered.connect(self.clear)
        self.toolbar.addAction(self.clearAction)

        qApp.paletteChanged.connect(self.onPaletteChanged)
        self.onPaletteChanged()

    #region Events

    def focusOutEvent(self, a0):
        super().focusOutEvent(a0)
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_timer.start()

    #endregion

    #region Signal Recievers

    def onPaletteChanged(self):
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, qApp.palette().base())
        self.setPalette(palette)

        toolbarPalette = self.toolbar.palette()
        toolbarPalette.setBrush(QPalette.ColorRole.Base, qApp.palette().window())
        self.toolbar.setPalette(toolbarPalette)

    def onItemClicked(self, item: QListWidgetItem):
        if self._checkboxMode == False:
            item: "SubViewTabItem" = item
            self.setCurrentItem(item)

    def onTabsChanged(self):
        self.view.clear()

        for widg in self._widgets:
            widg.close()

        self._widgets.clear()
        self._widgets = []

        images = self._loader.getTabList()
        for idx, img in enumerate(images):
            img: SubViewSettings.Tab

            widgetItem = SubViewTabWidget(img, self.view)
            widgetItem.setCheckable(self._checkboxMode)
            self._widgets.append(widgetItem)

            item = widgetItem.getItem()
            self.view.addItem(item)
            self.view.setItemWidget(item, widgetItem)

            if self._preloading and idx == self._loader.getLastIndex():
                self.setCurrentItem(item)

        if not self.currentItem():
            if self.view.count() > 0:
                self.setCurrentItem(self._widgets[-1].getItem())

        self._preloading = False

    def onResizeEnd(self):
        self._loader.setImageListSize(self.size())
        
    def onCheckboxModeUpdated(self, state: bool):
        self._checkboxMode = state
        if self._checkboxMode: self.view.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        else: self.view.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        for item in self._widgets:
            item.setCheckable(state)

    #endregion

    
    #region Get / Set Functions

    def setCurrentItem(self, item: "SubViewTabItem"):
        try:
            self._currentIndex = item.listWidget().indexFromItem(item)
        except:
            self._currentIndex = None

        if self._currentIndex: self._loader.setLastIndex(self._currentIndex.row())
        
        self._widget.onTabImageSelectionChanged()

    def getAllowBackwardsNavigation(self):
        if not self._currentIndex:
            return False
        elif self.currentItem().getAncestor() == None:
            return False
        else:
            return True

    def getAllowForwardsNavigation(self):
        if not self._currentIndex:
            return False
        elif self.currentItem().getDescendant() == None:
            return False
        else:
            return True

    #endregion

    #region Properties

    def currentData(self) -> "SubViewSettings.Tab":
        try:
            return self._widgets[self._currentIndex.row()].getData()
        except:
            return None

    def currentItem(self) -> "SubViewTabItem":
        try:
            return self.view.itemFromIndex(self._currentIndex)
        except:
            return None
        
    def selectedData(self) -> list["SubViewSettings.Tab"]:
        indexes = self.view.selectedIndexes()
        return [self._widgets[index.row()].getData() for index in indexes]
    
    #endregion

    #region Actions

    def refresh(self):
        self.onTabsChanged()

    def clear(self):
        self._loader.removeFromTabList(self.selectedData())
        self._currentIndex = None
        self.refresh()

    def clearActive(self):
        if not self.currentData():
            return
        
        self._loader.removeFromTabList([self.currentData()])
        self._currentIndex = None
        self.refresh()
    
    def selectAll(self):
        self.view.selectAll()

    def toPreviousImage(self):
        item = self.currentItem()
        if not item: return
        previous = item.getAncestor()
        if not previous: return
        self.setCurrentItem(previous)

    def toNextImage(self):
        item = self.currentItem()
        if not item: return
        next = item.getDescendant()
        if not next: return
        self.setCurrentItem(next)

    def importImages(self):
        self._loader.importImages()
    
    #endregion

class SubViewTabItem(QListWidgetItem):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setSizeHint(ITEM_SIZE)

    def getAncestor(self):
        lw = self.listWidget()
        model = lw.model()
        current_index = lw.indexFromItem(self)
        next_row_index = current_index.row() -1
        return lw.itemFromIndex(model.index(next_row_index, current_index.column()))
        
    def getDescendant(self):
        lw = self.listWidget()
        model = lw.model()
        current_index = lw.indexFromItem(self)
        next_row_index = current_index.row() + 1
        return lw.itemFromIndex(model.index(next_row_index, current_index.column()))

class SubViewTabWidget(QWidget):
    def __init__(self, data: SubViewSettings.Tab, list: QListWidget, parent: QWidget = None):
        super().__init__(parent)
        self._data = data
        self._view = list
        self._item = SubViewTabItem()
        self._checkerPainter = CheckerPainter(4)
        self._hasCheckboxes = False
        self.setFixedSize(ITEM_SIZE)

    #region Get / Set Functions

    def getData(self):
        return self._data
        
    def getItem(self):
        return self._item

    def getIndex(self):
        index = 0
        try:
            indexModel = self._view.indexFromItem(self._item)
            index = (self._view.modelColumn() * indexModel.row()) + indexModel.row()
        except:
            pass
        return index
    
    def getBackgroundColor(self):
        normal_color = qApp.palette().base()
        selected_color = qApp.palette().highlight()
        hover_color = QBrush(QPainterTools.blendColors(QPainterTools.setAlpha(selected_color.color(), 128), normal_color.color()))
        selected_hover_color = QBrush(QPainterTools.blendColors(QPainterTools.setAlpha(selected_color.color(), 192), QColor(Qt.GlobalColor.white)))

        if self.isSelected():
            if self.isHovered(): return selected_hover_color
            else: return selected_color
        else:
            if self.isHovered(): return hover_color
            else: return normal_color
    
    def setCheckable(self, val: bool):
        self._hasCheckboxes = val
        self.update()

    #endregion

    #region States

    def isSelected(self):
        if not self._item: return False
        
        return self._item in self._view.selectedItems()

    def isHovered(self):
        return self.underMouse()

    #endregion

    #region Events

    def paintImageEvent(self, targetRect: QRect, painter: QPainter):
        painter.setBrush(Qt.GlobalColor.black)
        painter.setPen(Qt.PenStyle.NoPen)

        pixmap = None
        image = self._data.getImageData()
        if image and not image.isNull():
            pixmap = QPixmap.fromImage(image)

        # Optional: Draw the outline of the target square to visualize the bounds
        self._checkerPainter.paint(painter, QRectF(targetRect))

        if pixmap and not pixmap.isNull():
            # 1. Calculate the scaled size using KeepAspectRatioByExpanding
            # This size will completely cover the targetRect, potentially being larger
            scaledSize = pixmap.size().scaled(targetRect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)

            # 2. Calculate the source rectangle in the original pixmap to clip to the center
            # We need to find the top-left corner (sx, sy) in the original pixmap
            # that, when scaled, aligns with the center of the target area.

            # Calculate the size difference
            # The scaled image will be centered, so we need to find the offset in the *original*
            # pixmap's coordinates.
            sourceWidth = int(targetRect.width() * (pixmap.width() / scaledSize.width()))
            sourceHeight = int(targetRect.height() * (pixmap.height() / scaledSize.height()))
            
            # Calculate the starting point (top-left) in the original pixmap to center the clip
            sourceX = (pixmap.width() - sourceWidth) // 2
            sourceY = (pixmap.height() - sourceHeight) // 2
            
            sourceRect = QRect(sourceX, sourceY, sourceWidth, sourceHeight)

            # 3. Use drawPixmap(targetRect, pixmap, sourceRect)
            # This draws the 'sourceRect' portion of 'pixmap' into the 'targetRect' area
            painter.drawPixmap(targetRect, pixmap, sourceRect)

            # Optional: Enable smooth scaling for better quality
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)


    def paintEvent(self, event: QPaintEvent):
        painter = QStylePainter(self)
            
        BRUSH_BACKGROUND = self.getBackgroundColor()
        BRUSH_TEXT = QBrush(Qt.GlobalColor.transparent)
        PEN_TEXT = QPen(Qt.GlobalColor.white)
        FONT_TEXT = QFont(qApp.font().family(), int(INDICATOR_SIZE / 4))

        DRAW_AREA = self.rect()
        IMAGE_DRAW_AREA = DRAW_AREA.marginsRemoved(QMargins(IMAGE_PADDING, IMAGE_PADDING, IMAGE_PADDING, IMAGE_PADDING))
        INDICATOR_RECT = QRectF(0, 0, INDICATOR_SIZE, INDICATOR_SIZE)
        TEXT_AREA = INDICATOR_RECT.marginsRemoved(QMarginsF(IMAGE_PADDING, IMAGE_PADDING, int(INDICATOR_SIZE / 4) - int(IMAGE_PADDING / 2), int(INDICATOR_SIZE / 4)  - int(IMAGE_PADDING / 2)))

        painter.setBrush(BRUSH_BACKGROUND)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(DRAW_AREA)

        self.paintImageEvent(IMAGE_DRAW_AREA, painter)

        painter.setBrush(BRUSH_BACKGROUND)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(INDICATOR_RECT, int(INDICATOR_SIZE / 2), int(INDICATOR_SIZE / 2))
        painter.drawRect(0, 0, INDICATOR_SIZE, int(INDICATOR_SIZE / 2))
        painter.drawRect(0, 0, int(INDICATOR_SIZE / 2), INDICATOR_SIZE)

        if self._hasCheckboxes == True:
            opts = QStyleOptionButton()
            check_indicator_rect = self.style().subElementRect(
                QStyle.SubElement.SE_ItemViewItemCheckIndicator, opts
            )

            checkbox_width = self.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth)
            checkbox_height = self.style().pixelMetric(QStyle.PixelMetric.PM_IndicatorHeight)

            # Calculate the centered rectangle within the full cell rectangle (opt.rect)
            centered_rect = QStyle.alignedRect(opts.direction, Qt.AlignmentFlag.AlignCenter, check_indicator_rect.size(), opts.rect)

            centered_rect.moveTo(centered_rect.topLeft() + QPoint(int(checkbox_width / 2), int(checkbox_height / 2)))

            opts.rect = centered_rect
            opts.state |= QStyle.StateFlag.State_Enabled
            if self.isSelected(): opts.state |= QStyle.StateFlag.State_On
            else: opts.state |= QStyle.StateFlag.State_Off
            painter.scale(CHECKBOX_SCALE, CHECKBOX_SCALE)
            painter.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorItemViewItemCheck, opts)
        else:
            painter.setBrush(BRUSH_TEXT)
            painter.setPen(PEN_TEXT)
            painter.setFont(FONT_TEXT)
            painter.drawText(TEXT_AREA, Qt.AlignmentFlag.AlignCenter, f"{self.getIndex():02}")

        painter.end()


        

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.update()
    
    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.update()

    #endregion


        

        