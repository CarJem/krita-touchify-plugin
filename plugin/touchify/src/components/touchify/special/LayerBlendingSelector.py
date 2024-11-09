from PyQt5.QtWidgets import *
from ....docker_manager import *
from krita import *
from ....variables import *
from ....helpers import TouchifyHelpers

try:
    from shortcut_composer.api_krita.enums.blending_mode import BlendingMode, PRETTY_NAMES
    SHORTCUT_COMPOSER_LOADED = True
except:
    SHORTCUT_COMPOSER_LOADED = False


class LayerBlendingOption(QWidgetAction):


    class Label(QLabel):
        clicked=pyqtSignal()

        def mousePressEvent(self, ev):
            self.clicked.emit()

    toggled = pyqtSignal(QWidgetAction)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.hostWidget = QWidget(parent)
        self.setDefaultWidget(self.hostWidget)

        self.hostLayout = QHBoxLayout(self.hostWidget)
        self.hostLayout.setContentsMargins(0,0,0,0)
        self.hostWidget.setLayout(self.hostLayout)

        self.checkbox = QCheckBox(self.hostWidget)
        self.checkbox.stateChanged.connect(self.onToggled)
        self.hostLayout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignLeft)

        self.label = LayerBlendingOption.Label(self.hostWidget)
        self.label.setStyleSheet("text-align: left; padding: 4px;")
        self.label.clicked.connect(self.onClicked)
        self.hostLayout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignLeft)

        self.hostLayout.addStretch()
        


        self.__doNotUpdate = False

    def setText(self, text: str):
        self.label.setText(text)
        super().setText(text)

    def isCheckboxChecked(self):
        return self.checkbox.isChecked()

    def setCheckboxChecked(self, state: bool):
        self.__doNotUpdate = True
        self.checkbox.setChecked(state)
        self.__doNotUpdate = False

    def onClicked(self):
        self.triggered.emit()

    def onToggled(self):
        if self.__doNotUpdate == False:
            self.toggled.emit(self)

class LayerBlendingSelector(QPushButton):




    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.timerActive = False
        if SHORTCUT_COMPOSER_LOADED:
            self.HAS_LOADED = True
            self.constructLayout()
        else:
            self.HAS_LOADED = False

    def showEvent(self, event):
        if self.HAS_LOADED: self.timerActive = True
        super().showEvent(event)

    def hideEvent(self, event):
        if self.HAS_LOADED: self.timerActive = False
        super().hideEvent(event)
        
    def closeEvent(self, event):
        if self.HAS_LOADED: self.timerActive = False
        super().closeEvent(event)

    def constructLayout(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.modeActions: list[LayerBlendingOption] = []
        self.setupTimer()
        self.setMinimumHeight(30)

        self.clicked.connect(self.showMenu)  
        self.menu = QMenu(self)
        self.menu.aboutToShow.connect(self.beforeShow)
        self.setStyleSheet("text-align: left; padding: 4px;")

        self.favsMenu = self.menu.addMenu("Favorites")
        self.favsUpdating = False

        for group in BlendingMode._groups_:
            subMenu = self.menu.addMenu(group)
            for mode in BlendingMode._groups_[group]:
                actualName = self.getFancyName(mode.value)
                action = LayerBlendingOption(subMenu)
                action.setText(actualName)
                action.setData(mode.value)
                action.triggered.connect(self.changePreset)
                action.toggled.connect(self.toggleFavorite)
                self.modeActions.append(action)
                subMenu.addAction(action)
        self.updateFavs()
                
        self.setMenu(self.menu)
        self.timerActive = True

    def setupTimer(self):
        parentExtension = TouchifyHelpers.getExtension()
        if parentExtension:
            parentExtension.intervalTimerTicked.connect(self.onTimerTick)

    def onTimerTick(self):
        if self.timerActive:
            self.updateInterface()

    def beforeShow(self):
        self.updateFavs()

    def updateInterface(self):
        if self.isVisible() == False:
            return
        
        activeWindow = Krita.instance().activeDocument()
        if not activeWindow: return

        activeView = activeWindow.activeNode()
        if not activeView: return

        text = self.getFancyName(activeView.blendingMode())
        self.setText(text)

    def updateFavs(self):
        if self.favsUpdating: return

        self.favsUpdating = True
        self.favsMenu.clear()

        self.favoriteModes = Krita.instance().readSetting("", "favoriteCompositeOps", "").split(",")
        for mode in self.favoriteModes:
            actualName = self.getFancyName(mode)
            action = self.favsMenu.addAction(actualName)
            action.setData(mode)
            action.triggered.connect(self.changePreset)

        for action in self.modeActions:
            mode_id = str(action.data())
            if mode_id in self.favoriteModes:
                action.setCheckboxChecked(True)
            else:
                action.setCheckboxChecked(False)
        self.favsUpdating = False

    def toggleFavorite(self, sender: LayerBlendingOption):
        if self.favsUpdating: return
        
        mode = str(sender.data())

        favoriteCompositeOps = Krita.instance().readSetting("", "favoriteCompositeOps", "").split(",")

        if sender.isCheckboxChecked() == True and mode not in favoriteCompositeOps:
            favoriteCompositeOps.append(mode)
        elif sender.isCheckboxChecked() == False and mode in favoriteCompositeOps:
            favoriteCompositeOps.remove(mode)

        Krita.instance().writeSetting("", "favoriteCompositeOps", ",".join(favoriteCompositeOps))
        self.updateFavs()

    def getFancyName(self, activeMode: str):
        for group in BlendingMode._groups_:
            for mode in BlendingMode._groups_[group]:
                if activeMode == mode.value:
                    actualName = mode.name
                    if mode in PRETTY_NAMES:
                        actualName = PRETTY_NAMES[mode]
                    else:
                        actualName = mode.name.replace('_', ' ').title()
                    return actualName
        return activeMode
        
    @pyqtSlot()
    def changePreset(self):
        sender: QAction = self.sender()
        mode = str(sender.data())

        activeWindow = Krita.instance().activeDocument()
        if not activeWindow: return

        activeView = activeWindow.activeNode()
        if not activeView: return

        activeView.setBlendingMode(mode)
        self.setText(sender.text())
        self.updateFavs()

