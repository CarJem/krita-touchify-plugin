import os
import pathlib
import time
import zipfile
from krita import *
from PyQt5 import QtCore, QtGui
from ...extensions.calculations import *
from ...extensions.color_picker import *
from ...extensions.commons import Commons
from ...dataclasses.images import ImageClip, InsertablePin
from ...extensions.native_actions import NativeActions
from ...extensions.paintables import Paintables
from .ui.ContextMenu import ContextMenu
from ...extensions.filetypes import REFERENCE_FILETYPE_DATA

class PreviewView( QWidget ):

    # Preview
    SIGNAL_RETURN_REQUESTED = QtCore.pyqtSignal()
    SIGNAL_INCREMENT = QtCore.pyqtSignal( int )
    # Menu
    SIGNAL_FUNCTION = QtCore.pyqtSignal( list )
    SIGNAL_PIN_IMAGE = QtCore.pyqtSignal( [ InsertablePin, ImageClip ] )
    SIGNAL_RANDOM = QtCore.pyqtSignal()
    # UI
    SIGNAL_EXTRA_LABEL = QtCore.pyqtSignal( str )
    SIGNAL_EXTRA_PANEL = QtCore.pyqtSignal( bool )
    SIGNAL_EXTRA_VALUE = QtCore.pyqtSignal( int )
    SIGNAL_EXTRA_MAX = QtCore.pyqtSignal( int )
    SIGNAL_ZOOM_UPDATED = QtCore.pyqtSignal( float )


    # Init
    def __init__( self, parent ):
        super( PreviewView, self ).__init__( parent )
        self.Variables()
    
    def Variables( self ):
        # Widget
        self.ww = 1
        self.hh = 1
        self.w2 = 0.5
        self.h2 = 0.5

        # Event
        self.ox = 0
        self.oy = 0
        self.ex = 0
        self.ey = 0

        # Display
        self.preview_path = None
        self.preview_qpixmap = None
        self.scale_method = Qt.TransformationMode.FastTransformation

        # Compact
        self.file_search = []

        # State
        self.state_press = False
        self.state_pickcolor = False
        self.state_clip = False
        self.state_animation = False
        self.state_compact = False
        self.state_information = False
        self.state_vector = False
        # Interaction
        self.operation = None
        # Camera
        self.pcmx = 0
        self.pcmy = 0
        self.pcz = 1
        self.cmx = 0 # Moxe X
        self.cmy = 0 # Move Y
        self.cz = 1 # Zoom
        self.display = False

        # Colors
        self.color_1 = QColor( "#ffffff" )
        self.color_2 = QColor( "#000000" )
        self.color_alpha = QColor( 0, 0, 0, 50 )
        self.color_clip = QColor( 0, 0, 0, 100 )

        # Edit
        self.edit_greyscale = False
        self.edit_invert_h = False
        self.edit_invert_v = False

        # Color Picker
        self.ColorPicker = ColorPicker(self)

        # Bounding Box
        self.bl = 0
        self.bt = 0
        self.br = 0
        self.bb = 0
        self.bw = self.br - self.bl
        self.bh = self.bb - self.bt

        # Clip
        self.clip_node = None
        self.cl = 0.1  # 0-1
        self.ct = 0.1  # 0-1
        self.cr = 0.9  # 0-1
        self.cb = 0.9  # 0-1
        self.cw = self.cr - self.cl  # 0-1
        self.ch = self.cb - self.ct  # 0-1

        # Drag and Drop
        self.setAcceptDrops( True )
        self.drop = False
        self.drag = False

        # Animation
        self.anim_sequence = []
        self.anim_frame = 0
        self.anim_count = 0
        self.anim_rate = 33
        self.Anim_Timer()

        # Compact
        self.comp_path = []
        self.comp_sequence = []
        self.comp_index = 0
        self.comp_count = 0

    #region Widget Overrides

    def sizeHint( self ):
        return QtCore.QSize( 5000,5000 )

    #endregion
    
    #region Relay

    def Set_FileSearch( self, file_search ):
        self.file_search = file_search

    def Set_Theme( self, color_1, color_2 ):
        self.color_1 = color_1
        self.color_2 = color_2

    def Set_Size( self, ww, hh ):
        self.ww = ww
        self.hh = hh
        self.w2 = ww * 0.5
        self.h2 = hh * 0.5
        self.resize( ww, hh )
        self.ColorPicker.setSourceSize(ww, hh)

    def Set_Scale_Method( self, scale_method ):
        self.scale_method = scale_method
        self.update()

    def Set_Display( self, boolean ):
        self.display = boolean
        self.update()
    
    #endregion

    #region Display
    def Display_Reset( self, state ):
        # Variables
        if state == True:
            self.state_animation = False
            self.state_compact = False
        # Functions
        self.Camera_Reset()
        self.Clip_Reset()
        self.Edit_Reset()
        self.Anim_Pause()
    
    def Display_Default( self ):
        self.Display_Reset( True )
        self.preview_path = None
        self.preview_qpixmap = None
        self.update()
        self.Camera_Grab()

    def Display_Path(self, image_path: str):
        def File_Extension( path ):
            if path == None:
                extension = None
            else:
                extension = pathlib.Path( path ).suffix
                extension = extension.replace( ".", "" )
            return extension
        
        file_anima = REFERENCE_FILETYPE_DATA["file_anima"]
        file_compact = REFERENCE_FILETYPE_DATA["file_compact"]

        extension = File_Extension( image_path )

        if extension in file_anima:
            self.view.Display_Animation( image_path )

        elif extension in file_compact:
            self.Display_Compact( image_path )
        else:
            self.Display_Static( image_path )

    def Display_Static( self, image_path: str ):
        qpixmap = QPixmap( image_path )
        if qpixmap.isNull() == False:
            if self.preview_path != image_path:
                self.Display_Reset( True )
                self.Check_Vector( image_path )
            self.preview_qpixmap = qpixmap
        else:
            self.preview_qpixmap = True
        self.preview_path = image_path
        self.update()
        self.Camera_Grab()

    def Display_Internet(self, url: str):
        qpixmap = Commons.Download_QPixmap( url )
        if qpixmap: self.Display_QPixmap(qpixmap)

    def Display_QPixmap( self, qpixmap ):
        if qpixmap.isNull() == False:
            self.Display_Reset( True )
            self.preview_path = None
            self.preview_qpixmap = qpixmap
            self.update()
            self.Camera_Grab()
        else:
            self.Display_Default()
    
    def Display_Animation( self, image_path ):
        qmovie = QMovie( image_path )
        if qmovie.isValid() == True:
            # Variables
            if self.preview_path != image_path:
                self.Display_Reset( True )
            self.preview_path = image_path
            # Frames
            frames = qmovie.frameCount()
            speed = qmovie.speed() / 100
            if frames == 1:
                self.Display_Static( image_path )
            else:
                # Variables
                self.state_animation = True
                self.anim_frame = 0
                # Frames
                rate = []
                sequence = []
                for i in range( 0, frames ):
                    qmovie.jumpToFrame( i )
                    delay = qmovie.nextFrameDelay()
                    rate.append( delay )
                    qpixmap = qmovie.currentPixmap()
                    if qpixmap.isNull() == False:
                        sequence.append( qpixmap )
                mean = Stat_Mean( rate )
                # Variables
                self.anim_sequence = sequence
                self.anim_count = len( sequence ) - 1
                self.anim_rate = int( mean * speed )
                # Animation
                self.Anim_Play()
                # UI
                self.SIGNAL_EXTRA_PANEL.emit( True )
                self.SIGNAL_EXTRA_MAX.emit( frames - 1 )
                self.SIGNAL_EXTRA_VALUE.emit( 0 )
                # Garbage
                del qmovie
            self.update()
        else:
            self.Display_Static( image_path )
    
    def Display_Compact( self, zip_path ):
        # Variables
        self.comp_path = []
        self.comp_sequence = []
        self.comp_index = 0
        # Open Zip File
        self.Display_Reset( True )
        if zipfile.is_zipfile( zip_path ):
            # Variables
            self.state_compact = True
            self.preview_path = zip_path
            # Archive
            self.comp_archive = zipfile.ZipFile( zip_path, "r" )
            name_list = self.comp_archive.namelist()
            for name in name_list:
                try:
                    if name.split( "." )[1] in self.file_search:
                        self.comp_path.append( name )
                except:
                    pass
        # Display
        if len( self.comp_path ) > 0:
            # Variables
            self.preview_qpixmap = self.Comp_Read( self.comp_archive, self.comp_path[self.comp_index] )
            self.comp_count = len( self.comp_path ) - 1
            # UI
            self.SIGNAL_EXTRA_PANEL.emit( True )
            self.SIGNAL_EXTRA_MAX.emit( self.comp_count )
            self.SIGNAL_EXTRA_VALUE.emit( 0 )
            self.Extra_Label( True )
            # Update
            self.update()
            self.Camera_Grab()
        else:
            self.Display_Static( zip_path )
    # endregion
 
    #region Draw
    def Draw_Render( self, qpixmap ):
        # QPixmap
        if self.display == False:
            draw = qpixmap.scaled( int( self.ww * self.cz ), int( self.hh * self.cz ), Qt.KeepAspectRatio, self.scale_method )
        else:
            ww = qpixmap.width()
            hh = qpixmap.height()
            draw = qpixmap.scaled( int( ww * self.cz ), int( hh * self.cz ), Qt.KeepAspectRatio, self.scale_method )
        self.bw = draw.width()
        self.bh = draw.height()
        # Variables
        self.bl = self.w2 - ( self.bw * 0.5 ) + ( self.cmx * self.cz )
        self.bt = self.h2 - ( self.bh * 0.5 ) + ( self.cmy * self.cz )
        self.br = self.bl + self.bw
        self.bb = self.bt + self.bh
        # Return
        return draw
    
    def Draw_Clip( self, qpixmap ):
        if self.state_clip == True:
            w = self.preview_qpixmap.width()
            h = self.preview_qpixmap.height()
            qpixmap = qpixmap.copy( int( w * self.cl ), int( h * self.ct ), int( w * self.cw ), int( h * self.ch ) )
        return qpixmap
    #endregion

    #region Animation
    def Anim_Timer( self ):
        self.anim_timer = QtCore.QTimer( self )
        self.anim_timer.timeout.connect( lambda: self.Anim_Increment( +1 ) )
        self.anim_timer.stop()
    
    def Anim_Increment( self, increment ):
        if self.state_animation == True:
            self.anim_frame = Limit_Loop( int( self.anim_frame + increment ), self.anim_count )
            self.preview_qpixmap = self.anim_sequence[ self.anim_frame ]
            self.SIGNAL_EXTRA_VALUE.emit( self.anim_frame )
            self.update()
    
    def Anim_Play( self ):
        if self.state_animation == True:
            self.anim_timer.start( self.anim_rate )
            self.Extra_Label( False )
    
    def Anim_Pause( self ):
        self.anim_timer.stop()
        self.Extra_Label( True )
    
    def Anim_Back( self ):
        if ( self.state_animation == True and self.anim_timer.isActive() == False ):
            self.Anim_Increment( -1 )
            self.Extra_Label( True )
    
    def Anim_Forward( self ):
        if ( self.state_animation == True and self.anim_timer.isActive() == False ):
            self.Anim_Increment( +1 )
            self.Extra_Label( True )
    
    def Anim_Frame( self, frame ):
        if self.state_animation == True:
            self.anim_frame = Limit_Loop( int( frame ), self.anim_count )
            self.preview_qpixmap = self.anim_sequence[ self.anim_frame ]
            if self.anim_timer.isActive() == False:
                self.Extra_Label( True )
                self.update()
    
    def Anim_Export_Cycle( self ):
        if self.state_animation == True:
            for i in range( 0, len( self.anim_sequence ) ):
                self.Anim_Export_Index( i )
    
    def Anim_Export_Index( self, index ):
        if self.state_animation == True:
            # Construct New Path
            path = os.path.split( self.preview_path )
            directory = path[0]
            split = os.path.splitext( path[1] )
            name = split[0]
            extension = split[1]

            # Variables
            name_new = f"{ name }_{ str( index ).zfill( 4 ) }.png"
            save_path = os.path.join( directory, name_new )
            exists = os.path.exists( save_path )
            if exists == False:
                screenshot_qpixmap = self.anim_sequence[ index ]
                screenshot_qpixmap.save( save_path )
                # Logger
                try:QtCore.qDebug( f"Imagine Board | SCREENSHOT { index }:{ self.frame_count }" )
                except:pass
                # Garbage
                del screenshot_qpixmap
    #endregion

    #region Compact
    def Comp_Read( self, archive, name ):
        if self.state_compact == True:
            try:
                extract = archive.open( name )
                data = extract.read()
                qpixmap = QPixmap()
                qpixmap.loadFromData( data )
            except:
                qpixmap = None
            return qpixmap
    
    def Comp_Increment( self, increment ):
        if self.state_compact == True:
            # Preparation
            self.Display_Reset( False )
            # Index
            comp_index = Limit_Range( self.comp_index + increment, 0, self.comp_count )
            if self.comp_index != comp_index:
                self.comp_index = comp_index
                self.preview_qpixmap = self.Comp_Read( self.comp_archive, self.comp_path[self.comp_index] )
    	    # Signals
            self.SIGNAL_EXTRA_VALUE.emit( self.comp_index )
            self.update()
            self.Camera_Grab()
    
    def Comp_Back( self ):
        if self.state_compact == True:
            self.Comp_Increment( -1 )
            self.Extra_Label( True )
    
    def Comp_Forward( self ):
        if self.state_compact == True:
            self.Comp_Increment( +1 )
            self.Extra_Label( True )
    
    def Comp_Index( self, index ):
        if self.state_compact == True:
            if self.comp_index != index:
                self.Display_Reset( False )
                self.comp_index = Limit_Range( index, 0, self.comp_count )
                self.preview_qpixmap = self.Comp_Read( self.comp_archive, self.comp_path[self.comp_index] )
                self.Extra_Label( True )
            self.update()
            self.Camera_Grab()
    
    def Comp_Export_Index( self, index ):
        if self.state_compact == True:
            # File Path
            file_directory = os.path.dirname( self.preview_path )
            file_basename = os.path.basename( self.preview_path )
            file_name = os.path.splitext( file_basename )[0]
            # Zip Path
            zip_namelist = self.comp_path[self.comp_index]
            zip_basename = os.path.basename( os.path.abspath( zip_namelist ))
            # Formating
            file_name    = file_name.replace( " ", "_" )
            zip_basename = zip_basename.replace( " ", "_" )
            join_name = f"{ file_name }_{ zip_basename }"
            save_location = os.path.join( file_directory, join_name )
            # Image Save
            qpixmap = self.Comp_Read( self.comp_archive, zip_namelist )
            exists = os.path.exists( save_location )
            if exists == False and qpixmap.isNull() == False:
                qpixmap.save( save_location )
            else:
                string = f"Imagine Board | ERROR zip file not saved"
                #QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( string ) )
    #endregion

    #region Camera
    def Camera_Reset( self ):
        self.cmx = 0
        self.cmy = 0
        self.cz = 1
        self.SIGNAL_ZOOM_UPDATED.emit(self.cz)
    
    def Camera_Previous( self ):
        self.pcmx = self.cmx
        self.pcmy = self.cmy
        self.pcz = self.cz
    
    def Camera_Move( self, ex, ey ):
        if self.cz != 0:
            self.cmx = self.pcmx + ( ( ex - self.ox ) / self.cz )
            self.cmy = self.pcmy + ( ( ey - self.oy ) / self.cz )
    
    def Camera_Scale( self, ex, ey ):
        factor = 200
        self.cz = Limit_Range( self.pcz - ( ( ey - self.oy ) / factor ), 0, 100 )
        self.SIGNAL_ZOOM_UPDATED.emit(self.cz)
    
    def Camera_Grab( self ):
        try:self.qimage_grab = self.grab().toImage()
        except:pass
    
    def Camera_Zoom(self, value: int, incremental: bool = True):
        self.Camera_Previous()
        if incremental:
            zoom_amount = value * 10
            factor = 200
            self.cz = Limit_Range( self.pcz - (zoom_amount / factor), 0, 100 )
        else:
            self.cz = Limit_Range( value, 0, 100 )
        self.update()
        self.SIGNAL_ZOOM_UPDATED.emit(self.cz)

    #endregion

    #region Pagination
    def Pagination_Reset( self, ex, ey ):
        self.ox = ex
        self.oy = ey
    
    def Pagination_Stylus( self, ex, ey ):
        factor = 20
        dx = ex - self.ox
        dy = ey - self.oy
        if dx >= factor:
            self.SIGNAL_INCREMENT.emit( +1 )
            self.Pagination_Reset( ex, ey )
        if dx <= -factor:
            self.SIGNAL_INCREMENT.emit( -1 )
            self.Pagination_Reset( ex, ey )
        if dy >= factor:
            self.SIGNAL_INCREMENT.emit( -1 )
            self.Pagination_Reset( ex, ey )
        if dy <= -factor:
            self.SIGNAL_INCREMENT.emit( +1 )
            self.Pagination_Reset( ex, ey )
    #endregion

    #region Clip
    def Clip_Reset( self ):
        self.state_clip = False
        self.cl = 0.1
        self.ct = 0.1
        self.cr = 0.9
        self.cb = 0.9
        self.cw = self.cr - self.cl
        self.ch = self.cb - self.ct
    
    def Clip_Node( self, ex, ey ):
        # Nodes
        n1 = [ self.bl + self.bw * self.cl, self.bt + self.bh * self.ct ]
        n2 = [ self.bl + self.bw * self.cr, self.bt + self.bh * self.ct ]
        n3 = [ self.bl + self.bw * self.cl, self.bt + self.bh * self.cb ]
        n4 = [ self.bl + self.bw * self.cr, self.bt + self.bh * self.cb ]

        # Distance
        d1 = Trig_2D_Points_Distance( ex, ey, n1[0], n1[1] )
        d2 = Trig_2D_Points_Distance( ex, ey, n2[0], n2[1] )
        d3 = Trig_2D_Points_Distance( ex, ey, n3[0], n3[1] )
        d4 = Trig_2D_Points_Distance( ex, ey, n4[0], n4[1] )
        # Sort
        dist = [ [ d1, 1 ], [ d2, 2 ], [ d3, 3 ], [ d4, 4 ] ]
        dist.sort()
        factor = 20
        if dist[0][0] <= factor:
            self.clip_node = dist[0][1]
        else:
            self.clip_node = None
    
    def Clip_Edit( self, ex, ey, node ):
        if node != None:
            lx = ( Limit_Range( ex, self.bl, self.br ) - self.bl ) / self.bw
            ly = ( Limit_Range( ey, self.bt, self.bb ) - self.bt ) / self.bh
            if node == 1:
                if lx != self.cr:self.cl = lx
                if ly != self.cb:self.ct = ly
            if node == 2:
                if lx != self.cl:self.cr = lx
                if ly != self.cb:self.ct = ly
            if node == 3:
                if lx != self.cr:self.cl = lx
                if ly != self.ct:self.cb = ly
            if node == 4:
                if lx != self.cl:self.cr = lx
                if ly != self.ct:self.cb = ly
    
    def Clip_Flip( self ):
        if self.cr < self.cl:
            self.cl, self.cr = self.cr, self.cl
        if self.cb < self.ct:
            self.ct, self.cb = self.cb, self.ct
        self.cw = self.cr - self.cl
        self.ch = self.cb - self.ct
    #endregion

    #region Misc

    def Extra_Label( self, mode ):
        string = ""
        if ( self.state_animation == True and mode == True ) == True:
            string = f"{ self.anim_frame }:{ self.anim_count }"
        if ( self.state_compact == True and mode == True and len( self.comp_path ) > 0 ) == True:
            string = f"{ self.comp_path[self.comp_index] }"
        self.SIGNAL_EXTRA_LABEL.emit( string )

    def Check_Vector( self, path ):
        self.state_vector = os.path.splitext( path )[1] in [ ".svg", ".svgz" ]
    
    def Information_Display( self ):
        # Variables
        path = self.preview_path
        # Logic
        if path == None:
            text = "None"
        else:
            # String
            text = ""

            # Paths
            try:
                info_path = os.path.split( path )
                info_dir = info_path[0]
                basename = os.path.splitext( info_path[1] )
                info_name = basename[0]
                info_type = basename[1].replace( ".", "" )
                text += f"Directory : { info_dir }\n"
                text += f"Name : { info_name } [ { info_type.upper() } ]\n"
            except:
                pass

            # Time
            try:
                mod_time = os.path.getmtime( path )
                local_time = time.localtime( mod_time )
                info_time = time.strftime( f"%Y-%m[%b]-%d[%a] %H:%M:%S", local_time )
                text += f"Time : { info_time }\n"
            except:
                pass

            # Size
            try:
                b = os.path.getsize( path )
                kb = b / 1000
                mb = kb / 1000
                if kb >= 1 and kb < 1000:
                    info_size = kb
                    info_scale = "Kb"
                elif mb >= 1 and mb < 1000:
                    info_size = mb
                    info_scale = "Mb"
                else:
                    info_size = b
                    info_scale = "b"
                text += f"Size : { round( info_size, 3 ) } { info_scale }\n"
            except:
                pass

            # Dimensions
            try:
                info_width = self.preview_qpixmap.width()
                info_height = self.preview_qpixmap.height()
                text += f"Dimension : { info_width } x { info_height } px"
            except:
                pass
        # Return
        return text
    
    def Edit_Reset( self ):
        self.edit_greyscale = False
        self.edit_invert_h = False
        self.edit_invert_v = False
    
    def Edit_Display( self, operation ):
        # Operations Boolean Toggle
        if operation == "egs":
            self.edit_greyscale = not self.edit_greyscale
        if operation == "efx":
            self.edit_invert_h = not self.edit_invert_h
        if operation == "efy":
            self.edit_invert_v = not self.edit_invert_v
        if operation == None:
            self.Edit_Reset()

        # Read
        if ( self.state_animation == False and self.state_compact == False ):
            qimage = QImage( self.preview_path )
        elif self.state_animation == True:
            qpixmap = self.anim_sequence[self.anim_frame]
            qimage = qpixmap.toImage()
        elif self.state_compact == True:
            qpixmap = self.Comp_Read( self.comp_archive, self.comp_path[self.comp_index] )
            qimage = qpixmap.toImage()

        # Edit Image
        if self.edit_greyscale == True:
            qimage = qimage.convertToFormat( 24 )
        if ( self.edit_invert_h == True or self.edit_invert_v == True ):
            qimage = qimage.mirrored( self.edit_invert_h, self.edit_invert_v )
        self.preview_qpixmap = QPixmap().fromImage( qimage )
        # Update
        self.update()

    def Cursor_Icon( self ):
        if ( self.state_pickcolor == True and self.state_press == True ):
            QApplication.setOverrideCursor( Qt.CrossCursor )
        else:
            QApplication.restoreOverrideCursor()

    def Context_Menu( self, event ):
        self.state_press = False
        ContextMenu.OpenContextMenu(self, event)

    #endregion

    #region Events
    def mousePressEvent( self, event ):
        # Variable
        self.state_press = True

        # Event
        ex = event.x()
        ey = event.y()
        self.ox = ex
        self.oy = ey
        self.ex = ex
        self.ey = ey

        # Cursor
        self.Cursor_Icon( )

        # LMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            if self.state_pickcolor == True:
                self.operation = "color_picker"
                self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.state_pickcolor )
            elif self.state_clip == True:
                self.operation = "clip"
                self.Clip_Node( ex, ey )
            else:
                self.operation = "camera_move"
        if ( event.modifiers() == QtCore.Qt.ShiftModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "camera_move"
            self.Camera_Previous()
        if ( event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "pagination"
            self.Camera_Reset()
        if ( event.modifiers() == QtCore.Qt.AltModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "drag_drop"

        # MMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.MiddleButton ):
            self.operation = "camera_move"
            self.Camera_Previous()

        # RMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = None
            self.Context_Menu( event )
        if ( event.modifiers() == QtCore.Qt.ShiftModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = "camera_scale"
            self.Camera_Previous()
        if ( event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = "pagination"
            self.Camera_Reset()
        if ( event.modifiers() == QtCore.Qt.AltModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = "drag_drop"

        # Update
        self.update()
    
    def mouseMoveEvent( self, event ):
        # Event
        ex = event.x()
        ey = event.y()
        self.ex = ex
        self.ey = ey

        # Neutral
        if ( self.operation == "color_picker" and self.anim_timer.isActive() == False ):
            self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.state_pickcolor )
        if self.operation == "clip":
            self.Clip_Edit( ex, ey, self.clip_node )
        # Camera
        if self.operation == "camera_move":
            self.Camera_Move( ex, ey )
        if self.operation == "camera_scale":
            self.Camera_Scale( ex, ey )
        # Pagination
        if self.operation == "pagination":
            self.Pagination_Stylus( ex, ey )
        # Drag Drop
        if self.operation == "drag_drop":
            clip = ImageClip(self.state_clip, self.cl, self.ct, self.cw, self.ch)
            if self.preview_path != None:
                self.drag = True
                NativeActions.Drag_Drop(self, self.preview_path, clip)

        # Update
        self.update()
    
    def mouseDoubleClickEvent( self, event ):
        self.SIGNAL_RETURN_REQUESTED.emit( )
    
    def mouseReleaseEvent( self, event ):
        # Variables
        self.state_press = False
        self.operation = None
        self.drop = False
        self.drag = False
        # Function
        self.Clip_Flip()
        self.ColorPicker.Event( self.ex, self.ey, self.qimage_grab, self.state_press, self.state_pickcolor )
        self.Cursor_Icon( )
        # Update
        self.update()
        self.Camera_Grab()
    
    def wheelEvent( self, event ):
        delta_y = event.angleDelta().y()
        angle = 5
        if delta_y >= angle:
            self.SIGNAL_INCREMENT.emit( +1 )
            self.Camera_Zoom(-1)
        if delta_y <= -angle:
            self.SIGNAL_INCREMENT.emit( -1 )
            self.Camera_Zoom(+1)

    def dragEnterEvent( self, event ):
        if event.mimeData().hasImage:
            self.drop = True
            event.accept()
        else:
            event.ignore()
        self.update()
    
    def dragMoveEvent( self, event ):
        if event.mimeData().hasImage:
            self.drop = True
            event.accept()
        else:
            event.ignore()
        self.update()
    
    def dragLeaveEvent( self, event ):
        self.drop = False
        event.accept()
        self.update()
    
    def dropEvent( self, event ):
        if event.mimeData().hasImage:
            if ( self.drop == True and self.drag == False ):
                event.setDropAction( Qt.DropAction.CopyAction )
                mime_data = NativeActions.Drop_Inside( event )

                if len( mime_data ) > 0:
                    # Variables
                    item = mime_data[0]
                    # Check Source
                    check_html = Commons.Check_Html( item )
                    if check_html == True:
                        self.Display_Internet( item )
                    else:
                        # Checks
                        item = os.path.abspath( item )
                        check_dir = os.path.isdir( item )
                        check_file = os.path.isfile( item )

                        if item and check_file:
                            self.Display_Path(item)


            event.accept()
        else:
            event.ignore()
        self.drop = False
        self.drag = False
        self.update()
    
    def enterEvent( self, event ):
        self.Camera_Grab()
    
    def leaveEvent( self, event ):
        pass
    
    def paintEvent( self, event ):
        # Variables
        ww = self.ww
        hh = self.hh
        w2 = self.w2
        h2 = self.h2
        if ww < hh:
            side = ww
        else:
            side = hh

        # Painter
        painter = QPainter( self )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, True )

        # Background Hover
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( self.color_alpha ) )
        painter.drawRect( 0, 0, ww, hh )

        # Mask
        painter.setClipRect( QRect( int( 0 ), int( 0 ), int( ww ), int( hh ) ), Qt.ReplaceClip )

        # Render Image
        qpixmap = self.preview_qpixmap
        render = True
        if qpixmap in [ None, False, True ]:
            render = False
        if render == True:
            # Draw Pixmap
            draw = self.Draw_Render( qpixmap )
            painter.drawPixmap( int( self.bl ), int( self.bt ), draw )

            # Clip Area
            if self.state_clip == True:
                # Painter
                painter.setPen( QtCore.Qt.NoPen )
                painter.setBrush( QBrush( self.color_clip ) )
                # Path
                area = QPainterPath()
                area.moveTo( self.bl + 0,                 self.bt + 0 )
                area.lineTo( self.bl + self.bw,           self.bt + 0 )
                area.lineTo( self.bl + self.bw,           self.bt + self.bh )
                area.lineTo( self.bl + 0,                 self.bt + self.bh )
                area.moveTo( self.bl + self.bw * self.cl, self.bt + self.bh * self.ct )
                area.lineTo( self.bl + self.bw * self.cr, self.bt + self.bh * self.ct )
                area.lineTo( self.bl + self.bw * self.cr, self.bt + self.bh * self.cb )
                area.lineTo( self.bl + self.bw * self.cl, self.bt + self.bh * self.cb )
                painter.drawPath( area )
                # Points
                painter.setPen( QPen( self.color_2, 2, Qt.SolidLine ) )
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
                tri = 15
                poly1 = QPolygon( [
                    QPoint( int( self.bl + self.bw * self.cl ),       int( self.bt + self.bh * self.ct ) ),
                    QPoint( int( self.bl + self.bw * self.cl + tri ), int( self.bt + self.bh * self.ct ) ),
                    QPoint( int( self.bl + self.bw * self.cl ),       int( self.bt + self.bh * self.ct + tri ) ),
                    ] )
                poly2 = QPolygon( [
                    QPoint( int( self.bl + self.bw * self.cr ),       int( self.bt + self.bh * self.ct ) ),
                    QPoint( int( self.bl + self.bw * self.cr ),       int( self.bt + self.bh * self.ct + tri ) ),
                    QPoint( int( self.bl + self.bw * self.cr - tri ), int( self.bt + self.bh * self.ct ) ),
                    ] )
                poly3 = QPolygon( [
                    QPoint( int( self.bl + self.bw * self.cr ),       int( self.bt + self.bh * self.cb ) ),
                    QPoint( int( self.bl + self.bw * self.cr - tri ), int( self.bt + self.bh * self.cb ) ),
                    QPoint( int( self.bl + self.bw * self.cr ),       int( self.bt + self.bh * self.cb - tri ) ),
                    ] )
                poly4 = QPolygon( [
                    QPoint( int( self.bl + self.bw * self.cl ),       int( self.bt + self.bh * self.cb ) ),
                    QPoint( int( self.bl + self.bw * self.cl ),       int( self.bt + self.bh * self.cb - tri ) ),
                    QPoint( int( self.bl + self.bw * self.cl + tri ), int( self.bt + self.bh * self.cb )  ),
                    ] )
                # Polygons
                painter.drawPolygon( poly1 )
                painter.drawPolygon( poly2 )
                painter.drawPolygon( poly3 )
                painter.drawPolygon( poly4 )
        elif ( render == False and self.drop == False ):
            # Dots ( no results )
            painter.setPen( QtCore.Qt.NoPen )
            if qpixmap == None:painter.setBrush( QBrush( self.color_2 ) )
            else:painter.setBrush( QBrush( self.color_1 ) )
            painter.drawEllipse( int( w2 - 0.2 * side ), int( h2 - 0.2 * side ), int( 0.4 * side ), int( 0.4 * side ) )

        # Information
        if self.state_information == True:
            # Variables
            s = 20
            r = 5
            cor = self.color_2
            cor.setAlpha( 200 )
            text = self.Information_Display()

            # Bounding Box
            box = QRect( int( s ), int( hh - s*6 ), int( ww - s*2 ), int( s*5 ) )
            # Highlight
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QBrush( cor ) )
            painter.drawRoundedRect( box, r, r )
            # String
            painter.setBrush( QtCore.Qt.NoBrush )
            painter.setPen( QPen( self.color_1, 1, Qt.SolidLine ) )
            qfont = QFont( "Consolas", 10 )
            painter.setFont( qfont )
            painter.drawText( box, Qt.AlignCenter, text )
            # Garbage
            del qfont

        # Display Color Picker
        if self.operation == "color_picker":
            self.ColorPicker.Render(painter, self.ex, self.ey )

        # Drag and Drop Triangle
        if ( self.drop == True and self.drag == False ):
            Paintables.Painter_Triangle( self.color_1, painter, w2, h2, side )
    #endregion


