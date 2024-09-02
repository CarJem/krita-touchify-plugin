
from math import e
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from .....variables import *

from .....stylesheet import Stylesheet
from .....ext.KritaSettings import *
from ....krita.KisSliderSpinBox import KisSliderSpinBox
from ....krita.KisAngleSelector import KisAngleSelector

DOCKER_TITLE = 'Brush Options'



class BrushOptionsDockerCfg:

    def __init__(self):
        self.ShowFlowSlider = KritaSettings.readSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowFlowSlider", True)
        self.ShowOpacitySlider = KritaSettings.readSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowOpacitySlider", True)
        self.ShowSizeSlider = KritaSettings.readSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowSizeSlider", True)
        self.ShowRotationSlider = KritaSettings.readSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowRotationSlider", True)

    def toggle(self, setting: str):
        if hasattr(self, setting):
            currentValue = getattr(self, setting)
            currentValue = not currentValue
            setattr(self, setting, currentValue)
            self.save()


    def save(self):
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowFlowSlider", self.ShowFlowSlider)
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowOpacitySlider", self.ShowOpacitySlider)
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowSizeSlider", self.ShowSizeSlider)
        KritaSettings.writeSettingBool(TOUCHIFY_ID_DOCKER_BRUSHOPTIONSDOCKER, "ShowRotationSlider", self.ShowRotationSlider)

class BrushSizeSlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushSizeSlider, self).__init__(0.01, 1000, False, parent)
        self.view: View = None
        self.setScaling(3)
        self.setAffixes('Size: ', ' px')
        self.connectValueChanged(self.valueChanged)
        
    def valueChanged(self, value):
        if self.view == None: return
        self.view.setBrushSize(value)

    def synchronizeView(self, view: View):
        self.view = view
        self.synchronize()

    def synchronize(self):
        if self.view == None: return
        self.setValue(self.view.brushSize())

