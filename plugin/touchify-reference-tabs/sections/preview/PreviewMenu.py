from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .PreviewSection import PreviewSection
from ...classes.common import generateFiletypeFilter
from ...DockerMenu import DockerMenu
from ...classes.settings import *

class PreviewMenu(DockerMenu):

    def __init__(self, section: PreviewSection, parent: QWidget | None = None):
        super().__init__("Preview Settings", parent)
        self.preview = section

        self.filetype_filter = generateFiletypeFilter()

        file_menu = self.addMenu("File")
        file_menu.addAction("Open Image...", self.openImage)
        
        view_menu = self.addMenu("View")
        view_menu.addSeparator()

        zoomSettingsMenu = view_menu.addMenu("Zoom Setting")
        self.fitSettingGroup = QActionGroup(self)
        fitPageAction = QAction("Fit Page", self.fitSettingGroup)
        fitPageAction.setCheckable(True)
        fitPageAction.setData(1)
        fitWidthAction = QAction("Fit Width", self.fitSettingGroup)
        fitWidthAction.setCheckable(True)
        fitWidthAction.setData(2)
        fitHeightAction = QAction("Fit Height", self.fitSettingGroup)
        fitHeightAction.setCheckable(True)
        fitHeightAction.setData(3)
        fitFullsizeAction = QAction("Zoom 100%", self.fitSettingGroup)
        fitFullsizeAction.setCheckable(True)
        fitFullsizeAction.setData(4)

        fitPageAction.setChecked(True)
        self.fitSettingGroup.triggered.connect(self.changeFitSetting)
        zoomSettingsMenu.addActions(self.fitSettingGroup.actions())

        scaleSettingsMenu = view_menu.addMenu("Scaling Mode Setting")
        self.scaleSettingGroup = QActionGroup(self)
        scaleSmoothAction = QAction("Smooth Scaling", self.scaleSettingGroup)
        scaleSmoothAction.setCheckable(True)
        scaleSmoothAction.setData(1)
        scaleFastAction = QAction("Sharp Scaling", self.scaleSettingGroup)
        scaleFastAction.setCheckable(True)
        scaleFastAction.setData(2)

        scaleSmoothAction.setChecked(True)
        self.scaleSettingGroup.triggered.connect(self.changeScaleSetting)
        scaleSettingsMenu.addActions(self.scaleSettingGroup.actions())

        view_menu.addAction("Change Background Color...", self.changeBGColor)

    def openImage(self, filePath=False):
        if not filePath:
            filePath, _filter = QFileDialog.getOpenFileName(self, "Open an image", filter=self.filetype_filter, directory=Settings.getFileDialogState())
            if not filePath: return
            Settings.setFileDialogState(os.path.dirname(filePath))

        self.preview.openImage(filePath)

    def updateMenus(self):
        self.checkCorrectFitSetting()
        self.checkCorrectScaleSetting()
        super().updateMenus()

    def changeFitSetting(self, action: QAction):
        tab = self.preview
        tab.action_changeFitSetting(action.data())

    def checkCorrectFitSetting(self):
        tab = self.preview
        for action in self.fitSettingGroup.actions():
            if action.data() == tab.fitSetting:
                action.setChecked(True)

    def changeScaleSetting(self, action: QAction):
        tab = self.preview
        tab.action_changeScaleSetting(action.data())

    def checkCorrectScaleSetting(self):
        tab = self.preview
        for action in self.scaleSettingGroup.actions():
            if action.data() == tab.scalingMode:
                action.setChecked(True)

    def changeBGColor(self):
        self.preview.action_changeBackgroundColor()
