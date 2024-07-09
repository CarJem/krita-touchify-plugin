
from math import e
from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *

from ..components.krita_ext.KisAngleSelector import KisAngleSelector

from ..config import KritaSettings

DOCKER_TITLE = 'Brush Options'

class SliderSpinBox(QDoubleSpinBox):
   
    def __init__(self, min: float = 0, max: float = 100, isInt: bool = False, parent=None):
        super(SliderSpinBox, self).__init__(parent)

        self.setMinimumWidth(100)
        self.setFixedHeight(30)

        self.editMode = False
        self.editModeInit = False
        self.scaling = 1
        self.isInt = isInt
        self.contextMenuOpened = False

        self.setRange(min, max)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.lineEdit().setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.lineEdit().installEventFilter(self)
        self.lineEdit().setMouseTracking(True)
        self.endEdit()

        self.editingFinished.connect(self.endEdit)
        self.lineEdit().selectionChanged.connect(self.onSelectionChanged)
        self.lineEdit().returnPressed.connect(self.endEdit)
        super().valueChanged.connect(self.updateProgBar)

    def onSelectionChanged(self):
        if self.editMode == False:
            self.lineEdit().deselect()

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.Type.MouseButtonPress or e.type() == QEvent.Type.MouseMove:
            m: QMouseEvent = e
            if self.editMode == False:
                if m.buttons() == Qt.MouseButton.LeftButton:
                    self.setFocus()
                    delta = m.pos().x() / self.lineEdit().width()
                    spinboxValue = delta**self.scaling * self.maximum()
                    if self.isInt:
                        self.setValue(int(spinboxValue))
                    else:
                        self.setValue(spinboxValue)
                elif m.buttons() == Qt.MouseButton.RightButton:
                    self.startEdit()
                    e.ignore()
            return True
        elif e.type() == QEvent.Type.KeyPress:
            e: QKeyEvent = e
            if self.editMode:
                if (e.key() == Qt.Key.Key_Return or
                    e.key() == Qt.Key.Key_Enter or
                    e.key() == Qt.Key.Key_Escape): self.endEdit()
            else:
                e.ignore()
            return True
        return super().eventFilter(o, e)
    
    def textFromValue(self, value: float):
        if self.isInt:
            return str(int(value))
        else:
            return super().textFromValue(value)
         
    def contextMenuEvent(self, e: QContextMenuEvent):
        if self.editMode == False:
            e.ignore()
        elif self.editModeInit == False:
            self.editModeInit = True
            e.ignore()
        else:
            self.contextMenuOpened = True
            super().contextMenuEvent(e)

    def focusInEvent(self, e: QFocusEvent):
        if self.contextMenuOpened:
            self.contextMenuOpened = False
        super().focusInEvent(e)

    def focusOutEvent(self, e: QFocusEvent):
        super().focusOutEvent(e)

    def getDelta(self):
        return (self.value() / self.maximum())**(1./self.scaling)

    def endEdit(self):
        if self.contextMenuOpened:
            return
        
        self.editMode = False
        self.editModeInit = False
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setCursor(Qt.CursorShape.SplitHCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.lineEdit().deselect()
        self.updateProgBar()

    def startEdit(self):
        self.editMode = True
        self.lineEdit().unsetCursor()
        self.lineEdit().setReadOnly(False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.lineEdit().selectAll()
        self.updateProgBar()
        
    def setRange(self, min, max):
        super().setRange(min, max)

    def setScaling(self, s):
        self.scaling = s

    def stepDown(self):
        self.endEdit()
        super().stepDown()

    def stepBy(self, step):
        self.endEdit()
        super().stepBy(step)

    def stepUp(self):
        self.endEdit()
        super().stepUp()

    def updateProgBar(self):
        delta = self.getDelta()
        pre_highlight = qApp.palette().color(QPalette.ColorRole.Highlight)

        if self.editMode:
            pre_highlight = pre_highlight.darker(150)

        highlight = pre_highlight.name().split("#")[1]
        background = qApp.palette().color(QPalette.ColorRole.Base).name().split("#")[1]
        

        if delta == 0:
            self.lineEdit().setStyleSheet(f"QLineEdit {{background-color: #{background}}}")
        elif delta >= 1:
            self.lineEdit().setStyleSheet(f"QLineEdit {{background-color: #{highlight}}}")
        else:
            buttonStyle = f"""QLineEdit {{background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #{highlight}, 
            stop:{delta} #{highlight}, 
            stop:{delta + 0.01} #{background}, 
            stop:1 #{background}) }}"""
            self.lineEdit().setStyleSheet(buttonStyle)

    def setValue(self, val):
        super().setValue(val)

    def setAffixes(self, pre, suf):
        self.setPrefix(pre)
        self.setSuffix(suf)

    def connectValueChanged(self, func):
        super().valueChanged.connect(func)

    def synchronize(self):
        pass

class BrushSizeSlider(SliderSpinBox):

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

class BrushOpacitySlider(SliderSpinBox):

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

class BrushFlowSlider(SliderSpinBox):
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

class BrushOptionsConfig:
    
    def __init__(self):
        self.ShowFlowSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowFlowSlider", True)
        self.ShowOpacitySlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowOpacitySlider", True)
        self.ShowSizeSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowSizeSlider", True)
        self.ShowRotationSlider = KritaSettings.readSettingBool("BrushOptionsDocker", "ShowRotationSlider", True)
    
    def toggle(self, setting: str):
        if hasattr(self, setting):
            currentValue = getattr(self, setting)
            currentValue = not currentValue
            setattr(self, setting, currentValue)
            self.save()
        

    def save(self):
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowFlowSlider", self.ShowFlowSlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowOpacitySlider", self.ShowOpacitySlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowSizeSlider", self.ShowSizeSlider)
        KritaSettings.writeSettingBool("BrushOptionsDocker", "ShowRotationSlider", self.ShowRotationSlider)

class BrushOptionsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super(BrushOptionsWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.config = BrushOptionsConfig()

        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.updateSliders)
        self.timer_pulse.start(100)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

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
        self.optionsButton.setStyleSheet(f"QPushButton::menu-indicator{{width:0px;}}")
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

        def updateSliderVisibility(option: bool, slider: SliderSpinBox):
            if option and slider.isHidden():
                slider.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
                slider.show()
            elif option == False and slider.isVisible():
                slider.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
                slider.hide()

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