class BrushOpacitySlider(KisSliderSpinBox):

    def __init__(self, parent=None):
        super(BrushOpacitySlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.setAffixes('Opacity: ', '%')
        self.connectValueChanged(self.valueChanged)
        
    def valueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingOpacity(self.value()/100)

    def synchronizeView(self, view: View):
        self.view = view
        self.synchronize()

    def synchronize(self):
        if self.view == None: return
        self.setValue(self.view.paintingOpacity()*100)

class BrushFlowSlider(KisSliderSpinBox):
    def __init__(self, parent=None):
        super(BrushFlowSlider, self).__init__(parent=parent, isInt=True)
        self.view: View = None
        self.setAffixes('Flow: ', '%')
        self.connectValueChanged(self.valueChanged)
        
    def valueChanged(self, value):
        if self.view == None: return
        self.view.setPaintingFlow(self.value()/100)
        
    def synchronizeView(self, view: View):
        self.view = view
        self.synchronize()
    
    def synchronize(self):
        if self.view == None: return
        self.setValue(self.view.paintingFlow()*100)

class BrushRotationSlider(KisAngleSelector):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(100)
        self.setFixedHeight(30)
        self.setWidgetsHeight(30)

        self.setFlipOptionsMode(KisAngleSelector.FlipOptionsMode.MenuButton)
        self.spinBox.setPrefix('Rotation: ')
        self.spinBox.valueChanged.connect(self.valueChanged)

    def valueChanged(self, value):
        if self.view == None: return
        self.view.setBrushRotation(self.spinBox.value())
        
    def synchronizeView(self, view: View):
        self.view = view
        self.synchronize()
    
    def synchronize(self):
        if self.view == None: return
        self.setAngle(self.view.brushRotation())

class BrushOptionsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super(BrushOptionsWidget, self).__init__(parent)
        self.config = BrushOptionsDockerCfg()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.updateSliders)
        self.timer_pulse.start(100)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.gridLayout = QVBoxLayout(self)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0,0,0,0)

        self.sizeSlider = BrushSizeSlider(self)
        self.opacitySlider = BrushOpacitySlider(self)
        self.flowSlider = BrushFlowSlider(self)
        self.rotationSlider = BrushRotationSlider(self)

        self.optionsMenu = self.genMenu()
        self.optionsButton = QPushButton(self)
        self.optionsButton.setIcon(Krita.instance().icon("configure"))
        self.optionsButton.setMenu(self.optionsMenu)
        self.optionsButton.setFixedHeight(15)
        self.optionsButton.setStyleSheet(Stylesheet.instance().hide_menu_indicator)
        self.optionsButton.clicked.connect(self.optionsButton.showMenu)
        self.gridLayout.addWidget(self.optionsButton)
        
        self.gridLayout.addWidget(self.sizeSlider)
        self.gridLayout.addWidget(self.opacitySlider)
        self.gridLayout.addWidget(self.flowSlider)
        self.gridLayout.addWidget(self.rotationSlider)
        self.gridLayout.addWidget(self.optionsButton)

    def genMenu(self):
        menu = QMenu()
        sect = menu.addSeparator()
        sect.setText("Show:")

        sizeToggle = menu.addAction("Size")
        sizeToggle.setCheckable(True)
        sizeToggle.setChecked(self.config.ShowSizeSlider)
        sizeToggle.toggled.connect(lambda: self.toggleSlider("ShowSizeSlider"))

        opacityToggle = menu.addAction("Opacity")
        opacityToggle.setCheckable(True)
        opacityToggle.setChecked(self.config.ShowOpacitySlider)
        opacityToggle.toggled.connect(lambda: self.toggleSlider("ShowOpacitySlider"))

        flowToggle = menu.addAction("Flow")
        flowToggle.setCheckable(True)
        flowToggle.setChecked(self.config.ShowFlowSlider)
        flowToggle.toggled.connect(lambda: self.toggleSlider("ShowFlowSlider"))

        rotationToggle = menu.addAction("Rotation")
        rotationToggle.setCheckable(True)
        rotationToggle.setChecked(self.config.ShowRotationSlider)
        rotationToggle.toggled.connect(lambda: self.toggleSlider("ShowRotationSlider"))

        return menu

    
    def toggleSlider(self, setting: str):
        self.config.toggle(setting)
        self.updateSliders()


    def updateSliders(self):

        def updateSliderVisibility(option: bool, slider: KisSliderSpinBox):
            if option and slider.isHidden():
                slider.show()
                slider.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                slider.updateGeometry()
                slider.adjustSize()
            elif option == False and slider.isVisible():
                slider.hide()
                slider.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
                slider.updateGeometry()
                slider.adjustSize()

        updateSliderVisibility(self.config.ShowSizeSlider, self.sizeSlider)
        updateSliderVisibility(self.config.ShowOpacitySlider, self.opacitySlider)
        updateSliderVisibility(self.config.ShowFlowSlider, self.flowSlider)
        updateSliderVisibility(self.config.ShowRotationSlider, self.rotationSlider)

        active_window = Krita.instance().activeWindow()
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return

        self.sizeSlider.synchronizeView(active_view)
        self.opacitySlider.synchronizeView(active_view)
        self.flowSlider.synchronizeView(active_view)
        self.rotationSlider.synchronizeView(active_view)
        
    def showEvent(self, event):
        self.timer_pulse.start()
        super().showEvent(event)

    def closeEvent(self, event):
        self.timer_pulse.stop()
        super().closeEvent(event)

    def onCanvasChanged(self, canvas: Canvas):
        active_window = Krita.instance().activeWindow()
        if active_window == None: return

        active_view = active_window.activeView()
        if active_view == None: return

        self.sizeSlider.synchronizeView(active_view)
        self.opacitySlider.synchronizeView(active_view)
        self.flowSlider.synchronizeView(active_view)
        self.rotationSlider.synchronizeView(active_view)

class BrushOptionsDocker(DockWidget):

    def __init__(self): 
        super().__init__()
        self.setWindowTitle(DOCKER_TITLE)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.brushOptions = BrushOptionsWidget(self)
        self.setWidget(self.brushOptions)

    def showEvent(self, event):
        super().showEvent(event)

    def closeEvent(self, event):
        super().closeEvent(event)
    
    # notifies when views are added or removed
    # 'pass' means do not do anything
    def canvasChanged(self, canvas):
        self.brushOptions.onCanvasChanged(canvas)