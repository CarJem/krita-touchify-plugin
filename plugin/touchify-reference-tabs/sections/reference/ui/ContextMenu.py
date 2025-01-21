from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import TYPE_CHECKING
from ....DockerMenu import DockerMenu
from ....dataclasses.Clip import Clip
from ....extensions.native_actions import NativeActions
if TYPE_CHECKING:
    from ..ReferenceView import ReferenceView

class ContextMenu(DockerMenu):
    def __init__(self, section: "ReferenceView", parent: QWidget | None = None, is_context_menu: bool = False):
        super().__init__("Reference Context", parent)
        self.view = section
        self.context_menu_mode = is_context_menu

        self.Variables()
        self.Items_Create()
        self.Items_Update()
        self.Items_Connect()

    def Variables(self):
        self.event_position = QPoint(0,0)
        self.state_insert = NativeActions.Insert_Check()
    
        self.menu_pack_string = f"Pack [ { self.view.select_count } ]"

        # Color
        self.action_color_picker_string = "Color Picker"
        if self.view.ColorPicker.pigment_o == None: self.action_color_picker_string += " [RGB]"

        # Path
        if self.view.pin_index == None:
            self.ctx_pin_tipo = None
            self.ctx_pin_egs = False
            self.ctx_pin_efx = False
            self.ctx_pin_efy = False
            self.ctx_pin_erz = 0
            self.ctx_pin_path = None
            self.ctx_pin_web = None
            self.ctx_pin_qpixmap = None
        else:
            self.ctx_pin = self.view.pin_list[self.view.pin_index]
            self.ctx_pin_tipo = self.ctx_pin.tipo
            self.ctx_pin_erz = self.ctx_pin.trz
            self.ctx_pin_egs = self.ctx_pin.egs
            self.ctx_pin_efx = self.ctx_pin.efx
            self.ctx_pin_efy = self.ctx_pin.efy
            self.ctx_pin_path = self.ctx_pin.path
            self.ctx_pin_web = self.ctx_pin.web
            self.ctx_pin_qpixmap = self.ctx_pin.qpixmap

        # Relative
        self.ctx_relative = []
        for i in range( 0, self.view.pin_count ):
            if ( self.view.pin_list[i].active == True or self.view.pin_list[i].select == True ):
                self.ctx_relative.append( self.view.pin_list[i] )

        # Clip
        self.ctx_clip = Clip(False, 0,0,1,1)

    def Update(self):
        self.Variables()
        self.Items_Update()

    def Items_Update(self):
        self.menu_pack.setTitle(self.menu_pack_string)
        self.action_color_picker.setText(self.action_color_picker_string)
        # Check Label
        self.action_label_edit.setCheckable( True )
        self.action_label_edit.setChecked( self.view.mode_label )
        # Check Edit
        self.action_edit_grey.setCheckable( True )
        self.action_edit_grey.setChecked( self.ctx_pin_egs )
        self.action_edit_flip_h.setCheckable( True )
        self.action_edit_flip_h.setChecked( self.ctx_pin_efx )
        self.action_edit_flip_v.setCheckable( True )
        self.action_edit_flip_v.setChecked( self.ctx_pin_efy )
        # Check Color Picker
        self.action_color_picker.setCheckable( True )
        self.action_color_picker.setChecked( self.view.mode_pickcolor )


        # Disable General (on nothing loaded)
        self.action_insert_pin.setEnabled(self.view.isEnabled())
        self.action_board_fit.setEnabled(self.view.isEnabled())

        # Disable Menus (on nothing loaded)
        self.menu_label.setEnabled(self.view.isEnabled())
        self.menu_color.setEnabled(self.view.isEnabled())
        self.menu_insert.setEnabled(self.view.isEnabled())


        # Disable Pin
        self.menu_pin.setEnabled( self.ctx_pin_tipo == "image" )
        # Disable Pack
        self.menu_pack.setEnabled( not self.view.select_count == 0 )
        # Disable Reset
        self.menu_reset.setEnabled( not self.view.pin_index == None )
        # Disable Edit
        self.menu_edit.setEnabled( not self.view.pin_index == None )
        # Disable Color
        self.action_color_analyse.setEnabled( not ( self.view.pin_index == None or self.view.pigment_o == None ) )
        # Disable Insert
        self.action_insert_document.setEnabled( not self.view.pin_index == None )
        self.action_insert_layer.setEnabled( not (self.view.pin_index == None or self.state_insert == False) )
        self.action_insert_reference.setEnabled( not (self.view.pin_index == None or self.state_insert == False) )
        # Disable Relative
        self.action_rebase.setEnabled( not self.view.pin_index == None )
        self.action_delete.setEnabled( not self.view.pin_index == None )

    def Items_Create(self):

        if self.context_menu_mode == False:
            edit_menu = self.addMenu("Edit")
            view_source = edit_menu
        else:
            view_source = self

        # General
        self.action_board_fit = view_source.addAction( "Board Fit" )
        self.action_insert_pin = view_source.addAction( "Insert Pin" )
        view_source.addSeparator()

        # Label
        self.menu_label = view_source.addMenu( "Label" )
        self.action_label_create = self.menu_label.addAction( "Create" )
        self.action_label_edit = self.menu_label.addAction( "Edit" )

        # Pin
        self.menu_pin = view_source.addMenu( "Pin" )
        self.action_pin_location = self.menu_pin.addAction( "File Location" )
        self.action_pin_copy     = self.menu_pin.addAction( "Copy Path" )
        self.action_pin_save     = self.menu_pin.addAction( "Save To" )

        # Packer
        self.menu_pack = view_source.addMenu( self.menu_pack_string )
        self.action_pack_grid      = self.menu_pack.addAction( "Linear Grid" )
        self.action_pack_row       = self.menu_pack.addAction( "Linear Row" )
        self.action_pack_column    = self.menu_pack.addAction( "Linear Column" )
        self.action_pack_pile      = self.menu_pack.addAction( "Linear Pile" )
        self.action_pack_area      = self.menu_pack.addAction( "Optimal Area" )
        self.action_pack_perimeter = self.menu_pack.addAction( "Optimal Perimeter" )
        self.action_pack_ratio     = self.menu_pack.addAction( "Optimal Ratio" )
        self.action_pack_class     = self.menu_pack.addAction( "Optimal Class" )

        # Reset
        self.menu_reset = view_source.addMenu( "Reset" )
        self.action_reset_rotation  = self.menu_reset.addAction( "Rotation" )
        self.action_reset_scale     = self.menu_reset.addAction( "Scale" )

        # Edit
        self.menu_edit = view_source.addMenu( "Edit" )
        self.action_edit_grey   = self.menu_edit.addAction( "View Greyscale" )
        self.action_edit_flip_h = self.menu_edit.addAction( "Flip Horizontal" )
        self.action_edit_flip_v = self.menu_edit.addAction( "Flip Vertical" )
        self.action_edit_reset  = self.menu_edit.addAction( "Reset" )

        # Color
        self.menu_color = view_source.addMenu( "Color" )
        self.action_color_picker  = self.menu_color.addAction( self.action_color_picker_string )
        self.action_color_analyse = self.menu_color.addAction( "Analyse" )

        # Insert
        self.menu_insert = view_source.addMenu( "Insert ")
        self.action_insert_document  = self.menu_insert.addAction( "Document" )
        self.action_insert_layer     = self.menu_insert.addAction( "Layer" )
        self.action_insert_reference = self.menu_insert.addAction( "Reference" )
        view_source.addSeparator()



        # Context
        self.action_rebase = view_source.addAction( "Rebase" )
        self.action_delete = view_source.addAction( "Delete" )

    def Items_Connect(self):
        if self.context_menu_mode: return

        actions: list[QAction] = [
            # General
            self.action_board_fit,
            self.action_insert_pin, 

            # Label
            self.action_label_create,
            self.action_label_edit,

            # Pin
            self.action_pin_location,
            self.action_pin_copy,
            self.action_pin_save,    

            # Packer
            self.action_pack_grid,      
            self.action_pack_row,       
            self.action_pack_column,
            self.action_pack_pile,
            self.action_pack_area,
            self.action_pack_perimeter,
            self.action_pack_ratio,
            self.action_pack_class,

            # Reset
            self.action_reset_rotation,
            self.action_reset_scale,

            # Edit
            self.action_edit_grey,
            self.action_edit_flip_h,
            self.action_edit_flip_v,
            self.action_edit_reset,

            # Color
            self.action_color_picker,
            self.action_color_analyse,

            # Insert
            self.action_insert_document,
            self.action_insert_layer,
            self.action_insert_reference,

            # Context
            self.action_rebase,
            self.action_delete,
        ]

        for action in actions:
            action.triggered.connect(self.Event_Trigger)


    def Event_Set(self, event: QMouseEvent):
        self.event_position = event.pos()

    def Event_Trigger( self ):
        sender = self.sender()
        if isinstance(sender, QAction): self.Event_Execute(sender)

    def Event_Execute( self, action: QAction | None ):
        view = self.view

        # General
        if action == self.action_board_fit:
            view.Board_Fit()
        if action == self.action_insert_pin:
            bx = self.event_position.x()
            by = self.event_position.y()
            view.Pin_URL( bx, by )

        # Label
        if action == self.action_label_create:
            view.Label_Insert( self.event_position )
        if action == self.action_label_edit:
            view.ModeSet_Label()
        # Pin
        if action == self.action_pin_location:
            view.SIGNAL_LOCATION.emit( self.ctx_pin_path )
        if action == self.action_pin_copy:
            NativeActions.Path_Copy( self.ctx_pin_path )
        if action == self.action_pin_save:
            view.SIGNAL_PIN_SAVE.emit( self.ctx_pin_qpixmap )

        # Pack Linear
        if action == self.action_pack_grid:
            view.Packer_Process( "GRID" )
        if action == self.action_pack_row:
            view.Packer_Process( "ROW" )
        if action == self.action_pack_column:
            view.Packer_Process( "COLUMN" )
        if action == self.action_pack_pile:
            view.Packer_Process( "PILE" )
        # Pack Optimal
        if action == self.action_pack_area:
            view.Packer_Process( "AREA" )
        if action == self.action_pack_perimeter:
            view.Packer_Process( "PERIMETER" )
        if action == self.action_pack_ratio:
            view.Packer_Process( "RATIO" )
        if action == self.action_pack_class:
            view.Packer_Process( "CLASS" )

        # Reset
        if action == self.action_reset_rotation:
            view.Reset_Rotation( self.ctx_relative )
        if action == self.action_reset_scale:
            view.Reset_Scale( self.ctx_relative )

        # Edit
        if action == self.action_edit_grey:
            pin_egs = not pin_egs
            view.Edit_Pin( pin_egs, pin_efx, pin_efy )
        if action == self.action_edit_flip_h:
            pin_efx = not pin_efx
            view.Edit_Pin( pin_egs, pin_efx, pin_efy )
        if action == self.action_edit_flip_v:
            pin_efy = not pin_efy
            view.Edit_Pin( pin_egs, pin_efx, pin_efy )
        if action == self.action_edit_reset:
            view.Edit_Pin( False, False, False )

        # Color
        if action == self.action_color_picker:
            view.ModeSet_ColorPicker()
        if action == self.action_color_analyse:
            qimage = self.ctx_pin_qpixmap.toImage()
            view.SIGNAL_ANALYSE.emit( qimage )

        # Insert
        if action == self.action_insert_document:
            view.SIGNAL_NEW_DOCUMENT.emit( self.ctx_pin_path, self.ctx_clip )
        if action == self.action_insert_layer:
            view.SIGNAL_INSERT_LAYER.emit( self.ctx_pin_path, self.ctx_clip )
        if action == self.action_insert_reference:
            view.SIGNAL_INSERT_REFERENCE.emit( self.ctx_pin_path, self.ctx_clip )


        # Relative
        if action == self.action_rebase:
            view.Relative_Rebase( self.ctx_relative )
        if action == self.action_delete:
            view.Relative_Delete( self.ctx_relative )

    @staticmethod
    def OpenContextMenu( view: "ReferenceView", event: QMouseEvent ):
        QApplication.restoreOverrideCursor()
        qmenu = ContextMenu(view, view, True)
        qmenu.Event_Set(event)
        action = qmenu.exec_( view.mapToGlobal( event.pos() ) )
        qmenu.Event_Execute(action)
        qmenu.deleteLater()
