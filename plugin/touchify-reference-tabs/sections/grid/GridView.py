import math
import zipfile
from krita import *
from PyQt5 import QtCore, QtGui
from ...dataclasses.images import ImageClip, InsertablePin
from ...extensions.calculations import *
from ...extensions.color_picker import *
from ...extensions.native_actions import NativeActions
from ...extensions.paintables import Paintables
from .ui.ContextMenu import ContextMenu

class GridView( QWidget ):
    # Grid
    SIGNAL_PREVIEW_REQUESTED = QtCore.pyqtSignal( str )
    SIGNAL_INDEX = QtCore.pyqtSignal( int )
    # Menu
    SIGNAL_PIN_IMAGE = QtCore.pyqtSignal( [ InsertablePin, ImageClip ] )


    # Init
    def __init__( self, parent ):
        super( GridView, self ).__init__( parent )
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
        self.scale_method = Qt.FastTransformation

        # Compact
        self.file_search = []

        # Line
        self.line_index = 0
        self.line_path = [ None ]
        self.line_qpixmap = [ None ]
        # Grid
        self.grid_size = 200
        self.grid_fit = Qt.KeepAspectRatioByExpanding
        self.gix = 0
        self.giy = 0
        self.gmx = 3
        self.gmy = 3
        self.grid_path = [ [ None ] * self.gmx ] * self.gmy
        self.grid_qpixmap = [ [ None ] * self.gmx ] * self.gmy
        self.grid_start = 0
        self.grid_end = self.gmx * self.gmy
        self.glt = 0
        self.glb = 0
        # Thumbnails
        self.tw = 200
        self.th = 200
        # Clip
        self.clip_false = ImageClip(False,0,0,1,1)

        # State
        self.state_maximized = False
        self.state_press = False
        self.state_pickcolor = False

        # State
        self.state_maximized = False
        # Interaction
        self.operation = None

        # Colors
        self.color_1 = QColor( "#ffffff" )
        self.color_2 = QColor( "#000000" )
        self.color_alpha = QColor( 0, 0, 0, 50 )

        # Function>>
        self.function_drop_panel = False
        self.function_operation = ""

        # Color Picker
        self.ColorPicker = ColorPicker(self)

        # Drag and Drop
        self.setAcceptDrops( True )
        self.drop = False
        self.drag = False
        
    def sizeHint( self ):
        return QtCore.QSize( 5000,5000 )

    # Relay

    def Set_FileSearch( self, file_search ):
        self.file_search = file_search

    def Set_Theme( self, color_1, color_2 ):
        self.color_1 = color_1
        self.color_2 = color_2

    def Set_Size( self, ww, hh, state_maximized ):
        self.ww = ww
        self.hh = hh
        self.w2 = ww * 0.5
        self.h2 = hh * 0.5
        self.state_maximized = state_maximized
        self.resize( ww, hh )
        self.Render_Matrix()
        self.ColorPicker.setSourceSize(ww, hh)

    def Set_Scale_Method( self, scale_method ):
        self.scale_method = scale_method
        self.update()

    # Display

    def Display_Default( self ):
        self.grid_path = [ [ None ] * self.gmx ] * self.gmy
        self.grid_qpixmap = [ [ None ] * self.gmx ] * self.gmy
        self.update()
        self.Camera_Grab()

    def Display_Path( self, line_path, line_index ):
        if self.line_path != line_path:
            self.line_path = line_path
            self.line_qpixmap = [ None ] * len( line_path )
        self.line_index = line_index
        # Update
        self.Render_Matrix()
        self.update()
        self.Camera_Grab()

    # Grid
    def Grid_Size( self, value: int ):
        self.grid_size = value
        self.Render_Matrix()
        self.update()
        self.Camera_Grab()

    def Grid_Fit( self, boolean: bool ):
        if boolean == False:
            self.grid_fit = Qt.AspectRatioMode.KeepAspectRatioByExpanding
        elif boolean == True:
            self.grid_fit = Qt.AspectRatioMode.KeepAspectRatio
        self.update()
        self.Camera_Grab()

    def Grid_Index( self, ex: int, ey: int ):
        # Grid Index
        self.gix = Limit_Range( int( ( ex / self.ww ) * self.gmx ), 0, self.gmx - 1 )
        self.giy = Limit_Range( int( ( ey / self.hh ) * self.gmy ), 0, self.gmy - 1 )
        # Line Index
        line_index = self.grid_start + gi_to_pi( self.gix, self.giy, self.gmx )
        line_limit = len( self.line_path ) - 1
        self.line_index = Limit_Range( line_index, 0, line_limit )
        # Signal
        self.SIGNAL_INDEX.emit( self.line_index )

    def Grid_Increment( self, increment: int ):
        # Variables
        limit = len( self.line_path ) - 1
        # Calculations
        gix, giy = pi_to_gi( self.line_index, self.gmx, self.gmy )
        if increment < 0:
            delta = self.gmx * increment
            self.line_index = Limit_Range( self.grid_start + gix + delta, 0, limit )
        if increment > 0:
            self.line_index = Limit_Range( self.grid_end + gix, 0, limit )
        # Signal
        self.SIGNAL_INDEX.emit( self.line_index )
        # Update
        self.Render_Matrix()
        self.update()
        self.Camera_Grab()

    # Render

    # Pagination
    def Pagination_Reset( self, ey ):
        oz = ey % self.th
        self.glt = ey - oz
        self.glb = self.glt + self.th
    
    def Pagination_Stylus( self, ey ):
        # Event
        ey = Limit_Range( ey, 0, self.hh )
        # Variables
        margin = 2
        limit = len( self.line_path )
        update = False
        # Logic
        if ey > ( self.glb + margin ):
            self.grid_start = Limit_Range( self.grid_start - self.gmx, 0, limit )
            self.grid_end = Limit_Range( self.grid_end - self.gmx, 0, limit )
            self.Pagination_Reset( ey )
            update = True
        if ey < ( self.glt - margin ):
            self.grid_start = Limit_Range( self.grid_start + self.gmx, 0, limit )
            self.grid_end = Limit_Range( self.grid_end + self.gmx, 0, limit )
            self.Pagination_Reset( ey )
            update = True
        # Update
        if update == True:
            self.Render_Matrix()
            self.update()
            self.Camera_Grab()

    def Cursor_Icon( self ):
        if ( self.state_pickcolor == True and self.state_press == True ):
            QApplication.setOverrideCursor( Qt.CrossCursor )
        else:
            QApplication.restoreOverrideCursor()

    # Camera
    def Camera_Grab( self ):
        try:self.qimage_grab = self.grab().toImage()
        except:pass

    # Context Menu
    def Context_Menu( self, event ):
        self.state_press = False
        grid_qpixmap = self.grid_qpixmap[self.giy][self.gix]
        if grid_qpixmap: ContextMenu.OpenContextMenu(self, event)

    #region Render
    
    def Render_Matrix( self ):
        if len( self.line_path ) > 0:
            # Grid Matrix
            gmx = round( self.ww / self.grid_size )
            gmy = round( ( self.hh * 0.8 ) / self.grid_size )
            if gmx <= 0:gmx = 1
            if gmy <= 0:gmy = 1
            # Thumbnails
            self.tw = int( self.ww / gmx )
            self.th = int( self.hh / gmy )

            # Screen Size
            screen = self.gmx * self.gmy
            # Screen Variation
            if ( self.gmx != gmx or self.gmy != gmy ):
                self.gmx = gmx
                self.gmy = gmy
            # Screen Inercia
            if self.line_index < self.grid_start:
                self.grid_start = math.floor( self.line_index / self.gmx ) * self.gmx
            if self.line_index >= self.grid_end:
                self.grid_start = math.ceil( ( self.line_index - screen + 1 ) / self.gmx ) * self.gmx
            # Screen End
            self.grid_end = self.grid_start + screen

            # Clean
            margin = 100
            cs = self.grid_start - margin
            ce = self.grid_end + margin
            for i in range( 0, cs ):
                self.line_qpixmap[i] = None
            for i in range( ce, len( self.line_qpixmap ) ):
                self.line_qpixmap[i] = None

            # Construct
            default = QPixmap()
            archive = Paintables.Painter_Icon( "bundle_archive" )
            string = []
            render = []
            for i in range( self.grid_start, self.grid_end ):
                try:
                    path = self.line_path[i]
                    qpixmap = self.line_qpixmap[i]
                    if qpixmap in [ None, False, True ]:
                        qpixmap = QPixmap( path )
                        if qpixmap.isNull() == False:
                            self.line_qpixmap[i] = qpixmap
                        elif zipfile.is_zipfile( path ) == True:
                            archive = zipfile.ZipFile( path, "r" )
                            name_list = archive.namelist()
                            name_list.sort()
                            qpixmap = True
                            for name in name_list:
                                try:
                                    if name.split( "." )[1] in self.file_search:
                                        extract = archive.open( name )
                                        data = extract.read()
                                        qpixmap = QPixmap()
                                        qpixmap.loadFromData( data )
                                        if qpixmap.isNull() == False:
                                            self.line_qpixmap[i] = qpixmap
                                            break
                                except:
                                    qpixmap = True
                        else:
                            qpixmap = True
                except:
                    qpixmap = None
                string.append( path )
                render.append( qpixmap )

            # Lists
            self.grid_path = preview_to_grid( string, self.gmx, self.gmy )
            self.grid_qpixmap = preview_to_grid( render, self.gmx, self.gmy )

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

        # Functions
        self.Cursor_Icon( )
        self.Grid_Index( ex, ey )

        # LMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            if self.state_pickcolor == True:
                self.operation = "color_picker"
                self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.state_pickcolor )
            else:
                self.operation = "neutral_press"
        if ( event.modifiers() == QtCore.Qt.ShiftModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "camera_move"
        if ( event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "pagination"
            self.Pagination_Reset( ey )
        if ( event.modifiers() == QtCore.Qt.AltModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.operation = "drag_drop"

        # MMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.MiddleButton ):
            self.operation = "camera_move"

        # RMB
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = None
            self.Context_Menu( event )
        if ( event.modifiers() == QtCore.Qt.ShiftModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = "camera_scale"
        if ( event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.RightButton ):
            self.operation = "pagination"
            self.Pagination_Reset( ey )
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
        if self.operation == "neutral_press":
            self.Grid_Index( ex, ey )
        if self.operation == "color_picker":
            self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.state_pickcolor )
        # Camera
        if self.operation == "camera_move":
            pass
        if self.operation == "camera_scale":
            pass
        # Pagination
        if self.operation == "pagination":
            self.Pagination_Stylus( ey )
        # Drag Drop
        if self.operation == "drag_drop":
            path = self.grid_path[self.giy][self.gix]       
            clip = ImageClip(False, 0, 0, 1, 1)
            if path != None:
                self.drag = True
                NativeActions.Drag_Drop(self, path, clip)


        # Update
        self.update()
    
    def mouseDoubleClickEvent( self, event ):
        self.SIGNAL_PREVIEW_REQUESTED.emit( self.grid_path[self.giy][self.gix] )
    
    def mouseReleaseEvent( self, event ):
        # Variables
        self.operation = None
        self.state_press = False
        # Function
        self.ColorPicker.Event( self.ex, self.ey, self.qimage_grab, self.state_press, self.state_pickcolor )
        self.Cursor_Icon( )
        # Update
        self.update()
        self.Camera_Grab()

    def wheelEvent( self, event ):
        delta_y = event.angleDelta().y()
        angle = 5
        if delta_y >= angle:
            self.Grid_Increment( +1 )
        if delta_y <= -angle:
            self.Grid_Increment( -1 )

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
                event.setDropAction( Qt.CopyAction )
                mime_data = NativeActions.Drop_Inside( event )
                #TODO: Implement Drop Functionality
            event.accept()
        else:
            event.ignore()
        self.drop = False
        self.drag = False
        self.update()

    def enterEvent( self, event ):
        self.Camera_Grab()
    
    def leaveEvent( self, event ):
        self.update()

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
        if self.tw < self.th:
            thumb = self.tw
        else:
            thumb = self.th

        # Painter
        painter = QPainter( self )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, True )

        # Background Hover
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( self.color_alpha ) )
        painter.drawRect( 0, 0, ww, hh )

        # Draw QPixmaps
        for y in range( 0, len( self.grid_qpixmap ) ):
            row = self.grid_qpixmap[y]
            for x in range( 0, len( row ) ):
                # Clip Mask
                px = self.tw * x
                py = self.th * y
                thumbnail = QRect( int( px ), int( py ), int( self.tw ), int( self.th ) )
                painter.setClipRect( thumbnail, Qt.ReplaceClip )

                # Render
                qpixmap = self.grid_qpixmap[y][x]
                broken = Paintables.Painter_Icon( "broken-preset" )
                render = True
                if qpixmap in [ None, False, True ]:
                    render = False
                if render == True:
                    try:draw = qpixmap.scaled( int( self.tw + 1 ), int( self.th + 1 ), self.grid_fit, self.scale_method )
                    except:draw = broken.scaled( int( self.tw + 1 ), int( self.th + 1 ), self.grid_fit, self.scale_method )
                    rw = draw.width()
                    rh = draw.height()
                    ox = ( self.tw - rw ) * 0.5
                    oy = ( self.th - rh ) * 0.5
                    painter.drawPixmap( int( px + ox ), int( py + oy ), draw )
                else:
                    painter.setPen( QtCore.Qt.NoPen )
                    if qpixmap == None or self.drop == True:
                        painter.setBrush( QBrush( self.color_2 ) )
                    else:
                        painter.setBrush( QBrush( self.color_1 ) )
                    ox = ( self.tw * 0.5 ) - ( 0.3 * thumb )
                    oy = ( self.th * 0.5 ) - ( 0.3 * thumb )
                    painter.drawEllipse( int( px + ox ), int( py + oy ), int( 0.6 * thumb ), int( 0.6 * thumb ) )

        # Clean Mask
        painter.setClipping( False )

        # Display Color Picker
        if self.operation == "color_picker":
            self.ColorPicker.Render( painter, self.ex, self.ey )

        # Drag and Drop Triangle
        if ( self.drop == True and self.drag == False ):
            Paintables.Painter_Triangle( self.color_1, painter, w2, h2, side )

    #endregion

