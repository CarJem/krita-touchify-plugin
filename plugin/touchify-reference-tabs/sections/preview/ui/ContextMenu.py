from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import TYPE_CHECKING
from ....DockerMenu import DockerMenu
from ....dataclasses.images import ImageClip, InsertablePin
from ....extensions.native_actions import NativeActions
if TYPE_CHECKING:
    from ..PreviewView import PreviewView

class ContextMenu(DockerMenu):
    def __init__(self, section: "PreviewView", parent: QWidget | None = None, is_context_menu: bool = False):
        super().__init__("Preview Context", parent)
        self.view = section
        self.context_menu_mode = is_context_menu

        self.Variables()
        self.Items_Create()
        self.Items_Update()
        self.Items_Connect()

    def Variables(self):
        self.clip = ImageClip(self.view.state_clip,self.view.cl,self.view.ct,self.view.cw,self.view.ch)

        self.string_pickcolor = "Picker"
        if self.view.ColorPicker.pigment_o == None:
            self.string_pickcolor += " [RGB]"
        
        if self.view.state_clip == True:
            self.string_clip = " (Clip)"
        else:
            self.string_clip = ""

    def Update(self):
        self.Variables()
        self.Items_Update()

    def Items_Update(self):
        state_null = self.view.preview_qpixmap == None
        state_insert = NativeActions.Insert_Check( )
        state_animation = self.view.state_animation
        state_compact = self.view.state_compact
        state_vector = self.view.state_vector
        path_none = self.view.preview_path == None

        self.action_clip.setCheckable( True )
        self.action_clip.setChecked( self.view.state_clip )
        # Check Information
        self.action_file_information.setCheckable( True )
        self.action_file_information.setChecked( self.view.state_information )
        # Check Edit
        self.action_edit_greyscale.setCheckable( True )
        self.action_edit_greyscale.setChecked( self.view.edit_greyscale )
        self.action_edit_invert_h.setCheckable( True )
        self.action_edit_invert_h.setChecked( self.view.edit_invert_h )
        self.action_edit_invert_v.setCheckable( True )
        self.action_edit_invert_v.setChecked( self.view.edit_invert_v )
        # Check Color
        self.action_pick_color.setCheckable( True )
        self.action_pick_color.setChecked( self.view.state_pickcolor )

        # Disable General
        self.action_pin.setEnabled( not (state_null == True) )
        self.action_random.setEnabled(state_null == False and (state_animation == True or state_compact == True) )
        # Disable Clip
        self.action_clip.setEnabled( not (state_null == True or state_vector == True or path_none == True) )
        # Disable File
        self.menu_file.setEnabled( not (state_null == True or path_none == True) )
        # Disable Animation
        self.menu_anim.setEnabled( not (state_null == True or state_animation == False or path_none == True) )
        # Disable Compact
        self.menu_comp.setEnabled( not (state_null == True or state_compact == False or path_none == True) )
        # Disable Edit
        self.menu_edit.setEnabled( not(state_null == True or state_animation == True or path_none == True) )
        # Disable Color
        self.menu_color.setEnabled( not (state_null == True) )
        self.action_analyse.setEnabled( not(state_null == True or self.view.ColorPicker.pigment_o == None) )
        # Disable Insert
        self.menu_insert.setEnabled( not (state_null == True or path_none == True or state_compact == True) )
        self.action_insert_layer.setEnabled( not(state_insert == False) )
        self.action_insert_ref.setEnabled( not(state_insert == False) )

        self.action_pin.setText("Pin Reference" + self.string_clip)
        self.action_pick_color.setText( self.string_pickcolor )
        self.action_analyse.setText("Analyse" + self.string_clip )
        self.action_document.setText( "Document" + self.string_clip )
        self.action_insert_layer.setText( "Layer" + self.string_clip )
        self.action_insert_ref.setText( "Reference" + self.string_clip )

    def Items_Create(self):

        if self.context_menu_mode == False:
            edit_menu = self.addMenu("Edit")
            qmenu = edit_menu
        else:
            qmenu = self

        # General
        self.action_pin = qmenu.addAction( "Pin Reference" + self.string_clip )
        self.action_random = qmenu.addAction( "Random Index" )
        self.action_clip = qmenu.addAction( "Clip Image" )
        qmenu.addSeparator()
        # File
        self.menu_file = qmenu.addMenu( "File" )
        self.action_file_location = self.menu_file.addAction( "File Location" )
        self.action_file_copy = self.menu_file.addAction( "Copy Path" )
        self.action_file_information = self.menu_file.addAction( "Information" )
        # Animation
        self.menu_anim = qmenu.addMenu( "Animation" )
        self.action_anim_export_one = self.menu_anim.addAction( "Export One Frame" )
        self.action_anim_export_all = self.menu_anim.addAction( "Export All Frames" )
        # Compact
        self.menu_comp = qmenu.addMenu( "Compressed" )
        self.action_comp_export_one = self.menu_comp.addAction( "Export One" )
        # Edit
        self.menu_edit = qmenu.addMenu( "Edit" )
        self.action_edit_greyscale = self.menu_edit.addAction( "View Greyscale" )
        self.action_edit_invert_h = self.menu_edit.addAction( "Flip Horizontal" )
        self.action_edit_invert_v = self.menu_edit.addAction( "Flip Vertical" )
        self.action_edit_reset = self.menu_edit.addAction( "Reset" )
        # Color
        self.menu_color = qmenu.addMenu( "Color" )
        self.action_pick_color = self.menu_color.addAction( self.string_pickcolor )
        self.action_analyse = self.menu_color.addAction( "Analyse" + self.string_clip )
        # Insert
        self.menu_insert = qmenu.addMenu( "Insert" )
        self.action_document = self.menu_insert.addAction( "Document" + self.string_clip )
        self.action_insert_layer = self.menu_insert.addAction( "Layer" + self.string_clip )
        self.action_insert_ref = self.menu_insert.addAction( "Reference" + self.string_clip )

    def Items_Connect(self):
        if self.context_menu_mode: return

        actions: list[QAction] = [
            # General
            self.action_pin,
            self.action_random,
            self.action_clip,
            # File
            self.action_file_location,
            self.action_file_copy,
            self.action_file_information,
            # Animation
            self.action_anim_export_one,
            self.action_anim_export_all,
            # Compact
            self.action_comp_export_one,
            # Edit
            self.action_edit_greyscale,
            self.action_edit_invert_h,
            self.action_edit_invert_v,
            self.action_edit_reset,
            # Color
            self.action_pick_color,
            self.action_analyse,
            # Insert
            self.action_document,
            self.action_insert_layer,
            self.action_insert_ref,
        ]

        for action in actions:
            action.triggered.connect(self.Event_Trigger)


    def Event_Set(self, event: QMouseEvent):
        self.event_position = event.pos()

    def Event_Trigger( self ):
        sender = self.sender()
        if isinstance(sender, QAction): self.Event_Execute(sender)

    def Event_Execute( self, action: QAction | None ):

        # General
        if action == self.action_pin:
            pin = InsertablePin(self.view.w2, self.view.h2, self.view.preview_path)
            self.view.SIGNAL_PIN_IMAGE.emit( pin, self.clip )
        if action == self.action_random:
            self.view.SIGNAL_RANDOM.emit()
        if action == self.action_clip:
            self.view.state_clip = not self.view.state_clip

        # File
        if action == self.action_file_location:
            NativeActions.File_Location( self.view.preview_path )
        if action == self.action_file_copy:
            NativeActions.Path_Copy( self.view.preview_path )
        if action == self.action_file_information:
            self.view.state_information = not self.view.state_information

        # Animation
        if action == self.action_anim_export_one:
            self.view.Anim_Export_Index( self.view.anim_frame )
        if action == self.action_anim_export_all:
            self.view.Anim_Export_Cycle()

        # Compressed
        if action == self.action_comp_export_one:
            self.view.Comp_Export_Index( self.view.comp_index )

        # Edit
        if action == self.action_edit_greyscale:
            self.view.Edit_Display( "egs" )
        if action == self.action_edit_invert_h:
            self.view.Edit_Display( "efx" )
        if action == self.action_edit_invert_v:
            self.view.Edit_Display( "efy" )
        if action == self.action_edit_reset:
            self.view.Edit_Display( None )

        # Color
        if action == self.action_pick_color:
            self.view.Toggle_ColorPicker()
        if action == self.action_analyse:
            qpixmap = self.view.Draw_Clip( self.view.preview_qpixmap )
            qimage = qpixmap.toImage()
            self.view.ColorPicker.Analyse(qimage)

        # Insert
        if action == self.action_document:
            NativeActions.Insert_Document(self.view.preview_path, self.clip)     
        if action == self.action_insert_layer:
            NativeActions.Insert_Layer(self.view.preview_path, self.clip)     
        if action == self.action_insert_ref:
            NativeActions.Insert_Reference(self.view.preview_path, self.clip)     


    @staticmethod
    def OpenContextMenu( view: "PreviewView", event: QMouseEvent ):
        QApplication.restoreOverrideCursor()
        qmenu = ContextMenu(view, view, True)
        qmenu.Event_Set(event)
        action = qmenu.exec_( view.mapToGlobal( event.pos() ) )
        qmenu.Event_Execute(action)
        qmenu.deleteLater()
