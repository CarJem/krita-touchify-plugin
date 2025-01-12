# Python
# Krita
from krita import *
# PyQt5
# Imagine Board
from .ReferenceCalc import *
from .ReferenceView import ReferenceView
import subprocess
import urllib
from ...DockerToolbar import DockerToolbar

# File Formats
extensions = [
    # Native
    "kra",
    "krz",
    "ora",
    # Static
    "bmp",
    "jpg",
    "jpeg",
    "png",
    "pbm",
    "pgm",
    "ppm",
    "xbm",
    "xpm",
    "tiff",
    "jfif",
    "psd",
    # Vector
    "svg",
    "svgz",
    # Animation
    "gif",
    "webp",
    # Compressed
    "zip",
    ]
# File Sort
file_normal = []
for e in extensions:
    file_normal.append( f"*.{ e }" )
file_backup = []
for e in extensions:
    file_backup.append( f"*.{ e }~" )
# File Type ( Preview )
file_static = []
file_anima = [ "gif", "webp" ]
file_compact = [ "zip" ]
for e in extensions:
    if ( e not in file_anima and e not in file_compact ):
        file_static.append( f"{ e }" )
file_vector = [ "svg", "svgz" ]
file_search = []
for e in extensions:
    if e not in file_compact:
        file_search.append( f"{ e }" )

# Variables
qt_max = 16777215
encode = "utf-8"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...DockerPage import DockerPage

