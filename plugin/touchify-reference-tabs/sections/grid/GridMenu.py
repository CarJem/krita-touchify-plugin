from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .GridSection import GridSection
from ...DockerMenu import DockerMenu
from ...extensions.settings import *
from .ui.ContextMenu import ContextMenu

class GridMenu(DockerMenu):
    def __init__(self, section: GridSection, parent: QWidget | None = None):
        super().__init__("Grid Settings", parent)
        self.grid = section

        file_menu = self.addMenu("File")
 
        openFolderAction = file_menu.addAction("Open Folder...")
        openFolderAction.triggered.connect(self.openFolder)

        self.context_menu = ContextMenu(self.grid.grid_view, self, False)
        self.mergeMenu(self.context_menu)

        optionsMenu = self.addMenu("Options")
        optionsMenu.aboutToShow.connect(self.updateMenus)
        self.fitImagesAction = optionsMenu.addAction("Fit Images")
        self.fitImagesAction.setCheckable(True)
        self.fitImagesAction.setChecked(self.grid.grid_view.grid_fit == Qt.AspectRatioMode.KeepAspectRatio)
        self.fitImagesAction.triggered.connect(self.toggleImageFit)

    def openFolder(self, folderPath=False):
        if not folderPath:
            folderPath = QFileDialog.getExistingDirectory(self, "Open a folder", Settings.getFileDialogState(), QFileDialog.Option.ShowDirsOnly)
            if not folderPath: return
            Settings.setFileDialogState(os.path.dirname(folderPath))

        self.grid.changePath(folderPath)

    def toggleImageFit(self):
        boolean = not self.grid.grid_view.grid_fit == Qt.AspectRatioMode.KeepAspectRatio
        self.grid.grid_view.Grid_Fit(boolean)

    def updateMenus(self):
        self.fitImagesAction.setChecked(self.grid.grid_view.grid_fit == Qt.AspectRatioMode.KeepAspectRatio)
        self.context_menu.Update()
        super().updateMenus()