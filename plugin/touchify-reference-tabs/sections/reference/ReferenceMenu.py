from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .ReferenceSection import ReferenceSection
from ...DockerMenu import DockerMenu
from .ReferenceContextMenu import ReferenceContextMenu

class ReferenceMenu(DockerMenu):
    def __init__(self, section: ReferenceSection, parent: QWidget | None = None):
        super().__init__("Reference Settings", parent)
        self.reference = section

        #region File Menu
        fileMenu = self.addMenu("File")
        self.file_group = QActionGroup(self)

        self.new_file_action = QAction("New Reference...", self.file_group)
        self.new_file_action.triggered.connect(self.createRef)

        self.open_file_action = QAction("Open Reference...", self.file_group)
        self.open_file_action.triggered.connect(self.openReference)

        file_group_seperator = QAction(self.file_group)
        file_group_seperator.setSeparator(True)

        self.save_file_action = QAction("Save Reference", self.file_group)
        self.save_file_action.triggered.connect(self.saveRef)
        self.save_file_action.setEnabled(False)

        self.save_as_file_action = QAction("Save Reference As...", self.file_group)
        self.save_as_file_action.triggered.connect(self.saveRefAs)
        self.save_as_file_action.setEnabled(False)

        file_group_seperator_2 = QAction(self.file_group)
        file_group_seperator_2.setSeparator(True)

        self.unload_action = QAction("Unload Reference...", self.file_group)
        self.unload_action.triggered.connect(self.unloadRef)
        self.unload_action.setEnabled(False)

        file_group_seperator_3 = QAction(self.file_group)
        file_group_seperator_3.setSeparator(True)

        self.export_action = QAction("Export Reference...", self.file_group)
        self.export_action.triggered.connect(self.exportRef)
        self.export_action.setEnabled(False)

        self.export_files = QAction("Download Files...", self.file_group)
        self.export_files.triggered.connect(self.downloadRefFiles)
        self.export_files.setEnabled(False)

        fileMenu.addActions(self.file_group.actions())
        #endregion

        self.context_menu = ReferenceContextMenu(self.reference.view, self, False)
        self.mergeMenu(self.context_menu)

        #region Options Menu

        optionsMenu = self.addMenu("Options")
        optionsMenu.aboutToShow.connect(self.updateMenus)
        
        self.autosave_action = optionsMenu.addAction("Autosave")
        self.autosave_action.setCheckable(True)
        self.autosave_action.setChecked(False)
        self.autosave_action.triggered.connect(self.toggleAutoSave)

        #endregion



    def createRef(self):   
        self.reference.Action_CreateFile()

    def saveRef(self):
        self.reference.Action_SaveFile()

    def saveRefAs(self):
        self.reference.Action_SaveFileAs()

    def unloadRef(self):
        self.reference.Action_UnloadFile()

    def openReference(self):
        self.reference.Action_OpenFile()

    def exportRef(self):
        self.reference.Action_ExportFile()

    def toggleAutoSave(self):
        self.reference.view.state_autosave = not self.reference.view.state_autosave
        self.autosave_action.setChecked(self.reference.view.state_autosave)

    def downloadRefFiles(self):
        self.reference.Action_FileDownload()

    def updateMenus(self):
        is_file_open = self.reference.ref_state.ref_board != None

        self.save_file_action.setEnabled(is_file_open)
        self.save_as_file_action.setEnabled(is_file_open)
        self.unload_action.setEnabled(is_file_open)
        self.export_action.setEnabled(is_file_open)
        self.export_files.setEnabled(is_file_open)

        self.autosave_action.setChecked(self.reference.view.state_autosave)
        self.autosave_action.setEnabled(is_file_open)


        self.context_menu.Update()
        super().updateMenus()
