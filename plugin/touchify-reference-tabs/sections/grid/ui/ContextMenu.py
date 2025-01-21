from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import TYPE_CHECKING
from ....DockerMenu import DockerMenu
from ....dataclasses.Clip import Clip
from ....dataclasses.InsertInfo import InsertInfo
from ....extensions.native_actions import NativeActions
if TYPE_CHECKING:
    from ..GridView import GridView

class ContextMenu(DockerMenu):
    def __init__(self, section: "GridView", parent: QWidget | None = None, is_context_menu: bool = False):
        super().__init__("Grid Context", parent)
        self.view = section
        self.context_menu_mode = is_context_menu

        self.Variables()
        self.Items_Create()
        self.Items_Update()
        self.Items_Connect()

    def Variables(self):
        self.string_pickcolor = "Picker"
        if self.view.ColorPicker.pigment_o == None: self.string_pickcolor += " [RGB]"
        self.event_position = QPoint(0,0)

        self.ctx_state_null = self.view.grid_qpixmap == None
        self.ctx_state_insert = NativeActions.Insert_Check( )
        self.ctx_clip = Clip(False, 0,0,1,1)
        self.ctx_w2 = self.view.w2
        self.ctx_h2 = self.view.h2
        self.ctx_grid_item_path = self.view.grid_path[self.view.giy][self.view.gix]
        self.ctx_grid_item_qpixmap = self.view.grid_qpixmap[self.view.giy][self.view.gix]
        self.ctx_clip_false = self.view.clip_false
        self.ctx_state_pickcolor = self.view.state_pickcolor

    def Update(self):
        self.Variables()
        self.Items_Update()

    def Items_Update(self):
        self.action_pick_color.setText(self.string_pickcolor)
        self.action_pick_color.setCheckable( True )
        self.action_pick_color.setChecked( self.view.state_pickcolor )
        self.action_analyse.setEnabled( not(self.ctx_state_null == True or self.view.ColorPicker.pigment_o == None) )
        self.menu_color.setEnabled( self.ctx_state_null == False )

        if self.context_menu_mode:
            self.action_pin.setEnabled( self.ctx_state_null == False )
            self.menu_file.setEnabled( self.ctx_state_null == False )
            self.menu_insert.setEnabled( self.ctx_state_null == False )
            self.action_insert_layer.setEnabled( self.ctx_state_insert == True )
            self.action_insert_ref.setEnabled( self.ctx_state_insert == True )

    def Items_Create(self):

        if self.context_menu_mode == False:
            edit_menu = self.addMenu("Edit")
            view_source = edit_menu
        else:
            view_source = self

        if self.context_menu_mode:
            # General
            self.action_pin = view_source.addAction( "Pin Reference" )
            view_source.addSeparator()
            # File
            self.menu_file = view_source.addMenu( "File" )
            self.action_file_location = self.menu_file.addAction( "File Location" )
            self.action_file_copy = self.menu_file.addAction( "Copy Path" )
        else:
            self.action_pin = None
            self.menu_file = None
            self.action_file_location = None
            self.action_file_copy = None

        # Color
        self.menu_color = view_source.addMenu( "Color" )
        self.action_pick_color = self.menu_color.addAction( self.string_pickcolor )
        self.action_analyse = self.menu_color.addAction( "Analyse" )

        if self.context_menu_mode:
            # Insert
            self.menu_insert = view_source.addMenu( "Insert" )
            self.action_document = self.menu_insert.addAction( "Document" )
            self.action_insert_layer = self.menu_insert.addAction( "Layer" )
            self.action_insert_ref = self.menu_insert.addAction( "Reference" )
        else:
            self.menu_insert = None
            self.action_document = None
            self.action_insert_layer = None
            self.action_insert_ref = None


    def Items_Connect(self):
        if self.context_menu_mode: return

        actions: list[QAction] = [
            # General
            self.action_pin,
            
            # Label
            self.action_file_copy,
            self.action_file_location,

            # Color
            self.action_pick_color,
            self.action_analyse,

            # Insert
            self.action_document,
            self.action_insert_layer,
            self.action_insert_ref
        ]

        for action in actions:
            if action: action.triggered.connect(self.Event_Trigger)


    def Event_Set(self, event: QMouseEvent):
        self.event_position = event.pos()

    def Event_Trigger( self ):
        sender = self.sender()
        if isinstance(sender, QAction): self.Event_Execute(sender)

    def Event_Execute( self, action: QAction | None ):
        view = self.view


        # General
        if action == self.action_pin:
            pin = InsertInfo(self.ctx_w2, self.ctx_h2, self.ctx_grid_item_path)
            view.SIGNAL_PIN_IMAGE.emit( pin, self.ctx_clip_false )

        # File
        if action == self.action_file_location:
            view.SIGNAL_LOCATION.emit( self.ctx_grid_item_path )
        if action == self.action_file_copy:
            NativeActions.Path_Copy( self.ctx_grid_item_path )

        # Color
        if action == self.action_pick_color:
            view.state_pickcolor = not self.ctx_state_pickcolor
        if action == self.action_analyse:
            qimage = self.ctx_grid_item_qpixmap.toImage()
            view.SIGNAL_ANALYSE.emit( qimage )

        # Insert
        if action == self.action_document:
            view.SIGNAL_NEW_DOCUMENT.emit( self.ctx_grid_item_path, self.ctx_clip )
        if action == self.action_insert_layer:
            view.SIGNAL_INSERT_LAYER.emit( self.ctx_grid_item_path, self.ctx_clip )
        if action == self.action_insert_ref:
            view.SIGNAL_INSERT_REFERENCE.emit( self.ctx_grid_item_path, self.ctx_clip )


    @staticmethod
    def OpenContextMenu( view: "GridView", event: QMouseEvent ):
        QApplication.restoreOverrideCursor()
        qmenu = ContextMenu(view, view, True)
        qmenu.Event_Set(event)
        action = qmenu.exec_( view.mapToGlobal( event.pos() ) )
        qmenu.Event_Execute(action)
        qmenu.deleteLater()
