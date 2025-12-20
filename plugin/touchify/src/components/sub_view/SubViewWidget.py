from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.src.alib_widgets.sliders.QDoubleSlider import QDoubleSlider
from touchify.src.components.sub_view.SubViewLoader import SubViewLoader
from touchify.src.components.sub_view.SubViewTabList import SubViewTabList
from touchify.src.components.sub_view.SubViewViewport import SubViewViewport

from touchify.src.alib_kis.widgets.KisAngleSelector import KisAngleSelector
from touchify.src.alib_vaporjem.extensions.pyqt_extensions import GeometryHelpers
from touchify.src.managers.ResourceManager import ResourceManager


class SubViewWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__toolbar_icon_size = QSize(20,20)

        self.__viewerActions = []
        self.__isUpdatingValues = False

        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(300)

        layout = QGridLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.loader = SubViewLoader(self)
        self.view = SubViewViewport(self)
        self.tabs = SubViewTabList(self.loader, self)

        self.view.sigViewerStateChanged.connect(self.onViewerStateChanged)
        self.view.sigViewerRequestedSave.connect(self.onViewerRequestedSave)

        layout.addWidget(self.view, 0, 0)
        
        self.toolbarAlpha = QToolBar(self)
        self.toolbarAlpha.setIconSize(self.__toolbar_icon_size)
        layout.addWidget(self.toolbarAlpha, 1, 0)

        self.toolbarBeta = QToolBar(self)
        self.toolbarBeta.setIconSize(self.__toolbar_icon_size)
        layout.addWidget(self.toolbarBeta, 2, 0)

        self.toolbarGamma = QToolBar(self)
        self.toolbarGamma.setIconSize(self.__toolbar_icon_size)
        layout.addWidget(self.toolbarGamma, 3, 0)

        self.zoomSlider = QDoubleSlider(Qt.Orientation.Horizontal, self)
        self.zoomSlider.decimals = 1
        self.zoomSlider.setValue(100)
        self.zoomSlider.setMinimum(0.8)
        self.zoomSlider.setMaximum(3200.0)
        self.zoomSlider.valueChanged.connect(self.onZoomChanged)
        self.toolbarAlpha.addWidget(self.__createSpacer(self.zoomSlider))
        self.__viewerActions.append(self.zoomSlider)

        self.zoomValue = QToolButton(self)
        self.zoomValue.clicked.connect(self.zoomValue.showMenu)
        self.zoomValue.setMenu(QMenu(self))
        self.zoomValue.setFixedSize(self.__toolbar_icon_size.width() * 4, self.__toolbar_icon_size.height())
        self.toolbarAlpha.addWidget(self.zoomValue)
        self.__viewerActions.append(self.zoomValue)
        for item in self.view.zoomIncrements:
            self.zoomValue.menu().addAction(item[1], self.onZoomSelectionChanged).setData(item[0])
        
        self.zoomOutButton = QAction(ResourceManager.iconLoader("material:minus-circle-outline"), "Zoom Out", self)
        self.zoomOutButton.triggered.connect(self.zoomOut)
        self.toolbarAlpha.addAction(self.zoomOutButton)
        self.__viewerActions.append(self.zoomOutButton)
        
        self.zoomInButton = QAction(ResourceManager.iconLoader("material:plus-circle-outline"), "Zoom In", self)
        self.zoomInButton.triggered.connect(self.zoomIn)
        self.toolbarAlpha.addAction(self.zoomInButton)
        self.__viewerActions.append(self.zoomInButton)

        self.fitToNavigatorButton = QAction(ResourceManager.iconLoader("zoom-fit-best"), "Fit to Navigator", self)
        self.fitToNavigatorButton.triggered.connect(self.fitToNavigator)
        self.toolbarAlpha.addAction(self.fitToNavigatorButton)
        self.__viewerActions.append(self.fitToNavigatorButton)

        self.rotationSlider = KisAngleSelector(self)
        self.rotationSlider.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.ContextMenu)
        self.rotationSlider.angleChanged.connect(self.onAngleChanged)
        self.toolbarBeta.addWidget(self.__createSpacer(self.rotationSlider))
        self.__viewerActions.append(self.rotationSlider)

        self.rotateLeftBtn = QAction(ResourceManager.iconLoader("material:rotate-left"), "Rotate Left", self)
        self.rotateLeftBtn.triggered.connect(self.rotateLeft)
        self.toolbarBeta.addAction(self.rotateLeftBtn)
        self.__viewerActions.append(self.rotateLeftBtn)

        self.rotateRightBtn = QAction(ResourceManager.iconLoader("material:rotate-right"), "Rotate Right", self)
        self.rotateRightBtn.triggered.connect(self.rotateRight)
        self.toolbarBeta.addAction(self.rotateRightBtn)
        self.__viewerActions.append(self.rotateRightBtn)

        self.resetRotationBtn = QAction(ResourceManager.iconLoader("rotation-reset"), "Reset Rotation", self)
        self.resetRotationBtn.triggered.connect(self.resetRotation)
        self.toolbarBeta.addAction(self.resetRotationBtn)
        self.__viewerActions.append(self.resetRotationBtn)

        self.flipHorizontalBtn = QAction(ResourceManager.iconLoader("material:flip-horizontal"), "Flip Horizontal", self)
        self.flipHorizontalBtn.setCheckable(True)
        self.flipHorizontalBtn.toggled.connect(self.flipHorizontal)
        self.toolbarBeta.addAction(self.flipHorizontalBtn)
        self.__viewerActions.append(self.flipHorizontalBtn)

        self.flipVerticalBtn = QAction(ResourceManager.iconLoader("material:flip-vertical"), "Flip Vertical", self)
        self.flipVerticalBtn.setCheckable(True)
        self.flipVerticalBtn.toggled.connect(self.flipVertical)
        self.toolbarBeta.addAction(self.flipVerticalBtn)
        self.__viewerActions.append(self.flipVerticalBtn)

        self.eyedropperBtn = QAction(ResourceManager.iconLoader("material:eyedropper"), "Switch to eyedropper automatically", self)
        self.eyedropperBtn.setCheckable(True)
        self.eyedropperBtn.toggled.connect(self.toggleColorPicker)
        self.toolbarGamma.addAction(self.eyedropperBtn)
        self.__viewerActions.append(self.eyedropperBtn)

        self.toolbarGamma.addWidget(self.__createSpacer())

        self.previousImageBtn = QAction(ResourceManager.iconLoader("material:arrow-left"), "To previous image", self)
        self.previousImageBtn.triggered.connect(self.toPreviousImage)
        self.toolbarGamma.addAction(self.previousImageBtn)
        self.__viewerActions.append(self.previousImageBtn)

        self.nextImageBtn = QAction(ResourceManager.iconLoader("material:arrow-right"), "To next image", self)
        self.nextImageBtn.triggered.connect(self.toNextImage)
        self.toolbarGamma.addAction(self.nextImageBtn)
        self.__viewerActions.append(self.nextImageBtn)

        self.imageListBtn = QAction(ResourceManager.iconLoader("material:view-grid"), "Image list", self)
        self.imageListBtn.triggered.connect(self.showImageList)
        self.toolbarGamma.addAction(self.imageListBtn)
        self.__viewerActions.append(self.imageListBtn)

        self.importImageBtn = QAction(ResourceManager.iconLoader("material:folder-multiple-plus-outline"), "Import", self)
        self.importImageBtn.triggered.connect(self.importImages)
        self.toolbarGamma.addAction(self.importImageBtn)
        self.__viewerActions.append(self.importImageBtn)

        self.openImageOnCanvasBtn = QAction(ResourceManager.iconLoader("material:file-import"), "Open image on canvas", self)
        self.openImageOnCanvasBtn.triggered.connect(self.openImageInCanvas)
        self.toolbarGamma.addAction(self.openImageOnCanvasBtn)
        self.__viewerActions.append(self.openImageOnCanvasBtn)

        self.clearImageBtn = QAction(ResourceManager.iconLoader("material:trash-can-outline"), "Clear", self)
        self.clearImageBtn.triggered.connect(self.clearImage)
        self.toolbarGamma.addAction(self.clearImageBtn)
        self.__viewerActions.append(self.clearImageBtn)


        self.tabs.refresh()

    #region Signals

    def onZoomSelectionChanged(self):
        if self.__isUpdatingValues: return
        ac: QAction = self.sender()
        value: float = ac.data()
        self.zoomSlider.setValue(value)

    def onZoomChanged(self):
        if self.__isUpdatingValues: return
        self.zoomValue.setText(f"{self.zoomSlider.value():.1f}%")
        self.view.setZoom(self.zoomSlider.value())

    def onAngleChanged(self, val: float):
        if self.__isUpdatingValues: return
        self.view.setRotation(self.rotationSlider.angle())

    def onViewerStateChanged(self):
        self.__isUpdatingValues = True

        is_image_loaded = self.view.getImageLoaded()

        self.zoomInButton.setEnabled(is_image_loaded)
        self.zoomOutButton.setEnabled(is_image_loaded)
        self.zoomSlider.setEnabled(is_image_loaded)
        self.rotationSlider.setEnabled(is_image_loaded)
        self.rotateLeftBtn.setEnabled(is_image_loaded)
        self.rotateRightBtn.setEnabled(is_image_loaded)
        self.resetRotationBtn.setEnabled(is_image_loaded)
        self.flipHorizontalBtn.setEnabled(is_image_loaded)
        self.flipVerticalBtn.setEnabled(is_image_loaded)
        self.eyedropperBtn.setEnabled(is_image_loaded)
        self.fitToNavigatorButton.setEnabled(is_image_loaded)
        self.openImageOnCanvasBtn.setEnabled(is_image_loaded)
        self.clearImageBtn.setEnabled(is_image_loaded)

        self.previousImageBtn.setEnabled(is_image_loaded and self.tabs.getAllowBackwardsNavigation())
        self.nextImageBtn.setEnabled(is_image_loaded and self.tabs.getAllowForwardsNavigation())

        self.zoomSlider.setValue(self.view.getZoom())
        self.zoomValue.setText(f"{self.view.getZoom():.1f}%")
        self.rotationSlider.setAngle(self.view.getRotation())
        self.flipHorizontalBtn.setChecked(self.view.getFlipHorizontal())
        self.flipVerticalBtn.setChecked(self.view.getFlipVertical())
        self.eyedropperBtn.setChecked(self.view.getSamplingColors())
        
        self.__isUpdatingValues = False

    def onTabImageSelectionChanged(self):
        item = self.tabs.currentData()
        if not item: self.view.setImage()
        else: self.view.setImage(item)
        
    def onViewerRequestedSave(self):
        if self.isVisible(): 
            state = self.view.saveState()
            if state: self.loader.saveTabState(state)

    #endregion

    #region Misc
    
    def __createSpacer(self, widget: QWidget = None):
        spacer = QWidget()
        spacer.setLayout(QHBoxLayout())
        spacer.layout().setSpacing(0)
        spacer.layout().setContentsMargins(0,0,0,0)

        if widget: spacer.layout().addWidget(widget, 1)
        else: spacer.layout().addStretch()

        return spacer
        

    #endregion

    #region Actions

    def zoomIn(self):
        self.view.zoomIn()

    def zoomOut(self):
        self.view.zoomOut()

    def fitToNavigator(self):
        self.view.fitToNavigator()

    def rotateLeft(self):
        currentValue = self.rotationSlider.angle()
        self.rotationSlider.setAngle(currentValue - 5.0)

    def rotateRight(self):
        currentValue = self.rotationSlider.angle()
        self.rotationSlider.setAngle(currentValue + 5.0)

    def resetRotation(self):
        self.rotationSlider.setAngle(0.0)

    def flipHorizontal(self, state: bool):
        self.view.setFlipHorizontal(state)

    def flipVertical(self, state: bool):
        self.view.setFlipVertical(state)

    def toggleColorPicker(self, state: bool):
        self.view.setSamplingColors(state)

    def toPreviousImage(self):
        self.tabs.toPreviousImage()

    def toNextImage(self):
        self.tabs.toNextImage()

    def showImageList(self):
        self.tabs.setContentsMargins(0,0,0,0)
        self.tabs.setWindowFlags(Qt.WindowType.Popup)
        
        button_src = self.toolbarGamma.widgetForAction(self.imageListBtn)
        position = button_src.mapToGlobal(button_src.rect().topRight()) - QPoint(self.tabs.width(), self.tabs.height())
        position = GeometryHelpers.clampToTarget(position, self.tabs.size(), self.window())

        self.tabs.move(position)
        self.tabs.show()

    def importImages(self):
        self.tabs.importImages()

    def openImageInCanvas(self, mode: str = "default"):
        current_data = self.tabs.currentData()
        if not current_data:
            return
        
        image_path = current_data.filepath
        if image_path in ( "", None ):
            return
        
        self.loader.insertImage(image_path)


    def clearImage(self):
        self.tabs.clearActive()

    #endregion