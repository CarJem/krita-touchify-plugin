from dataclasses import dataclass
import os
from typing import Optional
import urllib
from krita import *
from PyQt5 import QtCore, QtGui
from ...extensions.calculations import *
from .extensions.packer import Packer
from ...extensions.color_picker import *
from .dataclasses.ReferencePin import ReferencePin
from .ui.ContextMenu import ContextMenu
from ...extensions.commons import Commons
from ...extensions.native_actions import NativeActions
from ...dataclasses.images import ImageClip, InsertablePin
from ...extensions.paintables import Paintables



class ReferenceView( QWidget ):


    @dataclass
    class LabelInfo:
        valid: bool
        text: Optional[str] = None
        font: Optional[str] = None
        letter: Optional[int] = None
        pen: Optional[str] = None
        bg: Optional[str] = None
        


    #region Signals

    # Reference
    SIGNAL_PIN_IMAGE = QtCore.pyqtSignal( InsertablePin )
    SIGNAL_PIN_LABEL = QtCore.pyqtSignal( InsertablePin )
    SIGNAL_PIN_SAVE = QtCore.pyqtSignal( [ QPixmap ] )
    SIGNAL_BOARD_SAVE = QtCore.pyqtSignal( list )
    SIGNAL_CAMERA = QtCore.pyqtSignal( [ list, float, int ] )

    # UI
    SIGNAL_PB_VALUE = QtCore.pyqtSignal( int )
    SIGNAL_PB_MAX = QtCore.pyqtSignal( int )
    SIGNAL_PACK_STOP = QtCore.pyqtSignal( bool )
    SIGNAL_LABEL_PANEL = QtCore.pyqtSignal( bool )
    SIGNAL_LABEL_INFO = QtCore.pyqtSignal( [LabelInfo], [type(None)] )
    SIGNAL_ACTIONS_UPDATED = QtCore.pyqtSignal( )
    SIGNAL_PREVIEW_REQUESTED = QtCore.pyqtSignal( QPixmap )
    #endregion

    def __init__( self, parent ):
        super( ReferenceView, self ).__init__( parent )
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)

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

        # State
        self.state_inside = False
        self.state_maximized = False
        self.state_press = False
        self.state_select = False
        self.state_pack = False
        self.state_focused = False
        self.state_snap = False

        # Mode
        self.mode_autosave = False
        self.mode_label = False
        self.mode_pickcolor = False
        self.mode_snap = False
        self.mode_base_selection = False
        self.mode_base_cameramove = False
        self.mode_base_camerascale = False
        self.mode_base_selectionmove = False
        self.mode_lock = False

        # Interaction
        self.operation = None



        # Camera
        self.cn = [
            0.000, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009,
            0.010, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019,
            0.020, 0.021, 0.022, 0.023, 0.024, 0.025, 0.026, 0.027, 0.028, 0.029,
            0.030, 0.031, 0.032, 0.033, 0.034, 0.035, 0.036, 0.037, 0.038, 0.039,
            0.040, 0.041, 0.042, 0.043, 0.044, 0.045, 0.046, 0.047, 0.048, 0.049,
            0.050, 0.051, 0.052, 0.053, 0.054, 0.055, 0.056, 0.057, 0.058, 0.059,
            0.060, 0.061, 0.062, 0.063, 0.064, 0.065, 0.066, 0.067, 0.068, 0.069,
            0.070, 0.071, 0.072, 0.073, 0.074, 0.075, 0.076, 0.077, 0.078, 0.079,
            0.080, 0.081, 0.082, 0.083, 0.084, 0.085, 0.086, 0.087, 0.088, 0.089,
            0.090, 0.091, 0.092, 0.093, 0.094, 0.095, 0.096, 0.097, 0.098, 0.099,

            0.10, 0.10429, 0.10869, 0.11316, 0.11771, 0.12231, 0.12697, 0.13169, 0.13645, 0.14126, 0.14611, 0.1501, 0.15596, 0.16093, 0.16598, 0.17105, 0.17616, 0.18132, 0.18651, 0.19176, 0.19704, 
            0.20237, 0.20773, 0.21314, 0.2186, 0.22409, 0.22964, 0.23521, 0.24086, 0.24652, 0.25226, 0.25801, 0.26384, 0.26969, 0.27561, 0.28156, 0.28759, 0.29364, 0.29976, 
            0.30592, 0.31214, 0.31842, 0.32475, 0.33114, 0.33757, 0.34409, 0.35064, 0.35729, 0.36395, 0.37074, 0.37753, 0.38446, 0.3914, 0.39846, 
            0.40556, 0.41276, 0.42003, 0.42738, 0.43482, 0.44233, 0.44996, 0.45764, 0.46547, 0.4733, 0.48138, 0.48945, 0.49772, 
            0.50601, 0.51454, 0.52307, 0.53186, 0.54066, 0.54974, 0.55885, 0.56825, 0.5777, 0.58743, 0.59728, 
            0.60739, 0.61769, 0.6282, 0.63904, 0.65, 0.66145, 0.67309, 0.6851, 0.69755,
            0.7103, 0.72363, 0.7375, 0.75188, 0.76691, 0.78293, 0.79985, 
            0.8179, 0.83738, 0.85876, 0.88275, 
            0.91046, 0.94563, 

            1.0000, 1.0681, 1.1362, 1.2043, 1.2724, 1.3441, 1.4158, 1.5119, 1.6081, 1.7042, 1.8004, 1.9181,
            2.0359, 2.1708, 2.3058, 2.4514, 2.5970, 2.7812, 2.9654, 
            3.1517, 3.3381, 3.5795, 3.8209, 
            4.0623, 4.3038, 4.6025, 4.9012,
            5.2029, 5.5047, 5.8573,
            6.2099, 6.5693, 6.9288, 
            7.3262, 7.7237, 
            8.1328, 8.5419, 8.9714,
            9.4011, 9.84855,
            10.296, 10.7470,
            11.198, 11.6725,
            12.147, 12.6215,
            13.096, 13.5770,
            14.058, 14.5490,
            15.040, 15.5305,
            16.021, 16.5150,
            17.009, 17.5075,
            18.006, 18.5045,
            19.003, 19.5015,

            20.0, 20.5,
            21.0, 21.5,
            22.0, 22.5,
            23.0, 23.5,
            24.0, 24.5,
            25.0, 25.5,
            26.0, 26.5,
            27.0, 27.5,
            28.0, 28.5,
            29.0, 29.5,
            30.0, 30.5,
            31.0, 31.5,
            32.0, 32.5,
            33.0, 33.5,
            34.0, 34.5,
            35.0, 35.5,
            36.0, 36.5,
            37.0, 37.5,
            38.0, 38.5,
            39.0, 39.5,
            40.0, 40.5,
            41.0, 41.5,
            42.0, 42.5,
            43.0, 43.5,
            44.0, 44.5,
            45.0, 45.5,
            46.0, 46.5,
            47.0, 47.5,
            48.0, 48.5,
            49.0, 49.5,

            50.0,
            51.0,
            52.0,
            53.0,
            54.0,
            55.0,
            56.0,
            57.0,
            58.0,
            59.0,
            60.0,
            61.0,
            62.0,
            63.0,
            64.0,
            65.0,
            66.0,
            67.0,
            68.0,
            69.0,
            70.0,
            71.0,
            72.0,
            73.0,
            74.0,
            75.0,
            76.0,
            77.0,
            78.0,
            79.0,
            80.0,
            81.0,
            82.0,
            83.0,
            84.0,
            85.0,
            86.0,
            87.0,
            88.0,
            89.0,
            90.0,
            91.0,
            92.0,
            93.0,
            94.0,
            95.0,
            96.0,
            97.0,
            98.0,
            99.0,
            100.0,
            ]
        self.ci = self.cn.index( 1 )
        self.cz = self.cn[self.ci] # Camera Zoom

        # Display
        self.scale_method = Qt.FastTransformation

        # Files
        self.file_extension = []
        self.file_path = ""

        # Pin
        self.pin_list: list[ReferencePin] = []
        self.pin_previous: list[ReferencePin] = []
        self.pin_index = None
        self.pin_path = None
        self.pin_basename = None
        self.pin_node = None
        self.pin_count = 0
        self.pin_preview = None

        # Limit
        self.limit_x = []
        self.limit_y = []

        # Selection
        self.select_box = False
        self.select_count = 0

        # Pack
        self.packing_process = False

        # Board (surface)
        self.board_l = 0
        self.board_r = 0
        self.board_t = 0
        self.board_b = 0
        self.board_w = 0
        self.board_h = 0

        # Drag and Drop
        self.setAcceptDrops( True )
        self.drop = False
        self.drag = False

        # Colors
        self.color_1 = QColor( "#ffffff" )
        self.color_2 = QColor( "#000000" )
        self.color_shade = QColor( 0, 0, 0, 30 )
        self.color_alpha = QColor( 0, 0, 0, 50 )
        self.color_backdrop = QColor( 0, 0, 0, 100 )
        self.color_blue = QColor( "#3daee9" )

        # Color Picker
        self.ColorPicker = ColorPicker(self)
    
    #region Relay

    def Set_File_Extension( self, file_extension ):
        self.file_extension = file_extension
        

    def Set_Theme( self, color_1, color_2 ):
        self.color_1 = color_1
        self.color_2 = color_2

    def Set_Size( self, ww, hh, state_maximized ):
        if self.state_pack == False:
            # Count
            self.pin_count = len( self.pin_list )
            # Transform Correction
            dx = ( ww - self.ww ) * 0.5
            dy = ( hh - self.hh ) * 0.5
            for i in range( 0, self.pin_count ):
                self.Move_Transform( self.pin_list, i, dx, dy )
            # Widget
            self.ww = ww
            self.hh = hh
            self.w2 = ww * 0.5
            self.h2 = hh * 0.5
            # Maximized State
            self.state_maximized = state_maximized
            # Board
            self.Board_Limit( "DRAW" )
            # Update
            self.resize( ww, hh )
            self.ColorPicker.setSourceSize(ww, hh)
    
    def Set_Camera( self, position, zoom ):
        # Position
        self.Pin_Previous()
        board_l, board_r, board_t, board_b, board_w, board_h = self.Board_Limit( "PIN" )
        cx = self.w2
        cy = self.h2
        px = board_l + board_w * position[0]
        py = board_t + board_h * position[1]
        dx = cx - px
        dy = cy - py
        for i in range( 0, self.pin_count ):
            self.Move_Transform( self.pin_previous, i, dx, dy )

        # Zoom
        index = 0
        for i in range( 0, len( self.cn ) ):
            if ( zoom >= self.cn[i] ) and ( zoom < self.cn[i+1] ):
                index = i
                break
        self.ci = index
        self.cz = self.cn[index]

        # Update
        self.Board_Update()
    
    def Set_Scale_Method( self, scale_method ):
        self.scale_method = scale_method
        self.update()
    
    def Set_Stop_Cycle( self ):
        try:self.worker_packer.STOP()
        except:pass
    
    def Set_File_Path( self, path ):
        if path not in [ "", ".", None]:
            name = ( os.path.basename( path ) ).split( "." )[0]
            file_path = f" [ { name } ]"
        else:
            file_path = ""
        self.file_path = file_path
        self.update()
    
    #endregion
    
    #region Points
    def Point_Deltas( self, ex, ey ):
        try:
            dx = ( ex - self.ox ) / self.cz
            dy = ( ey - self.oy ) / self.cz
        except:
            dx = 0
            dy = 0
        return dx, dy
    def Point_Location( self, ex, ey ):
        try:
            px = self.w2 + ( ex - self.w2 ) / self.cz
            py = self.h2 + ( ey - self.h2 ) / self.cz
        except:
            px = self.w2
            py = self.h2
        return px, py
    #endregion
    
    #region Pin

    def Pin_Insert( self, pin: ReferencePin ):
        # Pin
        self.pin_list.append( pin )
        self.pin_count = len( self.pin_list )
        # Update
        self.update()
    
    def Pin_URL( self, bx, by ):
        url, ok = QInputDialog.getText( self, "Insert Pin", "URL", QLineEdit.Normal, "" )
        if ok and url != "":
            pin = InsertablePin(bx, by, url)
            self.SIGNAL_PIN_IMAGE.emit( pin )
            
    def Pin_ZData(self, index ):
        path = self.pin_list[index].path
        web = self.pin_list[index].web

        if path != None:
            zdata = Commons.Bytes_Python( path )
        elif web != None:
            zdata = Commons.Download_Data( web )
        else:
            zdata = None

        if not zdata: return

        qpixmap = QPixmap()
        qpixmap.loadFromData( zdata )
        if qpixmap.isNull(): return
        
        self.pin_list[index].zdata = str(zdata)
        self.pin_list[index].qpixmap = qpixmap
        self.pin_list[index].path = None
        self.pin_list[index].web = None

    def Pin_Update( self ):
        for i in range( 0, self.pin_count ):
            self.pin_list[i].index = i
    
    def Pin_Clear( self ):
        self.pin_index = None
        self.pin_path = None
        self.pin_basename = None
        self.pin_node = None
        self.state_focused = False

    def Pin_Exists( self, ex, ey ):
        index = None
        for i in range( self.pin_count - 1, -1, -1 ):
            dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )
            check = ( ex >= dl ) and ( ex <= dr ) and ( ey >= dt ) and ( ey <= db )
            if check == True:
                index = i
                break
        return index != None

    def Pin_Index( self, ex, ey ):
        # Variables
        index = None
        self.pin_count = len( self.pin_list )

        # Index
        for i in range( self.pin_count - 1, -1, -1 ):
            dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )
            check = ( ex >= dl ) and ( ex <= dr ) and ( ey >= dt ) and ( ey <= db )
            if check == True:
                index = i
                break

        # Variables
        if index != None:
            # Pin List
            save = self.pin_list[ index ]
            self.pin_list.pop( index )
            self.pin_list.append( save )

            # Pin Previous
            save = self.pin_previous[ index ]
            self.pin_previous.pop( index )
            self.pin_previous.append( save )

            # Variables
            pin_index = self.pin_count - 1
            self.pin_index = pin_index
            self.pin_node = self.Pin_Node( self.pin_index )
            self.state_focused = True
            if self.pin_list[pin_index].tipo == "image":
                self.pin_path = self.pin_list[pin_index].path
                try:self.pin_basename = str( os.path.basename( self.pin_path ) ) # local
                except:self.pin_basename = None # web
            else:
                self.pin_path = None
                self.pin_basename = None
        else:
            self.Pin_Clear()
    
    def Pin_Active( self, index ):
        for i in range( 0, self.pin_count ):
            self.pin_list[i].active = False
        if index != None:
            self.pin_list[index].active = True
    
    def Pin_Node( self, index ):
        # None = Board, 0 = No Node, 1-9 = Node
        if index == None:
            pin_node = None
        else:
            # Variables
            sca = 50
            rot = 75

            # Read
            img = self.pin_list[index].tipo == "image"

            # Read
            dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( index )

            # List
            nodes = []
            nodes.append( [ Trig_2D_Points_Distance( dl, dt, self.ox, self.oy ), 1 ] ) # top left
            nodes.append( [ Trig_2D_Points_Distance( dr, dt, self.ox, self.oy ), 3 ] ) # top right
            nodes.append( [ Trig_2D_Points_Distance( dl, db, self.ox, self.oy ), 7 ] ) # bot left
            nodes.append( [ Trig_2D_Points_Distance( dr, db, self.ox, self.oy ), 9 ] ) # bot right
            if ( dw >= sca or dh >= sca ):
                nodes.append( [ Trig_2D_Points_Distance( dx, dt, self.ox, self.oy ), 2 ] ) # top
                nodes.append( [ Trig_2D_Points_Distance( dl, dy, self.ox, self.oy ), 4 ] ) # mid left
                nodes.append( [ Trig_2D_Points_Distance( dr, dy, self.ox, self.oy ), 6 ] ) # mid right
                nodes.append( [ Trig_2D_Points_Distance( dx, db, self.ox, self.oy ), 8 ] ) # bot
            if ( img ==  True and ( dw >= rot or dh >= rot ) ):
                nodes.append( [ Trig_2D_Points_Distance( dx, dy, self.ox, self.oy ) * 2, 5 ] ) # mid
            nodes.sort()

            # Index
            pin_node = 0
            if nodes[0][0] <= 20:
                pin_node = nodes[0][1]

        # Return
        return pin_node
    
    def Pin_Limits( self ):
        # Variables
        set_limit_x = list()
        set_limit_y = list()
        active_select = False
        if self.pin_index != None:
            active_select = self.pin_list[self.pin_index].select
        # Collect values
        for i in range( 0, self.pin_count ):
            pin_select = self.pin_list[i].select
            check_active = self.pin_index != i and active_select == False
            check_select = self.pin_index != i and active_select == True and pin_select == False
            if ( check_active == True or check_select == True ):
                set_limit_x.append( self.pin_list[i].bl )
                set_limit_x.append( self.pin_list[i].br )
                set_limit_y.append( self.pin_list[i].bt )
                set_limit_y.append( self.pin_list[i].bb )
        # Update Limits
        self.limit_x = list( set( set_limit_x ) )
        self.limit_y = list( set( set_limit_y ) )
    
    def Pin_Previous( self ):
        if self.pin_count > 0:
            pin_previous = []
            for i in range( 0, self.pin_count ):
                dicta = {
                    # Transform
                    "trz" : self.pin_list[i].trz,
                    "tsk" : self.pin_list[i].tsk,
                    "tsw" : self.pin_list[i].tsw,
                    "tsh" : self.pin_list[i].tsh,
                    # Bounding Box
                    "bx" : self.pin_list[i].bx,
                    "by" : self.pin_list[i].by,
                    "bl" : self.pin_list[i].bl,
                    "br" : self.pin_list[i].br,
                    "bt" : self.pin_list[i].bt,
                    "bb" : self.pin_list[i].bb,
                    "bw" : self.pin_list[i].bw,
                    "bh" : self.pin_list[i].bh,
                    }
                pin_previous.append( ReferencePin(**dicta) )
            self.pin_previous = pin_previous
    
    def Pin_Preview( self, index ):
        # Logic
        if ( index == None or self.pin_preview != None ):
            return
        else:
            qpixmap = self.pin_list[index].qpixmap
            if qpixmap != None:
                self.SIGNAL_PREVIEW_REQUESTED.emit(qpixmap)
    
    def Pin_Draw_Box( self, index ):
        if index != None:
            # Read
            bx = self.pin_list[index].bx
            by = self.pin_list[index].by
            bl = self.pin_list[index].bl
            br = self.pin_list[index].br
            bt = self.pin_list[index].bt
            bb = self.pin_list[index].bb
            bw = self.pin_list[index].bw
            bh = self.pin_list[index].bh
            # Transform
            dx = self.w2 + ( bx - self.w2 ) * self.cz
            dy = self.h2 + ( by - self.h2 ) * self.cz
            dl = self.w2 + ( bl - self.w2 ) * self.cz
            dr = self.w2 + ( br - self.w2 ) * self.cz
            dt = self.h2 + ( bt - self.h2 ) * self.cz
            db = self.h2 + ( bb - self.h2 ) * self.cz
            dw = dr - dl
            dh = db - dt
            # Return
            return dx, dy, dl, dr, dt, db, dw, dh
    
    def Pin_Draw_QPixmap( self, lista: list[ReferencePin], index: int ):
        # Variables
        tipo = lista[index].tipo
        render = lista[index].render
        if ( index != None and tipo == "image" and render == True ):
            # Read
            trz = lista[index].trz
            tsw = lista[index].tsw
            tsh = lista[index].tsh
            egs = lista[index].egs
            efx = lista[index].efx
            efy = lista[index].efy
            qpixmap = lista[index].qpixmap
            # Pixmap
            if qpixmap != None:
                draw = self.Edit_QPixmap( qpixmap, egs, efx, efy )
                draw = self.Scale_QPixmap( draw, tsw, tsh )
                draw = self.Rotate_QPixmap( draw, trz )
                lista[index].draw = draw
                del draw
            else:
                lista[index].qpixmap = None
                lista[index].draw = None
            # Garbage
            del qpixmap
    
    #endregion
    
    #region QPixmap
    
    def Edit_QPixmap( self, source, egs, efx, efy ):
        source = source.toImage()
        if egs == True:
            source = source.convertToFormat( QImage.Format_Grayscale8 )
        if ( efx == True or efy == True ):
            source = source.mirrored( efx, efy )
        draw = QPixmap().fromImage( source )
        return draw
    
    def Scale_QPixmap( self, source, width, height ):
        w = width * self.cz
        h = height * self.cz
        if( self.state_inside == False and self.scale_method == True ):
            draw = source.scaled( int( w ), int( h ), Qt.IgnoreAspectRatio, Qt.SmoothTransformation )
        else:
            draw = source.scaled( int( w ), int( h ), Qt.IgnoreAspectRatio, Qt.FastTransformation )
        draw = draw.copy( int( w ), int( h ), int( w ), int( h ) ) # Cut the error
        return draw
    
    def Rotate_QPixmap( self, source, angle ):
        if angle == 0:
            draw = source
        else:
            rotation = QTransform().rotate( angle, Qt.ZAxis )
            draw = source.transformed( rotation )
        return draw
    
    #endregion
    
    #region Label
    
    def Label_Insert( self, pos: QPoint ):
        bx, by = self.Point_Location( pos.x(), pos.y() )
        pin = InsertablePin(bx,by)
        self.SIGNAL_PIN_LABEL.emit( pin )
    
    def Label_List( self ):
        lista = []
        for i in range( 0, self.pin_count ):
            if self.pin_list[i].select == True:
                lista.append( i )

        if self.state_focused and self.select_count <= 0 and self.pin_index != None:
            if self.pin_list[self.pin_index].tipo == "label": lista.append(self.pin_index)
        return lista
    
    def Label_Panel( self, index ):
        if index:
            info = ReferenceView.LabelInfo(
                True,
                self.pin_list[index].text,
                self.pin_list[index].font,
                self.pin_list[index].letter,
                self.pin_list[index].pen,
                self.pin_list[index].bg 
            )
            self.SIGNAL_LABEL_INFO.emit( info )
        else:
            self.SIGNAL_LABEL_INFO.emit( ReferenceView.LabelInfo(False) )            

    def Get_Label_Infomation( self ):
        lista = self.Label_List()
        if len( lista ) > 0:
            index = lista[-1]
            info = {
                "text"   : self.pin_list[index].text,
                "font"   : self.pin_list[index].font,
                "letter" : self.pin_list[index].letter,
                "pen"    : self.pin_list[index].pen,
                "bg"     : self.pin_list[index].bg,
                }
        else:
            info = None
        return info

    def Set_Label_Text( self, text ):
        lista = self.Label_List()
        for i in lista:
            self.pin_list[i].text = text
        self.update()
    
    def Set_Label_Font( self, font ):
        lista = self.Label_List()
        for i in lista:
            self.pin_list[i].font = font
        self.update()
    
    def Set_Label_Letter( self, letter ):
        lista = self.Label_List()
        for i in lista:
            self.pin_list[i].letter = letter
        self.update()
    
    def Set_Label_Pen( self, pen ):
        lista = self.Label_List()
        for i in lista:
            self.pin_list[i].pen = pen
        self.update()
   
    def Set_Label_Bg( self, bg ):
        lista = self.Label_List()
        for i in lista:
            self.pin_list[i].bg = bg
        self.update()
    
    #endregion
    
    #region Transformation

    def Pin_Transform( self, ex, ey, node ):
        # Check
        move = node == 0
        scale = node in [ 1, 2, 3, 4, 6, 7, 8, 9 ]
        rotate = node == 5
        # Transformation
        if move == True:
            dx, dy = self.Point_Deltas( ex, ey )
            self.Move_Pin( dx, dy )
        if scale == True:
            if self.pin_list[self.pin_index].tipo == "image":
                px, py = self.Point_Location( ex, ey )
                self.Scale_Pin( px, py, node )
            if self.pin_list[self.pin_index].tipo == "label":
                dx, dy = self.Point_Deltas( ex, ey )
                self.Scale_Label( self.pin_previous, self.pin_index, node, dx, dy )
        if rotate == True:
            if self.pin_list[self.pin_index].tipo == "image":
                dx = ( ex - self.ox )
                self.Rotate_Pin( dx )
    
    def Move_Pin( self, dx, dy ):
        # Variabels
        sx = 0
        sy = 0
        snap_dist = 10 / self.cz

        # Preview Move
        n_bx = self.pin_previous[self.pin_index].bx + dx
        n_by = self.pin_previous[self.pin_index].by + dy
        n_bl = self.pin_previous[self.pin_index].bl + dx
        n_br = self.pin_previous[self.pin_index].br + dx
        n_bt = self.pin_previous[self.pin_index].bt + dy
        n_bb = self.pin_previous[self.pin_index].bb + dy

        # Snap
        if self.state_snap == True:
            for j in range( 0, len( self.limit_x ) ):
                xj = self.limit_x[j]
                ll = xj - snap_dist
                lr = xj + snap_dist
                dl = abs( xj - n_bl )
                dr = abs( xj - n_br )
                cl = ( n_bl >= ll and n_bl <= lr )
                cr = ( n_br >= ll and n_br <= lr )
                if cl == True and dl < dr:
                    sx = xj - n_bl
                    break
                elif cr == True and dr < dl:
                    sx = xj - n_br
                    break
            for j in range( 0, len( self.limit_y ) ):
                yj = self.limit_y[j]
                lt = yj - snap_dist
                lb = yj + snap_dist
                dt = abs( yj - n_bt )
                db = abs( yj - n_bb )
                ct = ( n_bt >= lt and n_bt <= lb )
                cb = ( n_bb >= lt and n_bb <= lb )
                if ct == True and dt < db:
                    sy = yj - n_bt
                    break
                elif cb == True and db < dt:
                    sy = yj - n_bb
                    break

        # Move Pin Index
        self.Move_Transform( self.pin_previous, self.pin_index, dx + sx, dy + sy )

        # Snap and Selection
        if ( self.pin_list[self.pin_index].select == True and self.select_count > 0 ):
            for i in range( 0, self.pin_count ):
                if self.pin_list[i].select == True:
                    self.Move_Transform( self.pin_previous, i, dx + sx, dy + sy )
    
    def Move_Transform( self, previous, index, dx, dy ):
        self.pin_list[index].bx = previous[index].bx + dx
        self.pin_list[index].by = previous[index].by + dy
        self.pin_list[index].bl = previous[index].bl + dx
        self.pin_list[index].br = previous[index].br + dx
        self.pin_list[index].bt = previous[index].bt + dy
        self.pin_list[index].bb = previous[index].bb + dy
    
    def Move_Point( self, lista, index, px, py ):
        # Read
        bw = lista[index].bw
        bh = lista[index].bh
        # Write
        lista[index].bx = px + bw * 0.5
        lista[index].by = py + bh * 0.5
        lista[index].bl = px
        lista[index].br = px + bw
        lista[index].bt = py
        lista[index].bb = py + bh

    def Scale_Pin( self, px, py, node ):
        # Variables
        snap_dist = 20 / self.cz

        # Read
        tipo = self.pin_list[self.pin_index].tipo
        bx = self.pin_previous[self.pin_index].bx
        by = self.pin_previous[self.pin_index].by
        bl = self.pin_previous[self.pin_index].bl
        br = self.pin_previous[self.pin_index].br
        bt = self.pin_previous[self.pin_index].bt
        bb = self.pin_previous[self.pin_index].bb

        # Point Neutral
        if node == 1:
            nx = br
            ny = bb
            ax = bl
            ay = bt
        if node == 2:
            nx = bx
            ny = bb
            ax = bx
            ay = bt
        if node == 3:
            nx = bl
            ny = bb
            ax = br
            ay = bt
        if node == 4:
            nx = br
            ny = by
            ax = bl
            ay = by
        if node == 6:
            nx = bl
            ny = by
            ax = br
            ay = by
        if node == 7:
            nx = br
            ny = bt
            ax = bl
            ay = bb
        if node == 8:
            nx = bx
            ny = bt
            ax = bx
            ay = bb
        if node == 9:
            nx = bl
            ny = bt
            ax = br
            ay = bb

        # Line intersection
        dist = []
        for x in range( 0, len( self.limit_x ) ):
            try:
                lx = self.limit_x[x]
                ix, iy = Trig_2D_Points_Lines_Intersection( nx, ny, ax, ay, lx, 0, lx, 1 )
                di = Trig_2D_Points_Distance( px, py, ix, iy )
                dist.append( [ di, ix, iy ] )
            except:
                pass
        for y in range( 0, len( self.limit_y ) ):
            try:
                ly = self.limit_y[y]
                ix, iy = Trig_2D_Points_Lines_Intersection( nx, ny, ax, ay, 0, ly, 1, ly )
                di = Trig_2D_Points_Distance( px, py, ix, iy )
                dist.append( [ di, ix, iy ] )
            except:
                pass
        # Factor
        if len( dist ) > 0:
            dist.sort()
            di = dist[0][0]
            ix = dist[0][1]
            iy = dist[0][2]
            if di <= snap_dist:
                px = ix
                py = iy

        # Delta Scale
        sx = px - nx
        sy = py - ny

        # Scale
        self.Scale_Transform( self.pin_previous, self.pin_index, self.pin_node, nx, ny, sx, sy )
        self.Pin_Draw_QPixmap( self.pin_list, self.pin_index )

        # Snap and Selection
        if self.select_count > 0:
            for i in range( 0, self.pin_count ):
                if self.pin_list[i].select == True:
                    # Read
                    n_bx = self.pin_previous[i].bx
                    n_by = self.pin_previous[i].by
                    n_bl = self.pin_previous[i].bl
                    n_br = self.pin_previous[i].br
                    n_bt = self.pin_previous[i].bt
                    n_bb = self.pin_previous[i].bb

                    # Points
                    if node == 1:
                        n_nx = n_br
                        n_ny = n_bb
                        n_ax = n_bl
                        n_ay = n_bt
                    if node == 2:
                        n_nx = n_bx
                        n_ny = n_bb
                        n_ax = n_bx
                        n_ay = n_bt
                    if node == 3:
                        n_nx = n_bl
                        n_ny = n_bb
                        n_ax = n_br
                        n_ay = n_bt
                    if node == 4:
                        n_nx = n_br
                        n_ny = n_by
                        n_ax = n_bl
                        n_ay = n_by
                    if node == 6:
                        n_nx = n_bl
                        n_ny = n_by
                        n_ax = n_br
                        n_ay = n_by
                    if node == 7:
                        n_nx = n_br
                        n_ny = n_bt
                        n_ax = n_bl
                        n_ay = n_bb
                    if node == 8:
                        n_nx = n_bx
                        n_ny = n_bt
                        n_ax = n_bx
                        n_ay = n_bb
                    if node == 9:
                        n_nx = n_bl
                        n_ny = n_bt
                        n_ax = n_br
                        n_ay = n_bb

                    # Scale
                    self.Scale_Transform( self.pin_previous, i, node, n_nx, n_ny, sx, sy )
                    self.Pin_Draw_QPixmap( self.pin_list, i )
    
    def Scale_Transform( self, previous, index, node, nx, ny, sx, sy ):
        # nx, ny = neutral point
        # sx, sy = scaling point

        # Read
        trz = previous[index].trz
        tsk = previous[index].tsk
        tsw = previous[index].tsw
        tsh = previous[index].tsh
        bx = previous[index].bx
        by = previous[index].by
        bl = previous[index].bl
        br = previous[index].br
        bt = previous[index].bt
        bb = previous[index].bb
        bw = previous[index].bw
        bh = previous[index].bh

        # Factor
        if node in ( 1, 3, 7, 9 ):
            d_delta = Trig_2D_Points_Distance( 0, 0, sx, sy )
            d_box = Trig_2D_Points_Distance( 0, 0, bw, bh )
        if node in ( 2, 8 ):
            d_delta = Trig_2D_Points_Distance( 0, 0, 0, sy )
            d_box = Trig_2D_Points_Distance( 0, 0, 0, bh )
        if node in ( 4, 6 ):
            d_delta = Trig_2D_Points_Distance( 0, 0, sx, 0 )
            d_box = Trig_2D_Points_Distance( 0, 0, bw, 0 )
        factor = d_delta / d_box
        # Dimension with Factor
        fw = bw * factor
        fh = bh * factor

        # Write
        if ( fw != 0 and fh != 0 ):
            self.pin_list[index].tsk = tsk * factor
            self.pin_list[index].tsw = tsw * factor
            self.pin_list[index].tsh = tsh * factor
            if node == 1:
                self.pin_list[index].bx = nx - fw * 0.5
                self.pin_list[index].by = ny - fh * 0.5
                self.pin_list[index].bl = nx - fw
                self.pin_list[index].br = nx
                self.pin_list[index].bt = ny - fh
                self.pin_list[index].bb = ny
            if node == 2:
                self.pin_list[index].bx = nx
                self.pin_list[index].by = ny - fh * 0.5
                self.pin_list[index].bl = nx - fw * 0.5
                self.pin_list[index].br = nx + fw * 0.5
                self.pin_list[index].bt = ny - fh
                self.pin_list[index].bb = ny
            if node == 3:
                self.pin_list[index].bx = nx + fw * 0.5
                self.pin_list[index].by = ny - fh * 0.5
                self.pin_list[index].bl = nx
                self.pin_list[index].br = nx + fw
                self.pin_list[index].bt = ny - fh
                self.pin_list[index].bb = ny
            if node == 4:
                self.pin_list[index].bx = nx - fw * 0.5
                self.pin_list[index].by = ny
                self.pin_list[index].bl = nx - fw
                self.pin_list[index].br = nx
                self.pin_list[index].bt = ny - fh * 0.5
                self.pin_list[index].bb = ny + fh * 0.5
            if node == 6:
                self.pin_list[index].bx = nx + fw * 0.5
                self.pin_list[index].by = ny
                self.pin_list[index].bl = nx
                self.pin_list[index].br = nx + fw
                self.pin_list[index].bt = ny - fh * 0.5
                self.pin_list[index].bb = ny + fh * 0.5
            if node == 7:
                self.pin_list[index].bx = nx - fw * 0.5
                self.pin_list[index].by = ny + fh * 0.5
                self.pin_list[index].bl = nx - fw
                self.pin_list[index].br = nx
                self.pin_list[index].bt = ny
                self.pin_list[index].bb = ny + fh
            if node == 8:
                self.pin_list[index].bx = nx
                self.pin_list[index].by = ny + fh * 0.5
                self.pin_list[index].bl = nx - fw * 0.5
                self.pin_list[index].br = nx + fw * 0.5
                self.pin_list[index].bt = ny
                self.pin_list[index].bb = ny + fh
            if node == 9:
                self.pin_list[index].bx = nx + fw * 0.5
                self.pin_list[index].by = ny + fh * 0.5
                self.pin_list[index].bl = nx
                self.pin_list[index].br = nx + fw
                self.pin_list[index].bt = ny
                self.pin_list[index].bb = ny + fh
            self.pin_list[index].bw = fw
            self.pin_list[index].bh = fh
            self.pin_list[index].area = fw * fh
            self.pin_list[index].perimeter = 2 * fw + 2 * fh
            self.pin_list[index].ratio = fw / fh
    
    def Scale_Factor( self, previous, index, nx, ny, factor ):
        # Read
        trz = previous[index].trz
        tsk = previous[index].tsk
        tsw = previous[index].tsw
        tsh = previous[index].tsh
        bx = previous[index].bx
        by = previous[index].by
        bl = previous[index].bl
        br = previous[index].br
        bt = previous[index].bt
        bb = previous[index].bb
        bw = previous[index].bw
        bh = previous[index].bh

        # Calculation
        n_tsk = tsk * factor
        n_tsw = tsw * factor
        n_tsh = tsh * factor
        n_bx = nx + ( bx - nx ) * factor
        n_by = ny + ( by - ny ) * factor
        n_bl = nx + ( bl - nx ) * factor
        n_br = nx + ( br - nx ) * factor
        n_bt = ny + ( bt - ny ) * factor
        n_bb = ny + ( bb - ny ) * factor
        n_bw = n_br - n_bl
        n_bh = n_bb - n_bt

        # Write
        self.pin_list[index].tsk = n_tsk
        self.pin_list[index].tsw = n_tsw
        self.pin_list[index].tsh = n_tsh
        self.pin_list[index].bx = n_bx
        self.pin_list[index].by = n_by
        self.pin_list[index].bl = n_bl
        self.pin_list[index].br = n_br
        self.pin_list[index].bt = n_bt
        self.pin_list[index].bb = n_bb
        self.pin_list[index].bw = n_bw
        self.pin_list[index].bh = n_bh
        self.pin_list[index].area = n_bw * n_bh
        self.pin_list[index].perimeter = 2 * n_bw + 2 * n_bh
        self.pin_list[index].ratio = n_bw / n_bh
    
    def Scale_Label( self, previous, index, node, dx, dy ):
        # dx, dy =  delta amount

        # Variabels
        snap_dist = 10 / self.cz

        # Read
        bx = previous[index].bx
        by = previous[index].by
        bl = previous[index].bl
        br = previous[index].br
        bt = previous[index].bt
        bb = previous[index].bb
        # Nodes
        if node == 1:
            n_bl = bl + dx
            n_br = br
            n_bt = bt + dy
            n_bb = bb
        if node == 2:
            n_bl = bl
            n_br = br
            n_bt = bt + dy
            n_bb = bb
        if node == 3:
            n_bl = bl
            n_br = br + dx
            n_bt = bt + dy
            n_bb = bb
        if node == 4:
            n_bl = bl + dx
            n_br = br
            n_bt = bt
            n_bb = bb
        if node == 6:
            n_bl = bl
            n_br = br + dx
            n_bt = bt
            n_bb = bb
        if node == 7:
            n_bl = bl + dx
            n_br = br
            n_bt = bt
            n_bb = bb + dy
        if node == 8:
            n_bl = bl
            n_br = br
            n_bt = bt
            n_bb = bb + dy
        if node == 9:
            n_bl = bl
            n_br = br + dx
            n_bt = bt
            n_bb = bb + dy

        # Snap
        sx = 0
        sy = 0
        for j in range( 0, len( self.limit_x ) ):
            xj = self.limit_x[j]
            ll = xj - snap_dist
            lr = xj + snap_dist
            dl = abs( xj - n_bl )
            dr = abs( xj - n_br )
            if node in ( 1, 4, 7 ): # Left
                cl = ( n_bl >= ll and n_bl <= lr )
                if cl == True:
                    sx = xj - n_bl
                    break
            if node in ( 3, 6, 9 ): # Right
                cr = ( n_br >= ll and n_br <= lr )
                if cr == True:
                    sx = xj - n_br
                    break
        for j in range( 0, len( self.limit_y ) ):
            yj = self.limit_y[j]
            lt = yj - snap_dist
            lb = yj + snap_dist
            dt = abs( yj - n_bt )
            db = abs( yj - n_bb )
            if node in ( 1, 2, 3 ): # Top
                ct = ( n_bt >= lt and n_bt <= lb )
                if ct == True:
                    sy = yj - n_bt
                    break
            if node in ( 7, 8, 9 ): # Bottom
                cb = ( n_bb >= lt and n_bb <= lb )
                if cb == True:
                    sy = yj - n_bb
                    break

        # Nodes
        if node == 1:
            n_bl += sx
            n_bt += sy
        if node == 2:
            n_bt += sy
        if node == 3:
            n_br += sx
            n_bt += sy
        if node == 4:
            n_bl += sx
        if node == 6:
            n_br += sx
        if node == 7:
            n_bl += sx
            n_bb += sy
        if node == 8:
            n_bb += sy
        if node == 9:
            n_br += sx
            n_bb += sy
        # Dimensions
        w = n_br - n_bl
        h = n_bb - n_bt
        # Write
        if w > 0:
            self.pin_list[index].bx = n_bl + w * 0.5
            self.pin_list[index].bl = n_bl
            self.pin_list[index].br = n_br
        if h > 0:
            self.pin_list[index].by = n_bt + h * 0.5
            self.pin_list[index].bt = n_bt
            self.pin_list[index].bb = n_bb
        if w < 0:
            w = abs( w )
            self.pin_list[index].bx = n_br + w * 0.5
            self.pin_list[index].bl = n_br
            self.pin_list[index].br = n_bl
        if h < 0:
            h = abs( h )
            self.pin_list[index].by = n_bb + h * 0.5
            self.pin_list[index].bt = n_bb
            self.pin_list[index].bb = n_bt
        if ( w > 0 and h > 0 ):
            self.pin_list[index].bw = w
            self.pin_list[index].bh = h
            self.pin_list[index].area = w * h
            self.pin_list[index].perimeter = 2 * w + 2 * h
            self.pin_list[index].ratio = w / h

    def Rotate_Pin( self, dx ):
        # Angle
        angle = Limit_Angle( dx / 2, 2.5 )
        # Rotate Pin Index
        self.Rotate_Transform( self.pin_previous, self.pin_index, angle )
        self.Pin_Draw_QPixmap( self.pin_list, self.pin_index )

        # Selection
        if self.select_count > 0:
            for i in range( 0, self.pin_count ):
                if self.pin_list[i].select == True:
                    self.Rotate_Transform( self.pin_previous, i, angle )
                    self.Pin_Draw_QPixmap( self.pin_list, i )
    
    def Rotate_Transform( self, previous, index, angle ):
        # Read
        bx = previous[index].bx
        by = previous[index].by
        trz = previous[index].trz
        tsk = previous[index].tsk
        tsw = previous[index].tsw
        tsh = previous[index].tsh

        # Variables
        n_trz = Limit_Looper( trz + angle, 360 )
        # Dimensions
        w2 = tsw * 0.5
        h2 = tsh * 0.5
        raio = tsk * 0.5
        # Points

        cn = [ bx - w2, by ]
        c1 = [ bx - w2, by - h2 ]
        c3 = [ bx + w2, by - h2 ]
        c7 = [ bx - w2, by + h2 ]
        c9 = [ bx + w2, by + h2 ]
        # Angles for Corners
        a_c1 = Trig_2D_Points_Lines_Angle( cn[0], cn[1], bx, by, c1[0], c1[1] )
        a_c3 = Trig_2D_Points_Lines_Angle( cn[0], cn[1], bx, by, c3[0], c3[1] )
        a_c7 = Trig_2D_Points_Lines_Angle( cn[0], cn[1], bx, by, c7[0], c7[1] )
        a_c9 = Trig_2D_Points_Lines_Angle( cn[0], cn[1], bx, by, c9[0], c9[1] )
        # Circle Points
        c1_x, c1_y = Trig_2D_Points_Rotate( bx, by, raio, Limit_Looper( a_c1 + n_trz, 360 ) )
        c3_x, c3_y = Trig_2D_Points_Rotate( bx, by, raio, Limit_Looper( a_c3 + n_trz, 360 ) )
        c7_x, c7_y = Trig_2D_Points_Rotate( bx, by, raio, Limit_Looper( a_c7 + n_trz, 360 ) )
        c9_x, c9_y = Trig_2D_Points_Rotate( bx, by, raio, Limit_Looper( a_c9 + n_trz, 360 ) )
        # New Bounding Box
        n_bl = bx + ( min( c1_x, c3_x, c7_x, c9_x ) - bx )
        n_br = bx + ( max( c1_x, c3_x, c7_x, c9_x ) - bx )
        n_bt = by + ( min( c1_y, c3_y, c7_y, c9_y ) - by )
        n_bb = by + ( max( c1_y, c3_y, c7_y, c9_y ) - by )
        n_bw = ( n_br - n_bl )
        n_bh = ( n_bb - n_bt )

        # Write
        self.pin_list[index].trz = n_trz
        self.pin_list[index].bl = n_bl
        self.pin_list[index].br = n_br
        self.pin_list[index].bt = n_bt
        self.pin_list[index].bb = n_bb
        self.pin_list[index].bw = n_bw
        self.pin_list[index].bh = n_bh
        self.pin_list[index].area = n_bw * n_bh
        self.pin_list[index].perimeter = 2 * n_bw + 2 * n_bh
        self.pin_list[index].ratio = n_bw / n_bh

    def Edit_Pin( self, egs, efx, efy ):
        for i in range( 0, self.pin_count ):
            valid = self.pin_list[i].active == True or self.pin_list[i].select == True
            if valid == True:
                # Write
                self.pin_list[i].egs = egs
                self.pin_list[i].efx = efx
                self.pin_list[i].efy = efy
                # QPixmaps
                self.Pin_Draw_QPixmap( self.pin_list, i )
    
    #endregion
    
    #region Selection
    
    def Selection_Click( self, index ):
        if index != None:
            select = self.pin_list[index].select
            if select == True:
                self.pin_list[index].select = False
            else:
                self.pin_list[index].select = True
        self.Selection_Verify()
    
    def Selection_Box( self, ex, ey, operation ):
        # Variables
        self.select_box = True
        self.select_count = 0

        # Selection
        dist = Trig_2D_Points_Distance( self.ox, self.oy, ex, ey )
        if dist > 10:
            sl = min( ex, self.ox )
            sr = max( ex, self.ox )
            st = min( ey, self.oy )
            sb = max( ey, self.oy )
            for i in range( 0, self.pin_count ):
                dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )
                check = ( dl >= sl ) and ( dr <= sr ) and ( dt >= st ) and ( db <= sb )
                if check == True:
                    if operation in ( "add", "replace" ):
                        self.pin_list[i].select = True
                    if operation == "minus":
                        self.pin_list[i].select = False
                    self.select_count += 1
                if ( check == False and operation == "replace" ):
                    self.pin_list[i].select = False
    
    def Selection_Verify( self ):
        # Variables
        self.state_select = False
        self.select_count = 0

        # Cycle
        for i in range( 0, self.pin_count ):
            if self.pin_list[i].select == True:
                self.state_select = True
                self.select_count += 1

        # Label
        lista = self.Label_List()
        if len( lista ) > 0:
            index = lista[-1]
            self.Label_Panel( index )
        else:
            self.Label_Panel( None )
    
    def Selection_Raise( self ):
        holder = list()
        # Collect Pin
        for pin in self.pin_list:
            if pin.select == True:
                holder.append( pin )
                self.pin_list.remove( pin )
        # Update
        self.pin_list.extend( holder )
        self.Pin_Update()
        del holder
    
    def Selection_All( self ):
        # Variables
        count = self.pin_count
        self.state_select = True
        self.select_count = count
        # Pin
        for i in range( 0, count ):
            self.pin_list[i].select = True
            self.pin_list[i].active = False
    
    def Selection_Clear( self ):
        # Variables
        self.state_select = False
        self.select_box = False
        self.select_count = 0
        # Pin
        for i in range( 0, self.pin_count ):
            self.pin_list[i].select = False
            self.pin_list[i].active = False
    
    def Selection_ZData(self ):
        ci = 1
        self.SIGNAL_PB_MAX.emit( self.select_count )
        self.SIGNAL_PB_VALUE.emit( 0 )
        for i in range( 0, self.pin_count ):
            if self.pin_list[i].select and self.pin_list[i].tipo == "image":
                self.SIGNAL_PB_VALUE.emit( ci )
                QApplication.processEvents()
                self.Pin_ZData(i)
                ci += 1

        self.SIGNAL_PB_MAX.emit( 1 )
        self.SIGNAL_PB_VALUE.emit( 0 )

    #endregion
    
    #region Boards
    
    def Board_Insert( self, lista: list[ReferencePin] ):
        # Insert Pins
        self.pin_list.clear()
        self.pin_count = len( lista )
        for i in range( 0, self.pin_count ):
            pin = lista[i]
            self.pin_list.append( pin )
        # Update
        self.Board_Update()
    
    def Board_Fit( self ):
        # Variables
        self.pin_count = len( self.pin_list )
        if self.pin_count > 0:
            # Variables
            nx, ny = self.Point_Location( 0, 0 )
            mx, my = self.Point_Location( self.ww, self.hh )
            nmx = mx - nx
            nmy = my - ny
            # Board
            board_l, board_r, board_t, board_b, board_w, board_h = self.Board_Limit( "PIN" )
            # Move to Neutral
            for i in range( 0, self.pin_count ):
                px = nx + self.pin_list[i].bl - board_l
                py = ny + self.pin_list[i].bt - board_t
                self.Move_Point( self.pin_list, i, px, py )

            # Board
            board_l, board_r, board_t, board_b, board_w, board_h = self.Board_Limit( "PIN" )
            # Move to Center
            for i in range( 0, self.pin_count ):
                px = self.w2 + ( self.pin_list[i].bl - ( board_l + board_w * 0.5 ) )
                py = self.h2 + ( self.pin_list[i].bt - ( board_t + board_h * 0.5 ) )
                self.Move_Point( self.pin_list, i, px, py )

            self.Camera_Zoom_Fit()

        # Update
        self.Pin_Previous()
        self.Board_Limit( "DRAW" )
        self.update()
    
    def Board_Clear( self ):
        self.pin_list.clear()
        self.Board_Update()
    
    def Board_Update( self ):
        # Pin
        self.pin_count = len( self.pin_list )
        self.Pin_Previous()
        # Camera
        self.Camera_Emit()
        # Board
        self.Board_Limit( "DRAW" )
        self.Board_Render()
        if self.mode_autosave: self.Board_Save()
        # Update
        self.update()
        self.Camera_Grab()
    
    def Board_Limit( self, mode ):
        # Variables
        self.pin_count = len( self.pin_list )
        board_horz = []
        board_vert = []
        # Cycle
        for i in range( 0, self.pin_count ):
            # Read
            if mode == "PIN":
                bl = self.pin_list[i].bl
                br = self.pin_list[i].br
                bt = self.pin_list[i].bt
                bb = self.pin_list[i].bb
            if mode == "DRAW":
                bx, by, bl, br, bt, bb, bw, bh = self.Pin_Draw_Box( i )
            # Board Limit
            board_horz.extend( [ bl, br ] )
            board_vert.extend( [ bt, bb ] )
        if ( self.pin_count > 0 ):
            board_l = min( board_horz )
            board_r = max( board_horz )
            board_t = min( board_vert )
            board_b = max( board_vert )
            board_w = board_r - board_l
            board_h = board_b - board_t
        else:
            board_l = 0
            board_r = 0
            board_t = 0
            board_b = 0
            board_w = 0
            board_h = 0
        # Return
        if mode == "PIN":
            return board_l, board_r, board_t, board_b, board_w, board_h
        if mode == "DRAW":
            self.board_l = board_l
            self.board_r = board_r
            self.board_t = board_t
            self.board_b = board_b
            self.board_w = board_w
            self.board_h = board_h
    
    def Board_Render( self ):
        for i in range( 0, self.pin_count ):
            # Read
            render = self.pin_list[i].render
            # Calculations
            dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )
            draw = not ( ( dl > self.ww ) or ( dr < 0 ) or ( dt > self.hh ) or ( db < 0 ) )
            # Write
            self.pin_list[i].render = draw
            # Update Draw Information
            if ( render == False and draw == True ):
                self.Pin_Draw_QPixmap( self.pin_list, i )
    
    def Board_Focus( self ):
        for i in range( 0, self.pin_count ):
            if self.pin_list[i].render != None:
                self.Pin_Draw_QPixmap( self.pin_list, i )
    
    def Board_Save( self ):
        self.SIGNAL_BOARD_SAVE.emit( self.pin_list )
    
    #endregion

    #region Reset
    
    def Reset_Rotation( self, lista: list[ReferencePin] ):
        self.Pin_Previous()
        for item in lista:
            index = item.index
            angle = -self.pin_list[index].trz
            self.Rotate_Transform( self.pin_previous, index, angle )
            self.Pin_Draw_QPixmap( self.pin_list, index )
    
    def Reset_Scale( self, lista: list[ReferencePin] ):
        # Variables
        side = 200
        # Scaling
        self.Pin_Previous()
        for pin in lista:
            # Read
            index = pin.index
            nx = pin.bl
            ny = pin.bt
            width = pin.bw
            height = pin.bh
            # Calculations
            if width >= height:
                factor = side / height
            else:
                factor = side / width
            # Scale
            self.Scale_Factor( self.pin_previous, index, nx, ny, factor )
            self.Pin_Draw_QPixmap( self.pin_list, index )
    
    #endregion
    
    #region Relative
    
    def Relative_Rebase( self, lista: list[ReferencePin] ):
        # Variables
        count = self.pin_count
        suggestion = ""
        for item in lista:
            path = item.path
            if path != None:
                suggestion = os.path.dirname( path )
                break

        # Select Directory
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.DirectoryOnly )
        directory = file_dialog.getExistingDirectory( self, "Select Directory", suggestion )
        if directory not in [ "", "." ]:
            qdir = QDir( directory )
            qdir.setSorting( QDir.LocaleAware )
            qdir.setFilter( QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot )
            qdir.setNameFilters( self.file_extension )
            files = qdir.entryInfoList()
        else:
            files = []

        # Search Cycles
        path_old = []
        for i in range( 0, self.pin_count ):
            item = self.pin_list[i]
            path = item.path
            qpixmap = QPixmap( path )
            if qpixmap.isNull() == False:
                item.qpixmap = qpixmap
                item.draw = self.Pin_Draw_QPixmap( self.pin_list, i )
            else:
                item.qpixmap = None
                item.draw = None
            path_old.append( path )
        for item in lista:
            tipo = item.tipo
            bx = item.bx
            by = item.by
            path = item.path
            web = item.web
            qpixmap = item.qpixmap
            if path != None:basename = os.path.basename( path )
            elif web != None:basename = os.path.split( urllib.parse.urlparse( web ).path )[1]
            else:basename = None
            if ( tipo == "image" and qpixmap == None ):
                for f in files:
                    fn = f.fileName() # basename
                    fp = os.path.abspath( f.filePath() ) # path
                    if basename == fn and fp not in path_old:
                        pin = InsertablePin(bx + 20, by + 20, fp)
                        self.SIGNAL_PIN_IMAGE.emit( pin )
                        break
            # Selection
            if len( self.pin_list ) > count:
                self.Selection_Clear()
                for i in range( count, len( self.pin_list ) ):
                    self.pin_list[i].select = True
                self.Selection_Verify()
        # Update
        self.Board_Update()
        self.Board_Focus()
    
    def Relative_Delete( self, lista: list[ReferencePin] ):
        self.Pin_Clear()
        for i in range( 0, len( lista ) ):
            self.pin_list.remove( lista[i] )
        self.pin_count = len( self.pin_list )
        if self.pin_count == 0:
            self.Camera_Reset()
        self.Camera_Emit()
        self.Board_Update()
    
    #endregion
    
    #region Camera
    
    def Camera_Reset( self ):
        self.ci = self.cn.index( 1 )
        self.cz = self.cn[self.ci] # Camera Zoom
    
    def Camera_Move( self, ex, ey ):
        dx, dy = self.Point_Deltas( ex, ey )
        for i in range( 0, self.pin_count ):
            self.Move_Transform( self.pin_previous, i, dx, dy )
    
    def Camera_Scale( self, ex, ey ):
        dy = -( ( ey - self.oy ) / 10 )
        if abs( dy ) >= 1:
            self.oy = ey
            self.Camera_Zoom_Step( dy )
    
    def Camera_Zoom_Step( self, step ):
        self.ci = Limit_Range( self.ci + int( step ), 0, len( self.cn ) - 1 )
        self.cz = self.cn[self.ci]
        self.Camera_Emit()
    
    def Camera_Zoom_Fit( self ):
        # Board
        bl, br, bt, bb, bw, bh = self.Board_Limit( "PIN" )
        # Widget
        pl = 0
        pt = 0
        pr = self.ww
        pb = self.hh
        w2 = pr * 0.5
        h2 = pb * 0.5

        # Ratio
        cl = ( pl - w2 ) / ( bl - w2 )
        cr = ( pr - w2 ) / ( br - w2 )
        ct = ( pt - h2 ) / ( bt - h2 )
        cb = ( pb - h2 ) / ( bb - h2 )
        # Zoom
        zoom = []
        if cl > 0:zoom.append( cl )
        if cr > 0:zoom.append( cr )
        if ct > 0:zoom.append( ct )
        if cb > 0:zoom.append( cb )
        zoom = min( zoom )

        # Index
        index = self.cn.index( 1 )
        for i in range( 0, len( self.cn ) ):
            if ( zoom >= self.cn[i] and zoom < self.cn[i+1] ):
                index = i
                break
        # Apply
        self.ci = index
        self.cz = self.cn[self.ci]
        self.Camera_Emit()
    
    def Camera_Signal( self ):
        if ( self.board_w != 0 or self.board_h != 0 ):
            px = ( self.w2 - self.board_l ) / self.board_w
            py = ( self.h2 - self.board_t ) / self.board_h
        else:
            px = 0
            py = 0
        self.SIGNAL_CAMERA.emit( [ px, py ], self.cz, self.pin_count )
    
    def Camera_Emit( self ):
        self.Camera_Signal()
        for i in range( 0, self.pin_count ):
            self.Pin_Draw_QPixmap( self.pin_list, i )
    
    def Camera_Grab( self ):
        try:self.qimage_grab = self.grab().toImage()
        except:pass
    
    #endregion
    
    #region Packer
    
    def Packer_Process( self, method ):
        if self.select_count > 0:
            # Variables
            self.state_pack = True
            # Widget
            self.setEnabled( False )
            self.SIGNAL_PACK_STOP.emit( True )
            # Pin
            self.Selection_Raise()
            # Packer
            thread = True
            if thread == False:self.Packer_Single_Start( method )
            if thread == True:self.Packer_Thread_Start( method )
    
    def Packer_Single_Start( self, method ):
        self.worker_packer = Packer()
        self.worker_packer.run( self, "SINGLE", method )
    
    def Packer_Thread_Start( self, method ):
        # Thread
        self.thread_packer = QThread()
        # Worker
        self.worker_packer = Packer()
        self.worker_packer.moveToThread( self.thread_packer )
        # Thread
        self.thread_packer.started.connect( lambda : self.worker_packer.run( self, "THREAD", method ) )
        self.thread_packer.start()
    
    def Packer_Thread_Quit( self ):
        self.thread_packer.quit()
        self.Packer_Stop()
    
    def Packer_Stop( self ):
        # Variables
        self.state_pack = False
        self.Pin_Previous()
        # Widget
        self.setEnabled( True )
        self.SIGNAL_PACK_STOP.emit( False )
        # Update
        self.update()
    
    #endregion
    
    #region UI
    
    def ProgressBar_Value( self, value ):
        self.SIGNAL_PB_VALUE.emit( value )
    
    def ProgressBar_Maximum( self, maximum ):
        self.SIGNAL_PB_MAX.emit( maximum )
    
    #endregion

    #region Misc



    def Cursor_Shape( self, operation, pin_node ):
        if ( operation == "color_picker" ):
            QApplication.setOverrideCursor( Qt.CrossCursor )
        elif ( operation == "pin_move" or operation == "pin_transform" ):
            if pin_node == 0:
                QApplication.setOverrideCursor( Qt.SizeAllCursor )
            elif pin_node == 5:
                QApplication.setOverrideCursor( Qt.SizeHorCursor )
            elif pin_node in ( 1, 9 ):
                QApplication.setOverrideCursor( Qt.SizeFDiagCursor )
            elif pin_node in ( 3, 7 ):
                QApplication.setOverrideCursor( Qt.SizeBDiagCursor )
            elif pin_node in ( 2, 8 ):
                QApplication.setOverrideCursor( Qt.SizeVerCursor )
            elif pin_node in ( 4, 6 ):
                QApplication.setOverrideCursor( Qt.SizeHorCursor )
        elif ( operation == "camera_move" ):
            QApplication.setOverrideCursor( Qt.SizeAllCursor )
        elif ( operation == "camera_scale" ):
            QApplication.setOverrideCursor( Qt.SizeVerCursor )
        elif ( operation == "select_add" or operation == "select_minus" or operation == "select_replace" ):
            QApplication.restoreOverrideCursor()
        elif ( operation == "drag" ):
            QApplication.setOverrideCursor( Qt.ClosedHandCursor )
        elif ( operation == "drop" ):
            QApplication.setOverrideCursor( Qt.OpenHandCursor )
        else:
            QApplication.restoreOverrideCursor()

    def Context_Menu( self, event ):
        self.state_press = False
        ContextMenu.OpenContextMenu(self, event)

    def Insert_Drag( self, path, clip ):
        if path != None:
            self.drag = True
            NativeActions.Drag_Drop(self, path, clip)
    

    
    #endregion

    #region ModeSets / StateSet / Operations

    def ModeSet_Snap( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_snap

        self.mode_snap = boolean
        if self.state_snap != boolean:
            self.state_snap = boolean
            self.SIGNAL_ACTIONS_UPDATED.emit(  )

    def ModeSet_Base_Reset(self):
        self.mode_base_selectionmove = False
        self.mode_base_cameramove = False
        self.mode_base_camerascale = False
        self.mode_base_selection = False
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_Base_Selection( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_base_selection

        self.mode_base_selection = boolean
        self.mode_base_selectionmove = False
        self.mode_base_cameramove = False
        self.mode_base_camerascale = False
        self.SIGNAL_ACTIONS_UPDATED.emit( )       

    def ModeSet_Base_SelectionMove( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_base_selectionmove

        self.mode_base_selectionmove = boolean
        self.mode_base_selection = False
        self.mode_base_cameramove = False
        self.mode_base_camerascale = False
        self.SIGNAL_ACTIONS_UPDATED.emit( )       


    def ModeSet_Base_CameraMove( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_base_cameramove

        self.mode_base_cameramove = boolean
        self.mode_base_camerascale = False
        self.mode_base_selectionmove = False
        self.mode_base_selection = False
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_Base_CameraScale( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_base_camerascale

        self.mode_base_camerascale = boolean
        self.mode_base_selectionmove = False
        self.mode_base_cameramove = False
        self.mode_base_selection = False
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_Lock( self, boolean: bool = None ):
        if boolean == None:
            boolean = not self.mode_lock

        self.mode_lock = boolean
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_ColorPicker(self, boolean: bool = None):
        if boolean == None:
            boolean = not self.mode_pickcolor

        self.mode_pickcolor = boolean
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_AutoSave(self, boolean: bool = None):
        if boolean == None:
            boolean = not self.mode_autosave

        self.mode_autosave = boolean
        self.SIGNAL_ACTIONS_UPDATED.emit( )

    def ModeSet_Label(self, boolean: bool = None):
        if boolean == None:
            boolean = not self.mode_label

        self.mode_label = boolean
        self.SIGNAL_LABEL_PANEL.emit( self.mode_label )
        self.SIGNAL_ACTIONS_UPDATED.emit()

    def StateSet_Snap( self, boolean: bool = None ):
        if self.mode_snap: return

        if boolean == None:
            boolean = not self.state_snap

        if self.state_snap != boolean:
            self.state_snap = boolean
            self.SIGNAL_ACTIONS_UPDATED.emit(  )

    def Operation_DoubleClick(self, event: QMouseEvent):
        modifiers = event.modifiers()
        buttons = event.buttons()

        operation = None

        match buttons:
            case QtCore.Qt.MouseButton.LeftButton:
                match modifiers:
                    case QtCore.Qt.KeyboardModifier.NoModifier:
                        operation = "preview"
                    case QtCore.Qt.KeyboardModifier.ControlModifier:
                        if self.mode_lock == False: operation ="select_all"
            case QtCore.Qt.MouseButton.RightButton:
                match modifiers:
                    case QtCore.Qt.KeyboardModifier.ControlModifier:
                        if self.mode_lock == False: operation ="select_clear"
        
        return operation

    def Operation_Press(self, event: QMouseEvent):
        modifiers = event.modifiers()
        buttons = event.buttons()
        operation = None

        match buttons:
                case QtCore.Qt.MouseButton.LeftButton:
                    match modifiers:
                        case QtCore.Qt.KeyboardModifier.NoModifier:
                            if self.mode_base_selectionmove:
                                if self.state_focused: operation = "pin_move"
                            elif self.mode_base_cameramove: operation = "camera_move"
                            elif self.mode_base_camerascale: operation = "camera_scale"
                            elif self.mode_pickcolor == True: operation = "color_picker"
                            elif self.mode_base_selection and self.mode_lock == False: operation = "select_add"
                            elif self.mode_lock == False:
                                if self.pin_index == None: operation = "select_replace"
                                elif self.state_focused: operation = "pin_transform"
                                else: operation = "pin_move"
                        case QtCore.Qt.KeyboardModifier.ShiftModifier:
                            operation = "camera_move"
                        case QtCore.Qt.KeyboardModifier.ControlModifier:
                            if self.mode_lock == False: operation = "select_add"
                        case QtCore.Qt.KeyboardModifier.AltModifier:
                            operation = "drag_drop"
                        case ( QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier ):
                            if self.mode_lock == False: operation = "pin_transform"
                        case ( QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier ):
                            operation = "pin_preview"
                case QtCore.Qt.MouseButton.MiddleButton:
                    match modifiers:
                        case QtCore.Qt.KeyboardModifier.NoModifier:
                            operation = "camera_move"
                case QtCore.Qt.MouseButton.RightButton:
                    match modifiers:
                        case QtCore.Qt.KeyboardModifier.NoModifier:
                            operation = "context_menu"
                        case QtCore.Qt.KeyboardModifier.ShiftModifier:
                            operation = "camera_scale"
                        case QtCore.Qt.KeyboardModifier.ControlModifier:
                            if self.mode_lock == False: operation = "select_minus"
                        case QtCore.Qt.KeyboardModifier.AltModifier:
                            operation = "drag_drop"
        
        return operation
            
    def Operation_Release(self):
        return None


    #endregion

    #region Render

    def Render_BoundingBox(self, painter: QPainter, ww: int, hh: int, pin_index: int):
        # Read
        dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( pin_index )
        trz = self.pin_list[pin_index].trz

        # Variables
        dw2 = dw * 0.5
        dh2 = dh * 0.5
        line = 200

        # Bounding Box
        painter.setPen( QPen( self.color_2, 1, Qt.SolidLine ) )
        painter.setBrush( QtCore.Qt.NoBrush )
        painter.drawRect( int( dl ), int( dt ), int( dw ), int( dh ) )

        # Triangle
        min_tri = 20
        if ( ww > min_tri and hh > min_tri ):
            # Variables
            tri = 10
            # Scale 1
            if self.pin_node == 1:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_t1 = QPolygon( [
                QPoint( int( dl ),       int( dt ) ),
                QPoint( int( dl + tri ), int( dt ) ),
                QPoint( int( dl ),       int( dt + tri ) ),
                ] )
            painter.drawPolygon( poly_t1 )
            # scale 3
            if self.pin_node == 3:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_t3 = QPolygon( [
                QPoint( int( dr ),       int( dt ) ),
                QPoint( int( dr ),       int( dt + tri ) ),
                QPoint( int( dr - tri ), int( dt ) ),
                ] )
            painter.drawPolygon( poly_t3 )
            # Scale 7
            if self.pin_node == 7:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_t7 = QPolygon( [
                QPoint( int( dl ),       int( db ) ),
                QPoint( int( dl ),       int( db - tri ) ),
                QPoint( int( dl + tri ), int( db ) ),
                ] )
            painter.drawPolygon( poly_t7 )
            # Scale 9
            if self.pin_node == 9:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_t9 = QPolygon( [
                QPoint( int( dr ),       int( db ) ),
                QPoint( int( dr - tri ), int( db ) ),
                QPoint( int( dr ),       int( db - tri ) ),
                ] )
            painter.drawPolygon( poly_t9 )

        # Squares
        min_sq = 50
        if ( ww > min_sq and hh > min_sq ):
            # Variables
            sq = 5
            # Clip 2
            if self.pin_node == 2:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_s2 = QPolygon( [
                QPoint( int( dl + dw2 - sq ), int( dt ) ),
                QPoint( int( dl + dw2 - sq ), int( dt + sq ) ),
                QPoint( int( dl + dw2 + sq ), int( dt + sq ) ),
                QPoint( int( dl + dw2 + sq ), int( dt ) ),
                ] )
            painter.drawPolygon( poly_s2 )
            # Clip 4
            if self.pin_node == 4:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_s4 = QPolygon( [
                QPoint( int( dl ),      int( dt + dh2 - sq ) ),
                QPoint( int( dl + sq ), int( dt + dh2 - sq ) ),
                QPoint( int( dl + sq ), int( dt + dh2 + sq ) ),
                QPoint( int( dl ),      int( dt + dh2 + sq ) ),
                ] )
            painter.drawPolygon( poly_s4 )
            # Clip 6
            if self.pin_node == 6:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_s6 = QPolygon( [
                QPoint( int( dr ),      int( dt + dh2 - sq ) ),
                QPoint( int( dr - sq ), int( dt + dh2 - sq ) ),
                QPoint( int( dr - sq ), int( dt + dh2 + sq ) ),
                QPoint( int( dr ),      int( dt + dh2 + sq ) ),
                ] )
            painter.drawPolygon( poly_s6 )
            # Clip 8
            if self.pin_node == 8:
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
            poly_s8 = QPolygon( [
                QPoint( int( dl + dw2 - sq ), int( db ) ),
                QPoint( int( dl + dw2 - sq ), int( db - sq ) ),
                QPoint( int( dl + dw2 + sq ), int( db - sq ) ),
                QPoint( int( dl + dw2 + sq ), int( db ) ),
                ] )
            painter.drawPolygon( poly_s8 )

        # Circle
        min_cir = 30
        if ( ww > min_cir and hh > min_cir ):
            cir = 4
            # Clip 5
            if self.pin_node == 5:
                # Lines
                cir_x, cir_y = Trig_2D_Points_Rotate( dl + dw2 , dt + dh2, line, Limit_Looper( trz + 90, 360 ) )
                neu_x, neu_y = Trig_2D_Points_Rotate( dl + dw2 , dt + dh2, line, Limit_Looper( 90, 360 ) )
                painter.setPen( QPen( self.color_2, 4, Qt.SolidLine ) )
                painter.drawLine( int( dl + dw2 ), int( dt + dh2 ), int( cir_x ), int( cir_y ) )
                painter.drawLine( int( dl + dw2 ), int( dt + dh2 ), int( neu_x ), int( neu_y ) )
                painter.setPen( QPen( self.color_1, 2, Qt.SolidLine ) )
                painter.drawLine( int( dl + dw2 ), int( dt + dh2 ), int( cir_x ), int( cir_y ) )
                painter.drawLine( int( dl + dw2 ), int( dt + dh2 ), int( neu_x ), int( neu_y ) )
                # Circle
                painter.setPen( QPen( self.color_2, 1, Qt.SolidLine ) )
                painter.setBrush( QBrush( self.color_blue, Qt.SolidPattern ) )
                painter.drawEllipse( int( dl + dw2 - cir ), int( dt + dh2 - cir ), int( 2 * cir ), int( 2 * cir ) )
            else:
                painter.setBrush( QBrush( self.color_1, Qt.SolidPattern ) )
                painter.drawEllipse( int( dl + dw2 - cir ), int( dt + dh2 - cir ), int( 2 * cir ), int( 2 * cir ) )



    #endregion

    #region Events

    def sizeHint( self ):
        return QtCore.QSize( 5000,5000 )
    
    def keyPressEvent( self, event ):
        # Spacebar
        if event.key() == Qt.Key.Key_Space:
            pass

        # Escape
        if event.key() == Qt.Key.Key_Escape:
            self.Selection_Clear()
            self.update()

        # Delete
        if event.key() == Qt.Key.Key_Delete:
            selection = []
            for i in range( 0, self.pin_count ):
                if self.pin_list[i].select == True:
                    selection.append( self.pin_list[i] )
            self.Relative_Delete( selection )
            self.update()

        # Pack
        if event.key() == Qt.Key.Key_P:
            self.Packer_Process( "GRID" )
    
    def keyReleaseEvent( self, event ):
        # Space
        if event.key() == Qt.Key.Key_Space:
            auto = event.isAutoRepeat()
            if auto == False:
                pass

        # Escape
        if event.key() == Qt.Key.Key_Escape:
            pass

        # Delete
        if event.key() == Qt.Key.Key_Delete:
            pass

    def mousePressEvent( self, event: QMouseEvent ):
        # Variable
        self.state_press = True

        # Event
        ex = event.x()
        ey = event.y()
        self.ox = ex
        self.oy = ey
        self.ex = ex
        self.ey = ey

        # Pin
        self.Pin_Update()
        self.Pin_Index( ex, ey )
        self.Pin_Active( self.pin_index )
        self.Pin_Limits()

        self.operation = self.Operation_Press(event)
        
        match self.operation:
            case "pin_move":
                if self.state_focused and self.select_count <= 0 and self.select_box == False:
                    self.pin_node = self.Pin_Node(self.pin_index)
                else:
                    self.pin_node = 0
            case "color_picker":
                self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.mode_pickcolor )
            case "select_add":
                self.Selection_Click( self.pin_index )
            case "select_minus":
                self.Selection_Click( self.pin_index )
            case "context_menu":
                self.Context_Menu( event )
            case "pin_preview":
                self.Pin_Preview( self.pin_index )

        # Update
        self.Cursor_Shape( self.operation, self.pin_node )
        self.update()
    
    def mouseMoveEvent( self, event ):
        # Event
        ex = event.x()
        ey = event.y()
        self.ex = ex
        self.ey = ey

        if event.modifiers() == QtCore.Qt.NoModifier:
            self.StateSet_Snap( False )
        else:
            self.StateSet_Snap( True )

        match self.operation:
            case "color_picker":
                self.ColorPicker.Event( ex, ey, self.qimage_grab, self.state_press, self.mode_pickcolor )
            case "pin_move":
                dx, dy = self.Point_Deltas( ex, ey )
                self.Move_Pin( dx, dy )
            case "pin_transform":
                self.Pin_Transform( ex, ey, self.pin_node )
            case "camera_move":
                self.Camera_Move( ex, ey ) 
            case "camera_scale":
                self.Camera_Scale( ex, ey )
            case "select_add":
                self.Selection_Box( ex, ey, "add" )
            case "select_minus":
                self.Selection_Box( ex, ey, "minus" )
            case "select_replace":
                self.Selection_Box( ex, ey, "replace" )
            case "drag_drop":
                self.Insert_Drag( self.pin_path, ImageClip(False, 0,0,1,1) )

        # Update
        self.update()
    
    def mouseDoubleClickEvent( self, event ):
        # Event
        ex = event.x()
        ey = event.y()

        operation = self.Operation_DoubleClick(event)

        match operation:
            case "preview":
                self.Pin_Index( ex, ey )
                self.Pin_Preview( self.pin_index )
            case "select_all":
                self.Selection_All()
            case "select_clear":
                self.Selection_Clear()
    
    def mouseReleaseEvent( self, event ):
        # Variables
        self.state_press = False
        self.drop = False
        self.drag = False
        # Color Picker
        self.ColorPicker.Event(self.ex, self.ey, self.qimage_grab, self.state_press, self.mode_pickcolor )
        # Release
        self.releaseEvent()
    
    def releaseEvent( self ):
        # Variables General
        self.operation = self.Operation_Release()
        self.select_box = False
        # Variables Pin
        self.Pin_Update()
        self.Pin_Previous()
        #self.pin_index = None
        self.pin_path = None
        self.pin_basename = None
        self.pin_node = None
        self.pin_count = len( self.pin_list )
        # Variables Limit
        self.limit_x = []
        self.limit_y = []

        # Update
        self.Cursor_Shape( None, None )
        self.Selection_Verify()
        self.Board_Limit( "DRAW" )
        self.Camera_Signal()
        self.update()
        self.Camera_Grab()

    def wheelEvent( self, event ):
        # Variables
        self.state_press = True
        # Camera Zoom
        delta_y = event.angleDelta().y()
        angle = 5
        if delta_y >= angle:
            self.Camera_Zoom_Step( +1 )
        else:
            self.Camera_Zoom_Step( -1 )
        # Update
        self.update()

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
                # Policy
                event.setDropAction( Qt.CopyAction )
                # Position
                pos = event.pos()
                bx, by = self.Point_Location( pos.x(), pos.y() )
                # Data
                mime_data = NativeActions.Drop_Inside( event )
                # Insert Pin
                count = len( mime_data )
                # Board
                self.state_press = True
                # Progress Bar
                self.ProgressBar_Value( 0 )
                self.ProgressBar_Maximum( count )
                # Pin References
                self.drop = False
                for i in range( 0, count ):
                    # Progress Bar
                    self.ProgressBar_Value( i + 1 )
                    QApplication.processEvents()
                    # Pin
                    image_path = mime_data[i]
                    pin = InsertablePin(bx,by,image_path)
                    self.SIGNAL_PIN_IMAGE.emit( pin )
                # Progress Bar
                self.ProgressBar_Value( 0 )
                self.ProgressBar_Maximum( 1 )
                # Board
                self.state_press = False
                self.Board_Update()
            event.accept()
        else:
            event.ignore()
        self.drop = False
        self.drag = False
        self.releaseEvent()
        self.update()

    def showEvent( self, event ):
        self.ColorPicker.Find_Pigment_O()
    
    def enterEvent( self, event ):
        # Variables
        self.state_inside = True
        self.releaseEvent()
        # Keyboard
        self.grabKeyboard()
        # Color Picker
        self.Camera_Grab()
    
    def leaveEvent( self, event ):
        # Variables
        self.state_inside = False
        self.releaseEvent()
        # Keyboard
        self.releaseKeyboard()
        # Camera
        self.Board_Focus()
        # Update
        self.Board_Update()
    
    def closeEvent( self, event ):
        # Database
        self.Database_Close()
        # Qthread
        if self.thread_packer.isRunning():
            self.thread_packer.quit()
        # Garbage
        del self.thread_packer
        del self.worker_packer

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
        self.pin_count = len( self.pin_list )

        # Painter
        painter = QPainter( self )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, True )

        # Background Hover
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( self.color_alpha ) )
        painter.drawRect( 0, 0, ww, hh )

        # Mask
        painter.setClipRect( QRect( int( 0 ), int( 0 ), int( ww ), int( hh ) ), Qt.ReplaceClip )

        """
        # Board Scalling
        painter.setPen( QPen( self.color_1, 1, Qt.SolidLine ) )
        painter.setBrush( QtCore.Qt.NoBrush )
        dl = w2 - w2 * self.cz
        dt = h2 - h2 * self.cz
        dw = ww * self.cz
        dh = hh * self.cz
        dr = dl + dw
        db = dt + dh
        painter.drawRect( int(dl), int(dt), int(dw), int(dh) )
        """

        # Board
        if self.state_press == False:
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QBrush( self.color_shade ) )
            painter.drawRect( int( self.board_l ), int( self.board_t ), int( self.board_w ), int( self.board_h ) )
        # Lost Pins
        if ( self.state_press == False and self.pin_count > 0 ):
            valid = ( self.board_l >= ww ) or ( self.board_r <= 0 ) or ( self.board_t >= hh ) or ( self.board_b <= 0 )
            if valid == True:
                # Variables
                bw2 = self.board_l + self.board_w * 0.5
                bh2 = self.board_t + self.board_h * 0.5
                dot = 5
                # Line
                painter.setPen( QPen( self.color_1, 2, Qt.SolidLine ) )
                painter.setBrush( QtCore.Qt.NoBrush )
                painter.drawLine( int( w2 ), int( h2 ), int( bw2 ), int( bh2 ) )
                # Dot
                painter.setPen( QtCore.Qt.NoPen )
                painter.setBrush( QBrush( self.color_1 ) )
                painter.drawEllipse( int( w2 - dot ), int( h2 - dot ), int( dot * 2 ), int( dot * 2 ) )

        # No References Square
        if ( self.pin_count == 0 and self.drop == False ):
            painter.setPen( QtCore.Qt.NoPen )
            if self.file_path == "":
                painter.setBrush( QBrush( self.color_2 ) )
            else:
                painter.setBrush( QBrush( self.color_1 ) )
            poly_quad = QPolygon( [
                QPoint( int( w2 - ( 0.2 * side ) ), int( h2 - ( 0.2 * side ) ) ),
                QPoint( int( w2 + ( 0.2 * side ) ), int( h2 - ( 0.2 * side ) ) ),
                QPoint( int( w2 + ( 0.2 * side ) ), int( h2 + ( 0.2 * side ) ) ),
                QPoint( int( w2 - ( 0.2 * side ) ), int( h2 + ( 0.2 * side ) ) ),
                ] )
            painter.drawPolygon( poly_quad )

        # Render State
        self.Board_Render()

        # Images and Text
        painter.setBrush( QtCore.Qt.NoBrush )
        for i in range( 0, self.pin_count ):
            render = self.pin_list[i].render
            if render == True:
                # Read
                tipo = self.pin_list[i].tipo
                dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )

                # Render
                if tipo == "image":
                    # Read
                    pack = self.pin_list[i].pack
                    draw = self.pin_list[i].draw

                    # Image
                    if ( pack == True or draw == None ):
                        painter.setPen( QPen( self.color_1, 1, Qt.SolidLine ) )
                        painter.setBrush( QBrush( self.color_2 ) )
                        painter.drawRect( int( dl ), int( dt ), int( dw ), int( dh ) )
                    else:
                        painter.setPen( QtCore.Qt.NoPen )
                        painter.setBrush( QtCore.Qt.NoBrush )
                        painter.drawPixmap( int( dl ), int( dt ), draw )
                    del draw
                if tipo == "label":
                    # Read
                    text = self.pin_list[i].text
                    font = self.pin_list[i].font
                    letter = self.pin_list[i].letter
                    pen = self.pin_list[i].pen
                    bg = self.pin_list[i].bg

                    letter_size = int( letter * self.cz )
                    if letter_size > 0:
                        # Bounding Box
                        box = QRect( int( dl ), int( dt ), int( dw ), int( dh ) )
                        # Highlight
                        painter.setPen( QtCore.Qt.NoPen )
                        painter.setBrush( QBrush( QColor( bg ) ) )
                        painter.drawRect( box )
                        # String
                        painter.setBrush( QtCore.Qt.NoBrush )
                        painter.setPen( QPen( QColor( pen ), 1, Qt.SolidLine ) )
                        qfont = QFont( font )
                        qfont.setPointSizeF( letter_size )
                        painter.setFont( qfont )
                        painter.drawText( box, Qt.AlignCenter, text )
                        # Garbage
                        del qfont

        # Decorators
        if self.mode_pickcolor == False:
            # Dots Over
            if ( self.select_box == True or self.state_select == True ):
                # Variables
                sel_hor = []
                sel_ver = []
                # Painter
                painter.setPen( QtCore.Qt.NoPen )
                painter.setBrush( QBrush( self.color_1, Qt.Dense6Pattern ) )
                # Items
                for i in range( 0, self.pin_count ):
                    render = self.pin_list[i].render
                    if render == True:
                        select_i = self.pin_list[i].select == True
                        pack_i = self.pin_list[i].pack == True
                        if ( select_i == True and pack_i == False ):
                            dx, dy, dl, dr, dt, db, dw, dh = self.Pin_Draw_Box( i )
                            painter.drawRect( int( dl ), int( dt ), int( dw ), int( dh ) )
                            sel_hor.extend( [ dl, dr ] )
                            sel_ver.extend( [ dt, db ] )
                # Selection Square
                painter.setPen( QPen( self.color_1, 1, Qt.SolidLine ) )
                painter.setBrush( QtCore.Qt.NoBrush )
                if ( len( sel_hor ) > 0 and len( sel_ver ) > 0 ):
                    min_x = min( sel_hor )
                    min_y = min( sel_ver )
                    max_x = max( sel_hor )
                    max_y = max( sel_ver )
                    painter.drawRect( int( min_x ), int( min_y ), int( max_x - min_x ), int( max_y - min_y ) )
            # Active Nodes
            if ( self.pin_index != None and self.state_select == False and self.state_pack == False ):
                self.Render_BoundingBox( painter, ww, hh, self.pin_index )

        # Cursor Selection Square
        if ( self.state_press == True and self.select_box == True and self.state_pack == False ):
            painter.setPen( QPen( self.color_1, 2, Qt.SolidLine ) )
            painter.setBrush( QBrush( self.color_1, Qt.Dense7Pattern ) )
            sx = min( self.ox, self.ex )
            sy = min( self.oy, self.ey )
            sw = abs( self.ex - self.ox )
            sh = abs( self.ey - self.oy )
            painter.drawRect( int( sx ), int( sy ), int( sw ), int( sh ) )

        # Pixmap Preview
        if self.pin_preview != None:
            # Back Drop
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QBrush( self.color_backdrop ) )
            painter.drawRect( 0, 0, ww, hh )
            # Pin Preview
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QtCore.Qt.NoBrush )
            preview = self.pin_preview.scaled( int( ww ), int( hh ), Qt.KeepAspectRatio, Qt.FastTransformation )
            px = w2 - preview.width() * 0.5
            py = h2 - preview.height() * 0.5
            painter.drawPixmap( int( px ), int( py ), preview )

        # Display Color Picker
        if self.operation == "color_picker":
            self.ColorPicker.Render( painter, self.ex, self.ey )

        # Drag and Drop Triangle
        if ( self.drop == True and self.drag == False ):
            Paintables.Painter_Triangle( self.color_1, painter, w2, h2, side )

        """
        # Packing Points
        v = 255
        dot = 20 * self.cz
        painter.setPen( QPen( self.color_2, 2, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin ) )
        for item in self.p:
            px = w2 + ( item[0] - w2 ) * self.cz
            py = h2 + ( item[1] - h2 ) * self.cz
            valid = item[2]
            if valid == True:
                painter.setBrush( QBrush( QColor( 0, v, 0 ) ) )
            elif valid == False:
                painter.setBrush( QBrush( QColor( v, 0, 0 ) ) )
            elif valid == None:
                painter.setBrush( QBrush( self.color_1 ) )
            painter.drawEllipse( int( px - dot ), int( py - dot ), int( dot * 2 ), int( dot * 2 ) )

            # # Point location Text
            # painter.setBrush( QtCore.Qt.NoBrush )
            # painter.setPen( QPen( QColor( self.color_1 ), 1, Qt.SolidLine ) )
            # qfont = QFont( self.label_font, int( 8 * self.cz ) )
            # painter.setFont( qfont )
            # box = QRect( int( px ), int( py ), int( 100*self.cz ), int( 20*self.cz ) )
            # text = f"( {item[0]} , {item[1]} )"
            # painter.drawText( box, Qt.AlignCenter, text )
            # # Garbage
            # del qfont
        """
  
    #endregion