class ReferenceSection(QWidget):
    def __init__(self, parent: "DockerPage"):
        super().__init__(parent)
        self.DockerPage: "DockerPage" = parent
        self.Variables()
        self.Components()

    def canvas(self):
        return self.DockerPage.view_widget.docker.canvas()

    #region Setup Functions

    def Variables( self ):
        # Pykrita
        self.imagine_pyid = "pykrita_imagine_board_docker"

        # Paths
        self.directory_reference = os.path.dirname(os.path.abspath(__file__))

        # State
        self.state_load = False
        self.state_inside = False
        self.state_maximized = False

        # UI
        self.mode_index = 0
        self.search = ""

        # Items
        self.sync_list = "Folder" # "Folder" "Reference" "Document"(recent documents)
        self.sync_type = "Normal" # "Normal" "Backup~"
        self.sync_sort = "Local Aware"
        self.insert_size = False
        self.insert_scale = 1 # Photobask legacy
        self.scale_method = False
        # Lists
        self.list_folder = []
        self.list_krita = []
        self.list_reference = []
        # Folder
        self.folder_path = None
        self.folder_shift = []
        # Files
        self.file_path = [ None ]
        self.file_qpixmap = [ None ]
        self.file_found = False
        self.file_extension = file_normal
        self.file_sort = QDir.LocaleAware

        # Preview
        self.preview_state = "NULL" # "NULL" "STATIC" "ANIM" "COMPACT"
        self.preview_index = 0
        self.preview_max = 0
        self.preview_playpause = True  # True=Play  False=Pause
        # Preview Slidshow
        self.slideshow_sequence = "Linear" # "Linear" "Random"
        self.slideshow_time = 1000
        self.slideshow_play = False
        self.slideshow_lottery = []

        # Grid
        self.grid_size = 200
        self.grid_fit = False

        # Reference
        self.ref_kra = False
        self.ref_import = False
        self.ref_position = [ 1, 1 ]
        self.ref_zoom = 1
        self.ref_board = ""
        self.ref_doc = None
        # Label Picker
        self.picker_mode = None
        self.picker_pen = QColor( 0, 0, 0 )
        self.picker_bg = QColor( 0, 0, 0 )
        self.picker_cancel = QColor( 0, 0, 0 )

        # System
        self.sow_imagine = False
        self.sow_dockers = False
        self.transparent = False

        # Color Picker Module
        self.pigment_o_module = None
        self.pigment_o_pyid = "pykrita_pigment_o_docker"

        # Function>>
        self.function_path_source = None
        self.function_path_destination = None
        self.function_panel_drop = False
        self.function_operation = "NONE"
        self.function_string = []
        self.function_keyword = []
        self.function_number = 1
        self.function_python_index = 0
        self.function_python_path = []
        self.function_python_name = []
        self.function_python_script = ""
    
    def Components( self ):
        self.central_layout = QVBoxLayout(self)
        self.setLayout(self.central_layout)
    
        self.imagine_reference = ReferenceView( self )
        self.imagine_reference.setEnabled(False)
        self.imagine_reference.Set_File_Extension( file_normal )
        # General
        self.imagine_reference.SIGNAL_DRAG.connect( self.Drag_Drop )
        self.imagine_reference.SIGNAL_DROP.connect( self.Drop_Inside )
        # Reference
        self.imagine_reference.SIGNAL_PIN_IMAGE.connect( self.Pin_Image )
        self.imagine_reference.SIGNAL_PIN_LABEL.connect( self.Pin_Label )
        self.imagine_reference.SIGNAL_PIN_SAVE.connect( self.Pin_Save )
        self.imagine_reference.SIGNAL_BOARD_SAVE.connect( self.File_Save_St )
        self.imagine_reference.SIGNAL_CAMERA.connect( self.Reference_Camera )
        # Menu
        self.imagine_reference.SIGNAL_LOCATION.connect( self.File_Location )
        self.imagine_reference.SIGNAL_ANALYSE.connect( self.Color_Analyse )
        self.imagine_reference.SIGNAL_NEW_DOCUMENT.connect( self.Insert_Document )
        self.imagine_reference.SIGNAL_INSERT_LAYER.connect( self.Insert_Layer )
        self.imagine_reference.SIGNAL_INSERT_REFERENCE.connect( self.Insert_Reference )
        # UI
        self.imagine_reference.SIGNAL_PB_VALUE.connect( self.Progress_Value )
        self.imagine_reference.SIGNAL_PB_MAX.connect( self.Progress_Max )
        self.imagine_reference.SIGNAL_PACK_STOP.connect( self.Reference_Pack_Stop )
        self.imagine_reference.SIGNAL_LABEL_PANEL.connect( self.Reference_Label )
        self.imagine_reference.SIGNAL_LABEL_INFO.connect( self.Reference_Information )

        self.central_layout.addWidget(self.imagine_reference)
    
        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tool_panel.setFixedHeight(25)

        self.progress_bar = QProgressBar(self.tool_panel)
        self.progress_bar.setStyleSheet( "{ background-color: rgba( 0, 0, 0, 50 ); }" )
        self.progress_bar.setVisible(False)
        self.tool_panel.addWidget(self.progress_bar)

        self.menu_button = QtWidgets.QToolButton(self.tool_panel)
        self.menu_button.setFixedHeight(25)
        self.menu_button.setText("...")
        self.menu_button.clicked.connect(self.menu_button.showMenu)
        self.tool_panel.addWidget(self.menu_button)     
        
        self.action_menu = QMenu(self.menu_button)
        self.action_menu.addAction("New", self.File_New)
        self.action_menu.addAction("Open", self.File_Open)
        self.action_menu.addAction("Unload", self.File_Unload)
        self.action_menu.addAction("Save", self.File_Save)
        self.action_menu.addAction("Save As", self.File_Save_As)
        self.menu_button.setMenu(self.action_menu)

        self.Theme_Changed()

    #endregion

    #region File Actions

    def File_New( self ):
        ref_board = self.Dialog_Save( "New File Location", "board_000000" )
        if ref_board != None:
            self.ref_board = ref_board
            self.imagine_reference.Board_Clear()
        self.Data_Kritarc()

    def File_Open( self ):
        ref_board = self.Dialog_Load( "Open File Location" )
        if ref_board != None:
            self.EO_Load( ref_board )
            self.imagine_reference.setEnabled(True)
        self.Data_Kritarc()

    def File_Save_St( self, list_reference ):
        if self.imagine_reference.isEnabled():
            # Variabels
            self.list_reference = list_reference
            # Save
            self.EO_Save( self.ref_board )
            self.Data_Kritarc()
            
    def File_Save( self ):
        if self.ref_board != None: 
            self.EO_Save( self.ref_board )
            self.imagine_reference.Board_Save()
        else: self.File_Save_As()

    def File_Save_As( self ):
        ref_board = self.Dialog_Save( "Save File Location", "board_000000" )
        if ref_board != None:
            self.list_reference = self.imagine_reference.pin_list
            self.EO_Save( self.ref_board )
            self.imagine_reference.Board_Save()
            self.Data_Kritarc()

    def File_Unload( self ):
        self.ref_board = None
        self.imagine_reference.Board_Clear()
        self.imagine_reference.setEnabled(False)

    def File_Export( self ):
        export_path = self.Dialog_Save( "Export File Location", "export_000000" )
        self.EO_Export( export_path )

    def File_Download( self ):
        download_folder = self.Dialog_Directory( "Download Folder Location" )
        if download_folder not in [ "", ".", None ]:
            for item in self.list_reference:
                tipo = item["tipo"]
                qpixmap = item["qpixmap"]
                if tipo == "image":
                    # Variables
                    path = item["path"]
                    web = item["web"]
                    if path != None:
                        qpixmap = QPixmap( path )
                        name = os.path.basename( path )
                        save_path = os.path.join( download_folder, name )
                    if web != None:
                        qpixmap = self.Download_QPixmap( web )
                        name = os.path.split( urllib.parse.urlparse( web ).path )[1]
                        save_path = os.path.join( download_folder, name )
                    # Save
                    if os.path.exists( save_path ) == False:
                        qpixmap.save( save_path )
                    else:
                        self.Message_Log( "ERROR", f"Path already exists { save_path }" )

    def File_Location( self, image_path ):
        kernel = str( QSysInfo.kernelType() ) # WINDOWS=winnt & LINUX=linux
        if kernel == "winnt": # Windows
            FILEBROWSER_PATH = os.path.join( os.getenv( 'WINDIR' ), 'explorer.exe' )
            subprocess.run( [ FILEBROWSER_PATH, '/select,', image_path ] )
        elif kernel == "linux": # Linux
            QDesktopServices.openUrl( QUrl.fromLocalFile( os.path.dirname( image_path ) ) )
        elif kernel == "darwin": # MAC
            QDesktopServices.openUrl( QUrl.fromLocalFile( os.path.dirname( image_path ) ) )
        else:
            QDesktopServices.openUrl( QUrl.fromLocalFile( os.path.dirname( image_path ) ) )
        self.Message_Log( "FILE LOCATION", f"{ image_path }" )
    #endregion

    #region Message

    def Message_Log( self, operation, message ):
        pass
        
    def Message_Warnning( self, operation, message ):
        pass

    def Message_Float( self, operation, message, icon ):
        pass

    #endregion


    #region Event Functions

    def resizeEvent(self, a0):
        self.imagine_reference.Set_Size(self.width(), self.height(), False)
        return super().resizeEvent(a0)
    
    #endregion

    #region Drag and Drop
    def Drop_Inside( self, lista ):
        if len( lista ) > 0:
            # Variables
            item = lista[0]
            # Check Source
            check_html = self.Check_Html( item )
            if check_html == True:
                if self.function_panel_drop == False:
                    self.Preview_Internet( item )
                if self.function_panel_drop == True:
                    self.Function_Process( lista )
            else:
                # Checks
                item = os.path.abspath( item )
                check_dir = os.path.isdir( item )
                check_file = os.path.isfile( item )
                # Logic
                if check_dir == True:
                    directory = item
                    basename = None
                if check_file == True:
                    directory = os.path.dirname( item )
                    basename = os.path.basename( item )
                # Open
                if self.function_panel_drop == False: # Preview and Grid Only
                    if self.folder_path != directory:
                        self.Folder_Load( directory, 0 )
                    self.Preview_String( basename )
                if self.function_panel_drop == True:
                    self.Function_Process( lista )
    def Drag_Drop( self, image_path, clip ):
        # New Documents only consider the path so it excludes clip
        qimage = self.Image_Clip( image_path, clip )
        check_vector = image_path.endswith( tuple( file_vector ) )
        if check_vector == True:
            # Read SVG
            svg_shape = ""
            file_item = open( image_path, "r", encoding="UTF-8" )
            for line in file_item:
                svg_shape += line
            # Drag and Drop
            if svg_shape != "":
                # Clipboard
                clipboard = QApplication.clipboard().setText( svg_shape )
                # MimeData
                mimedata = QMimeData()
                url = QUrl().fromLocalFile( image_path )
                mimedata.setUrls( [ url ] )
                mimedata.setText( svg_shape )
                mimedata.setImageData( qimage )
                # Thumbnail
                self.Drag_Thumbnail( qimage, mimedata )
        else:
            if qimage.isNull() == False:
                # Clipboard
                clipboard = QApplication.clipboard().setImage( qimage )
                # MimeData
                mimedata = QMimeData()
                url = QUrl().fromLocalFile( image_path )
                mimedata.setUrls( [ url ] )
                mimedata.setText( image_path )
                mimedata.setImageData( qimage )
                # Thumbnail
                self.Drag_Thumbnail( qimage, mimedata )
    def Drag_Thumbnail( self, qimage, mimedata ):
        # Display
        size = 200
        thumb = QPixmap().fromImage( qimage )
        if thumb.isNull() == False:
            thumb = thumb.scaled( size, size, Qt.KeepAspectRatio, Qt.FastTransformation )
        # Drag
        drag = QDrag( self )
        drag.setMimeData( mimedata )
        drag.setPixmap( thumb )
        drag.setHotSpot( QPoint( int( thumb.width() * 0.5 ), int( thumb.height() * 0.5 ) ) )
        drag.exec( Qt.CopyAction )
    #endregion

    #region Insert / Image Operations
    def Insert_Document( self, image_path, clip ):
        if image_path not in ( "", None ):
            # Create Document
            document = Krita.instance().openDocument( image_path )
            Krita.instance().activeWindow().addView( document )
            w = document.width()
            h = document.height()
            # Crop
            if clip["state"] == True:
                ad = Krita.instance().activeDocument()
                ad.crop( int( w * clip["cl"] ), int( h * clip["ct"] ), int( w * clip["cw"] ), int( h * clip["ch"] ) )
                ad.waitForDone()
                ad.refreshProjection()
                Krita.instance().action('reset_display').trigger()
            # Show Message
            self.Message_Float( "INSERT", "New Document", "document-new" )
        else:
            self.Message_Float( "REPORT", "Null Image", "broken-preset" )
    def Insert_Layer( self, image_path, clip ):
        if image_path not in ( "", None ) and ( self.canvas() is not None ) and ( self.canvas().view() is not None ):
            check_vector = image_path.endswith( tuple( file_vector ) )
            if check_vector == True:
                self.Insert_Vector( image_path )
            else:
                self.Insert_Pixel( image_path, clip )
        else:
            self.Message_Float( "REPORT", "Null Image", "broken-preset" )
    def Insert_Reference( self, image_path, clip ):
        if image_path not in ( "", None ) and ( self.canvas() is not None ) and ( self.canvas().view() is not None ):
            # Image
            qimage = self.Image_Clip( image_path, clip )
            if qimage.isNull() == False:
                # MimeData
                mimedata = QMimeData()
                url = QUrl().fromLocalFile( image_path )
                mimedata.setUrls( [ url ] )
                mimedata.setImageData( qimage )
                mimedata.setData( image_path, image_path.encode() )
                # Clipboard
                clipboard = QApplication.clipboard().setMimeData( mimedata )
                # Place Image
                Krita.instance().action( 'paste_as_reference' ).trigger()
                Krita.instance().activeDocument().refreshProjection()
                # Message
                self.Message_Float( "INSERT", "Reference", "krita_tool_reference_images" )
            else:
                self.Message_Float( "REPORT", "Null Image", "broken-preset" )
        else:
            self.Message_Float( "REPORT", "Null Image", "broken-preset" )
    def Insert_Vector( self, image_path ):
        report = "Vector"
        try:
            # Variables
            basename = os.path.basename( image_path )
            # Read SVG
            svg_shape = ""
            file_item = open( image_path, "r", encoding="UTF-8" )
            for line in file_item:
                svg_shape += line
            # Create Layer
            ad = Krita.instance().activeDocument()
            rn = ad.rootNode()
            vl = ad.createVectorLayer( basename )
            rn.addChildNode( vl, None )
            # Input Shape to Layer
            vl.addShapesFromSvg( svg_shape )
        except Exception as e:
            report = e
        self.Message_Float( "INSERT", report, "vectorLayer" )
    def Insert_Pixel( self, image_path, clip ):
        report = "Pixel"
        try:
            # Variables
            basename = os.path.basename( image_path )
            # Create Layer
            ad = Krita.instance().activeDocument()
            rn = ad.rootNode()
            pl = ad.createNode( basename, "paintLayer" )
            rn.addChildNode( pl, None )
            # Qimage Data
            qimage = self.Image_Clip( image_path, clip )
            ptr = qimage.constBits()
            ptr.setsize( qimage.byteCount() )
            pl.setPixelData( bytes( ptr.asarray() ), 0, 0, qimage.width(), qimage.height() )
            ad.refreshProjection()
        except Exception as e:
            report = e
        self.Message_Float( "INSERT", report, "paintLayer" )
    def Image_Clip( self, image_path, clip ):
        qimage = QImage( image_path )
        if qimage.isNull() == False:
            if clip["state"] == True:
                w = qimage.width()
                h = qimage.height()
                qimage = qimage.copy( int( w * clip["cl"] ), int( h * clip["ct"] ), int( w * clip["cw"] ), int( h * clip["ch"] ) )
            if ( self.insert_size == False ) and ( self.canvas() is not None ) and ( self.canvas().view() is not None ):
                ad = Krita.instance().activeDocument()
                iw = ad.width()
                ih = ad.height()
            else:
                size = max( qimage.size().width(), qimage.size().height() )
                iw = size
                ih = size
            qimage = qimage.scaled( iw * self.insert_scale, ih * self.insert_scale, Qt.KeepAspectRatio, Qt.SmoothTransformation )
        return qimage
    #endregion

    #region Color
    def Color_Analyse( self, qimage ):
        if ( self.pigment_o_module != None and qimage.isNull() == False ):
            report = self.pigment_o_module.API_Image_Analyse( qimage )
            self.Message_Log( "ANALYSE", f"{ report }" )
        else:
            self.Message_Log( "ERROR", "Pigment.O not present" )
    #endregion

    #region Pin
    def Pin_Image( self, pin ):
        image_path = pin["image_path"]
        check_html = self.Check_Html( image_path )
        if check_html == True:
            self.Pin_Insert( tipo="image", bx=pin["bx"], by=pin["by"], text=None, path=None, web=image_path )
        else:
            self.Pin_Insert( tipo="image", bx=pin["bx"], by=pin["by"], text=None, path=image_path, web=None )
    def Pin_Label( self, pin ):
        self.Pin_Insert( tipo="label", bx=pin["bx"], by=pin["by"], text="Text", path=None, web=None )
    def Pin_Insert( self, tipo, bx, by, text, path, web ):
        # Variables
        width = 0
        height = 0

        # Image
        if tipo == "image" and path != None:
            path = os.path.abspath( path )
            qpixmap = QPixmap( path )
            if qpixmap.isNull() == False:
                width = int( qpixmap.width() )
                height = int( qpixmap.height() )
        if tipo == "image" and web != None:
            qpixmap = self.Download_QPixmap( web )
            try:
                width = int( qpixmap.width() )
                height = int( qpixmap.height() )
            except:
                self.Message_Warnning( "ERROR", "access failed")
        # Label
        if tipo == "label":
            qpixmap = None
            width = 200
            height = 100

        # Valid Reference Pin
        if ( width > 0 and height > 0 ):
            # Fit
            if ( tipo == "image" and self.ref_import == False ):
                side = 200
                fx = side / width
                fy = side / height
                if width >= height:
                    sx = width * fy
                    sy = side
                else:
                    sx = side
                    sy = height * fx
                width = int( sx )
                height = int( sy )

            # Variables
            w2 = width * 0.5
            h2 = height * 0.5

            # Bounding Box
            bl = int( bx - w2 )
            br = int( bx + w2 )
            bt = int( by - h2 )
            bb = int( by + h2 )
            bw = int( abs( br - bl ) )
            bh = int( abs( bb - bt ) )

            # Clip
            cl = 0
            cr = 1
            ct = 0
            cb = 1
            cw = 1
            ch = 1

            # ID
            index = len( self.list_reference )
            # State
            render = True
            active = False
            select = False
            pack = False
            # Transform
            rotation_z = 0
            scale_constant = Trig_2D_Points_Distance( 0, 0, bw, bh )
            scale_width = bw
            scale_height = bh
            # Dimensions
            area = bw * bh
            perimeter = ( 2 * bw ) + ( 2 * bh )
            ratio = bw / bh
            pack = False
            # Edits
            edit_grayscale = False
            edit_flip_x = False
            edit_flip_y = False
            # Text
            font = "Consolas"
            letter = 20
            pen = self.color_1.name()
            bg = self.color_2.name()
            # QPixmap & Draw
            if tipo == "image":
                draw = qpixmap.scaled( int( bw * self.ref_zoom ), int( bh * self.ref_zoom ), Qt.IgnoreAspectRatio, Qt.FastTransformation )
            else:
                qpixmap = None
                draw = None
            zdata = None

            # PIN
            pin = {
                # ID
                "index"      : index, # integer
                # Type
                "tipo"      : tipo, # string ("image" "label")
                # State
                "render"     : render, # bool
                "active"     : active, # bool
                "select"     : select, # bool
                "pack"       : pack, # bool
                # Transform
                "trz"        : rotation_z, # float
                "tsk"        : scale_constant, # float ( diameter of circle )
                "tsw"        : scale_width, # float ( width with no rotation )
                "tsh"        : scale_height, # float ( height with no rotation )
                # Bound Box
                "bx"         : bx, # float ( center x )
                "by"         : by, # float ( center y )
                "bl"         : bl, # float ( left )
                "br"         : br, # float ( right )
                "bt"         : bt, # float ( top )
                "bb"         : bb, # float ( bottom )
                "bw"         : bw, # float ( width )
                "bh"         : bh, # float ( height )
                # Clip
                "cl"         : cl, # float
                "cr"         : cr, # float
                "ct"         : ct, # float
                "cb"         : cb, # float
                "cw"         : cw, # float
                "ch"         : ch, # float
                # Dimensions
                "area"       : area, # float
                "perimeter"  : perimeter, # float
                "ratio"      : ratio, # float
                # Edits
                "egs"        : edit_grayscale, # bool
                "efx"        : edit_flip_x, # bool
                "efy"        : edit_flip_y, # bool
                # Text
                "text"       : text, # string
                "font"       : font, # string
                "letter"     : letter, # integer
                "pen"        : pen, # string
                "bg"         : bg, # string
                # Pixmap
                "path"       : path, # string
                "web"        : web, # string
                "qpixmap"    : qpixmap, # QPixmap
                "draw"       : draw, # QPixmap
                "zdata"      : zdata, # string of bytes
                }

            # Emit
            self.imagine_reference.Pin_Insert( pin )

            # Garbage
            del qpixmap, draw, pin
    def Pin_Save( self, qpixmap ):
        # File Dialog
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.AnyFile )
        file_path = file_dialog.getSaveFileName( self, "Save Pin Location", "", "File( *.png *.jpg *.jpeg *.bmp *.ppm *.xpm *.xbm )" )[0]
        if file_path not in [ "", ".", None ]:
            qpixmap.save( file_path )
    #endregion

    #region Dialog
    def Dialog_Load( self, title ):
        if self.ref_board in [ "", ".", None ]:
            directory = self.directory_reference
        else:
            directory = self.ref_board
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.AnyFile )
        file_path = file_dialog.getOpenFileName( self, title, directory, "File( *.eo )" )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        return file_path
    def Dialog_Save( self, title, name ):
        # Variabels
        directory = self.directory_reference
        if ( self.canvas() is not None ) and ( self.canvas().view() is not None ):
            file_name = Krita.instance().activeDocument().fileName()
            directory = os.path.dirname( file_name )
            basename = os.path.basename( file_name )
            name = os.path.splitext( basename )[0]
        directory = os.path.join( directory, f"{ name }.eo")
        # File Dialog
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.AnyFile )
        file_path = file_dialog.getSaveFileName( self, title, directory, "File( *.eo )" )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        return file_path
    def Dialog_Directory( self, title ):
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.DirectoryOnly )
        folder_path = file_dialog.getExistingDirectory( self, title, "" )
        if folder_path in [ "", ".", None ]:
            folder_path = None
        return folder_path
    #endregion

    #region EO file
    def EO_Load( self, path ):
        if ( path not in [ "", ".", None ] and os.path.exists( path ) == True ):
            with open( path, "r", encoding=encode ) as f:
                board = f.readlines()
                self.Data_Load( board, path )
    def EO_Save( self, path ):
        if path not in [ "", ".", None ]:
            data = self.Data_Save()
            with open( path, "w", encoding=encode ) as f:
                f.write( data )
    def EO_Export( self, path ):
        if path not in [ "", ".", None ]:
            data = self.Data_Export()
            with open( path, "w", encoding=encode ) as f:
                f.write( data )
    #endregion

    #region Data
    def Data_Load( self, board, ref_board ):
        # Variables
        count = len( board )
        # Progress Bar
        self.Progress_Value( 0 )
        self.Progress_Max( count )
        # Construct Board
        lista = []
        ref_zoom = 1
        ref_position = [ 0.5, 0.5 ]
        if len( board ) > 0:
            if board[0].startswith( "Imagine Board" ) == True:
                for i in range( 1, count ):
                    try:
                        # Progress Bar
                        self.Progress_Value( i )
                        QApplication.processEvents()
                        # Formating
                        line = board[i]
                        if line.endswith("\n") == True:
                            line = line[:-1]
                        # Evaluation
                        if line == "connect": # Export
                            self.ref_board = ref_board
                        elif line.startswith( "ref_position=" ) == True: # Camera Position
                            n = len( "ref_position=" )
                            ref_position = eval( line[n:] )
                        elif line.startswith( "ref_zoom=" ) == True: # Camera Scale
                            n = len( "ref_zoom=" )
                            ref_zoom = float( line[n:] )
                        else: # Pin
                            line = eval( line )
                            # QPixmap
                            path = line["path"]
                            url = line["web"]
                            zdata = line["zdata"]
                            if path != None: # Local
                                qpixmap = QPixmap( path )
                                if qpixmap.isNull() == False:
                                    line["qpixmap"] = qpixmap
                            elif url != None: # Internet
                                qpixmap = self.Download_QPixmap( url )
                                if qpixmap.isNull() == False:
                                    line["qpixmap"] = qpixmap
                            elif zdata != None: # Import
                                qpixmap = QPixmap()
                                qpixmap.loadFromData( zdata )
                                if qpixmap.isNull() == False:
                                    line["qpixmap"] = qpixmap
                            lista.append( line )
                    except:
                        pass
        if len( lista ) > 0:
            # Preview & Grid
            self.list_reference = lista
            if self.sync_list != "Folder":
                self.Filter_Search()
            # Reference
            self.imagine_reference.Board_Insert( lista )
            self.imagine_reference.Set_Camera( ref_position, ref_zoom )
        # Progress Bar
        self.Progress_Value( 0 )
        self.Progress_Max( 1 )
    def Data_Save( self ):
        # Header
        data = "Imagine Board"
        # Type of save
        data += f"\nconnect"
        # Camera
        data += f"\nref_position={ self.ref_position }"
        data += f"\nref_zoom={ self.ref_zoom }"
        for item in self.list_reference:
            # Clean
            item["qpixmap"] = None
            item["draw"] = None
            item["zdata"] = None
            # String
            data += f"\n{ item }"
        return data
    def Data_Export( self ):
        # Header
        data = "Imagine Board"
        # Type of save
        data += f"\ndata"
        # Camera
        data += f"\nref_position={ self.ref_position }"
        data += f"\nref_zoom={ self.ref_zoom }"
        for item in self.list_reference:
            # ZData
            path = item["path"]
            web = item["web"]
            if path != None:
                item["zdata"] = self.Bytes_Python( path )
            elif web != None:
                item["zdata"] = self.Download_Data( web )
            else:
                item["zdata"] = None
            # Clean
            item["qpixmap"] = None
            item["draw"] = None
            # String
            data += f"\n{ item }"
        return data
    def Data_Kritarc( self ):
        self.imagine_reference.Set_File_Path( self.ref_board )
        Krita.instance().writeSetting( "Imagine Board", "ref_board", str( self.ref_board ) )
    #endregion

    #region Label Operations
    def Reference_Label( self, boolean ):
        if boolean == True:
            value = qt_max
        else:
            value = 0
        #self.layout.label_panel.setMaximumHeight( value )
        pass
    def LabelPanel_Shrink( self ):
        #self.layout.label_panel.setMaximumHeight( 0 )
        pass
    def Reference_Information( self, info ):
        # Variables
        info_text = info["text"]
        info_font = info["font"]
        info_letter = info["letter"]
        info_pen = info["pen"]
        info_bg = info["bg"]
        # Signals
        #self.layout.label_font.blockSignals( True )
        #self.layout.label_letter.blockSignals( True )
        #self.layout.label_pen.blockSignals( True )
        #self.layout.label_bg.blockSignals( True )
        # ToolTip
        #self.layout.label_font.setCurrentText( info_font )
        #self.layout.label_letter.setValue( info_letter )
        #self.layout.label_pen.setToolTip( info_pen )
        #self.layout.label_bg.setToolTip( info_bg )
        # Modules
        #self.block_pen.Set_Color( QColor( info_pen ) )
        #self.block_bg.Set_Color( QColor( info_bg ) )
        # Signals
        #self.layout.label_font.blockSignals( False )
        #self.layout.label_letter.blockSignals( False )
        #self.layout.label_pen.blockSignals( False )
        #self.layout.label_bg.blockSignals( False )
    def Label_Text( self ):
        previous = self.imagine_reference.Get_Label_Infomation()
        if previous != None:
            string, ok = QInputDialog.getMultiLineText( self, "Imagine Board", "Input Text", previous["text"] )
            if ( ok == True and string != None ):
                self.imagine_reference.Set_Label_Text( string )
    def Label_Font( self, font ):
        self.imagine_reference.Set_Label_Font( font )
    def Label_Letter( self, letter ):
        self.imagine_reference.Set_Label_Letter( letter )
    #endregion

    #region Packer
    def Reference_Pack_Stop( self, boolean ):
        pass
        #if boolean == True:
            #self.layout.stop.setIcon( self.qicon_stop_abort )
        #elif boolean == False:
            #self.layout.stop.setIcon( self.qicon_stop_idle )
    def Reference_Stop_Cycle( self ):
        self.imagine_reference.Set_Stop_Cycle()
    #endregion

    #region Camera
    def Reference_Camera( self, ref_position, ref_zoom, len_board ):
        # Variables
        self.ref_position = ref_position
        self.ref_zoom = ref_zoom
        # Interface
        #self.layout.zoom.setText( f"z{ ref_zoom }:{ len_board }" )
        # Save
        Krita.instance().writeSetting( "Imagine Board", "ref_position", str( self.ref_position ) )
        Krita.instance().writeSetting( "Imagine Board", "ref_zoom", str( self.ref_zoom ) )
    #endregion
    
    #region Theme
    def Theme_Changed( self ):
        # Krita Theme
        theme_value = QApplication.palette().color( QPalette.Window ).value()
        if theme_value > 128:
            self.color_1 = QColor( "#191919" )
            self.color_2 = QColor( "#e5e5e5" )
        else:
            self.color_1 = QColor( "#e5e5e5" )
            self.color_2 = QColor( "#191919" )
        # Update
        self.imagine_reference.Set_Theme( self.color_1, self.color_2 )
    #endregion

    #region Internet
    def Download_QPixmap( self, url ):
        data = self.Download_Data( url )
        try:
            qpixmap = QPixmap()
            qpixmap.loadFromData( data )
        except:
            qpixmap = None
        return qpixmap
    def Download_Data( self , url ):
        try:
            request = urllib.request.Request( url, headers={ "User-Agent": "Mozilla/5.0" } )
            response = urllib.request.urlopen( request )
            data = response.read()
        except:
            data = None
        return data
    def Check_Html( self, url ):
        boolean = False
        result = urllib.parse.urlparse( url )
        scheme = result.scheme
        if scheme == "https":
            boolean = True
        return boolean
    #endregion
    
    #region Progress Bar
    def Progress_Value( self, value ):
        self.progress_bar.setValue( value )
    def Progress_Max( self, value ):
        if value == 1: self.progress_bar.setVisible(False)
        else: self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum( value )
    #endregion
