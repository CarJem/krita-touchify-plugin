from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from jemlib.alib_widgets.sliders.QDoubleSlider import QDoubleSlider
from touchify_sub_view.SubViewLoader import SubViewLoader
from touchify_sub_view.SubViewTabList import SubViewTabList
from touchify_sub_view.SubViewViewport import SubViewViewport

from jemlib.alib_kis.widgets.KisAngleSelector import KisAngleSelector
from jemlib.alib_vaporjem.extensions.pyqt_extensions import GeometryHelpers
from jemlib.managers.IconRepository import IconRepository


class SubViewWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.__toolbar_icon_size = QSize(20,20)
        self.__menu_icon_size = QSize(18,18)

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

        self.menuBar = QToolBar(self)
        self.menuBar.setMaximumHeight(self.__menu_icon_size.height())
        self.menuBar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        self.menuBar.setContentsMargins(0,0,0,0)
        layout.addWidget(self.menuBar, 0, 0)
    
        layout.addWidget(self.view, 1, 0)
        
        self.zoomToolbar = QToolBar(self)
        self.zoomToolbar.setIconSize(self.__toolbar_icon_size)
        self.zoomToolbar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        layout.addWidget(self.zoomToolbar, 2, 0)

        self.rotationToolbar = QToolBar(self)
        self.rotationToolbar.setIconSize(self.__toolbar_icon_size)
        self.rotationToolbar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        layout.addWidget(self.rotationToolbar, 3, 0)

        self.navigationToolbar = QToolBar(self)
        self.navigationToolbar.setIconSize(self.__toolbar_icon_size)
        self.navigationToolbar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        layout.addWidget(self.navigationToolbar, 4, 0)

        self.options_menu = QMenu(self)
        self.options_menu_button = QToolButton(self)
        self.options_menu_button.setMaximumSize(self.__menu_icon_size)
        self.options_menu_button.setContentsMargins(0,0,0,0)
        self.options_menu_button.setPopupMode(QToolButton.InstantPopup)
        self.options_menu_button.setStyleSheet("QToolButton::menu-indicator { image: none }")
        self.options_menu_button.setAutoRaise(True)
        self.options_menu_button.setMenu(self.options_menu)
        self.options_menu_button.setIcon(IconRepository.materialIcon("menu"))
        self.menuBar.addWidget(self.options_menu_button)



        self.file_label = QLabel(self)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setContentsMargins(0,0,0,0)
        self.menuBar.addWidget(self.__createSpacer(self.file_label))

        self.fullscreenModeBtn = self.options_menu.addAction("Fullscreen Mode")
        self.fullscreenModeBtn.setCheckable(True)
        self.fullscreenModeBtn.setChecked(self.loader.getPrefs().fullscreenMode)
        self.fullscreenModeBtn.toggled.connect(self.onFullscreenToggled)

        self.options_menu.addSeparator()

        self.showRotationBarBtn = self.options_menu.addAction("Show Rotation Toolbar")
        self.showRotationBarBtn.setCheckable(True)
        self.showRotationBarBtn.setChecked(self.loader.getPrefs().showRotationBar)
        self.showRotationBarBtn.toggled.connect(self.onRotationBarToggled)

        self.showZoomBarBtn = self.options_menu.addAction("Show Zoom Toolbar")
        self.showZoomBarBtn.setCheckable(True)
        self.showZoomBarBtn.setChecked(self.loader.getPrefs().showZoomBar)
        self.showZoomBarBtn.toggled.connect(self.onZoomBarToggled)

        self.showNavigatorBarBtn = self.options_menu.addAction("Show Navigator Toolbar")
        self.showNavigatorBarBtn.setCheckable(True)
        self.showNavigatorBarBtn.setChecked(self.loader.getPrefs().showNavigationBar)
        self.showNavigatorBarBtn.toggled.connect(self.onNavigationBarToggled)

        self.zoomSlider = QDoubleSlider(Qt.Orientation.Horizontal, self)
        self.zoomSlider.decimals = 1
        self.zoomSlider.setValue(100)
        self.zoomSlider.setMinimum(0.8)
        self.zoomSlider.setMaximum(3200.0)
        self.zoomSlider.valueChanged.connect(self.onZoomChanged)
        self.zoomToolbar.addWidget(self.__createSpacer(self.zoomSlider))
        self.__viewerActions.append(self.zoomSlider)

        self.zoomValue = QToolButton(self)
        self.zoomValue.clicked.connect(self.zoomValue.showMenu)
        self.zoomValue.setMenu(QMenu(self))
        self.zoomValue.setFixedSize(self.__toolbar_icon_size.width() * 4, self.__toolbar_icon_size.height())
        self.zoomToolbar.addWidget(self.zoomValue)
        self.__viewerActions.append(self.zoomValue)
        for item in self.view.zoomIncrements:
            self.zoomValue.menu().addAction(item[1], self.onZoomSelectionChanged).setData(item[0])
        
        self.zoomOutButton = QAction(IconRepository.iconLoader("material:minus-circle-outline"), "Zoom Out", self)
        self.zoomOutButton.triggered.connect(self.zoomOut)
        self.zoomToolbar.addAction(self.zoomOutButton)
        self.__viewerActions.append(self.zoomOutButton)
        
        self.zoomInButton = QAction(IconRepository.iconLoader("material:plus-circle-outline"), "Zoom In", self)
        self.zoomInButton.triggered.connect(self.zoomIn)
        self.zoomToolbar.addAction(self.zoomInButton)
        self.__viewerActions.append(self.zoomInButton)

        self.fitToNavigatorButton = QAction(IconRepository.iconLoader("zoom-fit-best"), "Fit to Navigator", self)
        self.fitToNavigatorButton.triggered.connect(self.fitToNavigator)
        self.zoomToolbar.addAction(self.fitToNavigatorButton)
        self.__viewerActions.append(self.fitToNavigatorButton)

        self.rotationSlider = KisAngleSelector(self)
        self.rotationSlider.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.ContextMenu)
        self.rotationSlider.angleChanged.connect(self.onAngleChanged)
        self.rotationToolbar.addWidget(self.__createSpacer(self.rotationSlider))
        self.__viewerActions.append(self.rotationSlider)

        self.rotateLeftBtn = QAction(IconRepository.iconLoader("material:rotate-left"), "Rotate Left", self)
        self.rotateLeftBtn.triggered.connect(self.rotateLeft)
        self.rotationToolbar.addAction(self.rotateLeftBtn)
        self.__viewerActions.append(self.rotateLeftBtn)

        self.rotateRightBtn = QAction(IconRepository.iconLoader("material:rotate-right"), "Rotate Right", self)
        self.rotateRightBtn.triggered.connect(self.rotateRight)
        self.rotationToolbar.addAction(self.rotateRightBtn)
        self.__viewerActions.append(self.rotateRightBtn)

        self.resetRotationBtn = QAction(IconRepository.iconLoader("rotation-reset"), "Reset Rotation", self)
        self.resetRotationBtn.triggered.connect(self.resetRotation)
        self.rotationToolbar.addAction(self.resetRotationBtn)
        self.__viewerActions.append(self.resetRotationBtn)

        self.flipHorizontalBtn = QAction(IconRepository.iconLoader("material:flip-horizontal"), "Flip Horizontal", self)
        self.flipHorizontalBtn.setCheckable(True)
        self.flipHorizontalBtn.toggled.connect(self.flipHorizontal)
        self.rotationToolbar.addAction(self.flipHorizontalBtn)
        self.__viewerActions.append(self.flipHorizontalBtn)

        self.flipVerticalBtn = QAction(IconRepository.iconLoader("material:flip-vertical"), "Flip Vertical", self)
        self.flipVerticalBtn.setCheckable(True)
        self.flipVerticalBtn.toggled.connect(self.flipVertical)
        self.rotationToolbar.addAction(self.flipVerticalBtn)
        self.__viewerActions.append(self.flipVerticalBtn)

        self.eyedropperBtn = QAction(IconRepository.iconLoader("material:eyedropper"), "Switch to eyedropper automatically", self)
        self.eyedropperBtn.setCheckable(True)
        self.eyedropperBtn.toggled.connect(self.toggleColorPicker)
        self.navigationToolbar.addAction(self.eyedropperBtn)
        self.__viewerActions.append(self.eyedropperBtn)

        self.navigationToolbar.addWidget(self.__createSpacer())

        self.previousImageBtn = QAction(IconRepository.iconLoader("material:arrow-left"), "To previous image", self)
        self.previousImageBtn.triggered.connect(self.toPreviousImage)
        self.navigationToolbar.addAction(self.previousImageBtn)
        self.__viewerActions.append(self.previousImageBtn)

        self.nextImageBtn = QAction(IconRepository.iconLoader("material:arrow-right"), "To next image", self)
        self.nextImageBtn.triggered.connect(self.toNextImage)
        self.navigationToolbar.addAction(self.nextImageBtn)
        self.__viewerActions.append(self.nextImageBtn)

        self.imageListBtn = QAction(IconRepository.iconLoader("material:view-grid"), "Image list", self)
        self.imageListBtn.triggered.connect(self.showImageList)
        self.navigationToolbar.addAction(self.imageListBtn)
        self.__viewerActions.append(self.imageListBtn)

        self.importImageBtn = QAction(IconRepository.iconLoader("material:folder-multiple-plus-outline"), "Import", self)
        self.importImageBtn.triggered.connect(self.importImages)
        self.navigationToolbar.addAction(self.importImageBtn)
        self.__viewerActions.append(self.importImageBtn)

        self.openImageOnCanvasBtn = QAction(IconRepository.iconLoader("material:file-import"), "Open image on canvas", self)
        self.openImageOnCanvasBtn.triggered.connect(self.openImageInCanvas)
        self.navigationToolbar.addAction(self.openImageOnCanvasBtn)
        self.__viewerActions.append(self.openImageOnCanvasBtn)

        self.clearImageBtn = QAction(IconRepository.iconLoader("material:trash-can-outline"), "Clear", self)
        self.clearImageBtn.triggered.connect(self.clearImage)
        self.navigationToolbar.addAction(self.clearImageBtn)
        self.__viewerActions.append(self.clearImageBtn)

        qApp.paletteChanged.connect(self.onPaletteChanged)
        self.tabs.refresh()
        self.onPaletteChanged()

    #region Signals

    def onPaletteChanged(self):
        self.file_label.setStyleSheet("QLabel { background-color: palette(base) }")
        self.file_label.setAutoFillBackground(True)

        self.menuBar.setStyleSheet(f"""
            QToolBar {{ 
                margin: 0px; 
                padding: 0px; 
                background-color: palette(base);
            }}
            QToolBar::item {{ 
                margin: 0px; 
                padding: 0px; 
                background-color: palette(base);
            }}
        """)
        self.view.setBackgroundColor(qApp.palette().window().color())

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
        show_zoom_bar = self.showZoomBarBtn.isChecked() and not self.fullscreenModeBtn.isChecked()
        show_rotation_bar = self.showRotationBarBtn.isChecked() and not self.fullscreenModeBtn.isChecked()
        show_navigation_bar = self.showNavigatorBarBtn.isChecked() and not self.fullscreenModeBtn.isChecked()

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
        
        if self.zoomToolbar.isVisible() != show_zoom_bar: self.zoomToolbar.setVisible(show_zoom_bar)
        if self.rotationToolbar.isVisible() != show_rotation_bar: self.rotationToolbar.setVisible(show_rotation_bar)
        if self.navigationToolbar.isVisible() != show_navigation_bar: self.navigationToolbar.setVisible(show_navigation_bar)
        self.showZoomBarBtn.setEnabled(not self.fullscreenModeBtn.isChecked())
        self.showRotationBarBtn.setEnabled(not self.fullscreenModeBtn.isChecked())
        self.showNavigatorBarBtn.setEnabled(not self.fullscreenModeBtn.isChecked())

        self.file_label.setText("" if not is_image_loaded else self.tabs.currentData().getName())
            
        
        self.__isUpdatingValues = False

    def onTabImageSelectionChanged(self):
        item = self.tabs.currentData()
        if not item: self.view.setImage()
        else: self.view.setImage(item)
        
    def onViewerRequestedSave(self):
        if self.isVisible(): 
            state = self.view.saveState()
            if state: self.loader.saveTabState(state)

    def onFullscreenToggled(self, state: bool):
        if self.loader.getPrefs().fullscreenMode != state:
            self.loader.getPrefs().fullscreenMode = state
            self.loader.save(True)
            self.onViewerStateChanged()

    def onZoomBarToggled(self, state: bool):
        if self.loader.getPrefs().showZoomBar != state:
            self.loader.getPrefs().showZoomBar = state
            self.loader.save(True)
            self.onViewerStateChanged()

    def onRotationBarToggled(self, state: bool):
        if self.loader.getPrefs().showRotationBar != state:
            self.loader.getPrefs().showRotationBar = state
            self.loader.save(True)
            self.onViewerStateChanged()

    def onNavigationBarToggled(self, state: bool):
        if self.loader.getPrefs().showNavigationBar != state:
            self.loader.getPrefs().showNavigationBar = state
            self.loader.save(True)
            self.onViewerStateChanged()

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
        
        button_src = self.navigationToolbar.widgetForAction(self.imageListBtn)
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