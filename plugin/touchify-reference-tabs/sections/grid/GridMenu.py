from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .GridSection import GridSection
from ...DockerMenu import DockerMenu
from ...classes.settings import *

class GridMenu(DockerMenu):
    def __init__(self, section: GridSection, parent: QWidget | None = None):
        super().__init__("Grid Settings", parent)
        self.grid = section

        file_menu = self.addMenu("File")
 
        openFolderAction = QAction("Open Folder...")
        openFolderAction.triggered.connect(self.openFolder)
        file_menu.addAction(openFolderAction)

    def openFolder(self, folderPath=False):
        if not folderPath:
            folderPath = QFileDialog.getExistingDirectory(self, "Open a folder", Settings.getFileDialogState(), QFileDialog.Option.ShowDirsOnly)
            if not folderPath: return
            Settings.setFileDialogState(os.path.dirname(folderPath))

        self.grid.changePath(folderPath)


    def updateMenus(self):
        super().updateMenus()