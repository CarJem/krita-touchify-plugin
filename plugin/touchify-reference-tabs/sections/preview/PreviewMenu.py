from urllib.parse import urlparse
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .PreviewSection import PreviewSection
from ...extensions.filetypes import Filetypes
from ...DockerMenu import DockerMenu
from ...extensions.settings import *
from ...extensions.commons import Commons
from .ui.ContextMenu import ContextMenu

class PreviewMenu(DockerMenu):

    def __init__(self, section: PreviewSection, parent: QWidget | None = None):
        super().__init__("Preview Settings", parent)
        self.preview = section

        file_menu = self.addMenu("File")
        file_menu.addAction("Open Image...", self.openImage)
        file_menu.addAction("Open URL...", self.openUrl)

        self.context_menu = ContextMenu(self.preview.view, self, False)
        self.mergeMenu(self.context_menu)
        
        options_menu = self.addMenu("Options")
        options_menu.aboutToShow.connect(self.updateMenus)
        options_menu.addSeparator()

        options_menu.addSection("Image Scaling")
        self.scaleSettingGroup = QActionGroup(self)
        ############################################
        scaleSmoothAction = QAction("Smooth Scaling", self.scaleSettingGroup)
        scaleSmoothAction.setCheckable(True)
        scaleSmoothAction.setChecked(True)
        scaleSmoothAction.setData(1)
        ############################################
        scaleFastAction = QAction("Sharp Scaling", self.scaleSettingGroup)
        scaleFastAction.setCheckable(True)
        scaleFastAction.setData(2)
        ############################################
        self.scaleSettingGroup.triggered.connect(self.changeScaleSetting)
        options_menu.addActions(self.scaleSettingGroup.actions())

    def openUrl(self):
        url, ok = QInputDialog.getText( self, "Open Image", "URL", QLineEdit.Normal, "" )
        if ok and url != "":
            parsed_url = urlparse(url)
            file_bytes: bytes = Commons.Download_Data(url)
            file_name = os.path.join(Settings.getFileDialogState(), os.path.basename(parsed_url.path))
            file_path = Commons.Dialog_Save(self, "Downloaded Image Location", file_name, "File( *.* )" )

            if file_path not in [ "", ".", None ]: 
                with open( file_path, "wb" ) as f:
                    f.write( file_bytes )
                self.preview.Action_OpenImage(file_path)

    def openImage(self, filePath=False):
        filter = Filetypes.generateFiletypeFilter()
        if not filePath:
            filePath, _filter = QFileDialog.getOpenFileName(self, "Open an image", filter=filter, directory=Settings.getFileDialogState())
            if not filePath: return
            Settings.setFileDialogState(os.path.dirname(filePath))

        self.preview.Action_OpenImage(filePath)

    def updateMenus(self):
        self.checkCorrectScaleSetting()
        self.context_menu.Update()
        super().updateMenus()

    def changeScaleSetting(self, action: QAction):
        tab = self.preview
        tab.Action_ChangeScaleSetting(action.data())

    def checkCorrectScaleSetting(self):
        tab = self.preview
        for action in self.scaleSettingGroup.actions():
            if action.data() == tab.scalingMode:
                action.setChecked(True)
