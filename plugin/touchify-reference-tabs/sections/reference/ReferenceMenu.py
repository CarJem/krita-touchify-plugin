from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .ReferenceSection import ReferenceSection
from ...DockerMenu import DockerMenu
from .ui.ContextMenu import ContextMenu
from ...extensions.commons import Commons

class ReferenceMenu(DockerMenu):

    def __init__(self, section: ReferenceSection, parent: QWidget | None = None):
        super().__init__("Reference Settings", parent)
        self.reference = section

        #region File Menu
        fileMenu = self.addMenu("File")
        self.file_group = QActionGroup(self)

        self.new_file_action = QAction("New Reference...", self.file_group)
        self.new_file_action.triggered.connect(self.Action_CreateFile)

        self.open_file_action = QAction("Open Reference...", self.file_group)
        self.open_file_action.triggered.connect(self.Action_OpenFile)

        file_group_seperator = QAction(self.file_group)
        file_group_seperator.setSeparator(True)

        self.save_file_action = QAction("Save Reference", self.file_group)
        self.save_file_action.triggered.connect(self.Action_SaveFile)
        self.save_file_action.setEnabled(False)

        file_group_seperator_2 = QAction(self.file_group)
        file_group_seperator_2.setSeparator(True)

        self.unload_file_action = QAction("Unload Reference...", self.file_group)
        self.unload_file_action.triggered.connect(self.Action_UnloadFile)
        self.unload_file_action.setEnabled(False)

        file_group_seperator_3 = QAction(self.file_group)
        file_group_seperator_3.setSeparator(True)

        self.export_file_action = QAction("Export Reference...", self.file_group)
        self.export_file_action.triggered.connect(self.Action_ExportFile)
        self.export_file_action.setEnabled(False)

        self.download_files_action = QAction("Download Files...", self.file_group)
        self.download_files_action.triggered.connect(self.Action_DownloadFile)
        self.download_files_action.setEnabled(False)

        fileMenu.addActions(self.file_group.actions())
        #endregion

        editMenu = self.addMenu("Edit")
        editMenu.aboutToShow.connect(self.updateMenus)

        self.context_menu = ContextMenu(self.Board(), self, False)
        self.mergeMenu(self.context_menu)

        #region Options Menu

        optionsMenu = self.addMenu("Options")
        optionsMenu.aboutToShow.connect(self.updateMenus)
        
        self.autosave_action = optionsMenu.addAction("Autosave")
        self.autosave_action.setCheckable(True)
        self.autosave_action.setChecked(False)
        self.autosave_action.triggered.connect(self.Action_ToggleAutoSave)

        #endregion

    def RefState( self ):
        return self.reference.ref_state
    
    def Board( self ):
        return self.reference.view


    def Action_CreateFile( self ):
        ref_board = Commons.Dialog_Save(self, "New File Location", "board_000000", "File( *.eo )" )
        if ref_board != None: self.RefState().Data_Load( ref_board )

    def Action_OpenFile( self ):
        ref_board = Commons.Dialog_Load(self, "Open File Location", "File( *.eo )" )
        if ref_board != None: self.RefState().Data_Load( ref_board )
            
    def Action_SaveFile( self ):
        self.RefState().Data_Save()

    def Action_UnloadFile( self ):
        self.RefState().Data_Unload()

    def Action_ExportFile( self ):
        export_path = Commons.Dialog_Save(self, "Export File Location", "export_000000", "File( *.eo )" )
        if export_path != None: self.RefState().Data_Export( export_path )

    def Action_DownloadFile( self ):
        download_folder = Commons.Dialog_Directory(self, "Download Folder Location" )
        if download_folder != None: self.RefState().Data_Download( download_folder )

    def Action_ToggleAutoSave(self):
        self.Board().ModeSet_AutoSave()

    def updateMenus(self):
        is_file_open = self.RefState().loaded()

        self.save_file_action.setEnabled(is_file_open)
        self.unload_file_action.setEnabled(is_file_open)
        self.export_file_action.setEnabled(is_file_open)
        self.download_files_action.setEnabled(is_file_open)
        self.autosave_action.setEnabled(is_file_open)

        self.autosave_action.setChecked(self.Board().mode_autosave)


        self.context_menu.Update()
        super().updateMenus()
