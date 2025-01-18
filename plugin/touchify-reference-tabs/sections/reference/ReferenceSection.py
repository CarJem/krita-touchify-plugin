from krita import *
from .ReferenceCalc import *
from .ReferenceView import ReferenceView
import subprocess
import urllib
from ...classes.common import REFERENCE_FILETYPE_DATA
from ...DockerToolbar import DockerToolbar
from .ReferenceLabelEditor import ReferenceLabelEditor
from .ReferenceSaveState import ReferenceSaveState
from .ReferencePin import ReferencePin
from .ReferenceCommons import ReferenceCommons

# Variables
EO_ENCODING = "utf-8"

from ...classes.settings import Settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...DockerPage import DockerPage

class ReferenceSection(QWidget):

    class ReferenceProgressBar(QProgressBar):
        SIGNAL_VISIBILITY_CHANGED = pyqtSignal()
        def __init__(self, parent: QWidget = None):
            super().__init__(parent)

        def hideEvent(self, a0):
            self.SIGNAL_VISIBILITY_CHANGED.emit()
            return super().hideEvent(a0)
        
        def showEvent(self, a0):
            self.SIGNAL_VISIBILITY_CHANGED.emit()
            return super().showEvent(a0)

    def __init__(self, parent: "DockerPage"):
        super().__init__(parent)
        self.DockerPage: "DockerPage" = parent
        self.Variables()
        self.Components()
        self.Connections()
        self.OnEvent_ThemeChanged()

    def canvas(self):
        return self.DockerPage.view_widget.docker.canvas()

    #region Setup Functions

    def Variables( self ):
        # Paths
        self.directory_reference = Settings.getFileDialogState()

        # Items
        self.sync_list = "Folder" # "Folder" "Reference" "Document"(recent documents)
        self.insert_size = False
        self.insert_scale = 1 # Photobask legacy
        self.scale_method = False
        # Folder
        self.folder_path = None
        self.folder_shift = []


        self.ref_state = ReferenceSaveState(self)

        # Reference
        self.ref_kra = False
        self.ref_import = False
        self.ref_doc = None


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
        self.central_layout.setContentsMargins(0,0,0,0)
        self.central_layout.setSpacing(0)
        self.setLayout(self.central_layout)

        self.refrence_container = QWidget( self )
        self.refrence_container.setContentsMargins(0,0,0,4)
        self.central_layout.addWidget(self.refrence_container)
    
        self.view = ReferenceView( self.refrence_container )
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setEnabled(False)
        self.view.Set_File_Extension( REFERENCE_FILETYPE_DATA["file_normal"] )

        self.footer_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.footer_panel.setContentsMargins(0, 0 ,0, 4)
        self.footer_panel.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_panel.setFixedHeight(0)
        self.central_layout.addWidget(self.footer_panel)

        self.label_editor = ReferenceLabelEditor( self )
        self.label_editor.SIGNAL_VISIBILITY_CHANGED.connect(self.Footer_Update)
        self.label_editor.setParent(self.footer_panel)
        self.label_editor.setVisible(False)
        self.footer_panel.addWidget(self.label_editor)     

        self.progress_bar = self.ReferenceProgressBar(self.footer_panel)
        self.progress_bar.SIGNAL_VISIBILITY_CHANGED.connect(self.Footer_Update)
        self.progress_bar.setStyleSheet( "{ background-color: rgba( 0, 0, 0, 50 ); }" )
        self.progress_bar.setVisible(False)
        self.footer_panel.addWidget(self.progress_bar)

        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.widgetLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tool_panel.setFixedHeight(25)

        self.label_editor_button = QtWidgets.QToolButton(self.tool_panel)
        self.label_editor_button.setCheckable(True)
        self.label_editor_button.setChecked(False)
        self.label_editor_button.setIcon(Krita.instance().icon("draw-text"))
        self.tool_panel.addWidget(self.label_editor_button)

        self.color_picker_button = QtWidgets.QToolButton(self.tool_panel)
        self.color_picker_button.setCheckable(True)
        self.color_picker_button.setChecked(False)
        self.color_picker_button.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        self.tool_panel.addWidget(self.color_picker_button)

        self.snap_button = QtWidgets.QToolButton(self.tool_panel)
        self.snap_button.setCheckable(True)
        self.snap_button.setChecked(False)
        self.snap_button.setIcon(Krita.instance().icon("chain-broken-icon"))
        self.tool_panel.addWidget(self.snap_button)
    
    def Connections( self ):
        self.color_picker_button.clicked.connect(self.Action_ColorPickerToggle)
        self.label_editor_button.clicked.connect(self.Action_LabelEditorToggle)
        self.snap_button.clicked.connect(self.Action_SnapToggle)

        self.ref_state.SIGNAL_PROGRESS_VALUE.connect(self.Progress_Value)

        self.view.SIGNAL_DRAG.connect( self.OnEvent_DragDrop )
        self.view.SIGNAL_DROP.connect( self.OnEvent_DropInside )
        self.view.SIGNAL_PIN_IMAGE.connect( self.Pin_Image )
        self.view.SIGNAL_PIN_LABEL.connect( self.Pin_Label )
        self.view.SIGNAL_PIN_SAVE.connect( self.Pin_Save )
        self.view.SIGNAL_BOARD_SAVE.connect( self.OnEvent_SavePinsRequested )
        self.view.SIGNAL_CAMERA.connect( self.OnEvent_CameraChanged )
        self.view.SIGNAL_LOCATION.connect( self.OnEvent_FileLocationRequested )
        self.view.SIGNAL_ANALYSE.connect( self.OnEvent_ColorAnalyseRequested )
        self.view.SIGNAL_NEW_DOCUMENT.connect( self.Insert_Document )
        self.view.SIGNAL_INSERT_LAYER.connect( self.Insert_Layer )
        self.view.SIGNAL_INSERT_REFERENCE.connect( self.Insert_Reference )
        self.view.SIGNAL_PB_VALUE.connect( self.Progress_Value )
        self.view.SIGNAL_PB_MAX.connect( self.Progress_Max )
        self.view.SIGNAL_PACK_STOP.connect( self.OnEvent_ReferencePackStop )
        self.view.SIGNAL_LABEL_PANEL.connect( self.OnEvent_LabelEditorRequest )
        self.view.SIGNAL_LABEL_INFO.connect( self.label_editor.setInformation )
        self.view.SIGNAL_ACTIONS_UPDATED.connect(self.OnEvent_ActionsUpdated)
        self.view.SIGNAL_SNAP_TOGGLED.connect(self.OnEvent_SnapToggled)
        self.view.SIGNAL_PREVIEW_REQUESTED.connect(self.OnEvent_PreviewRequested)

    #endregion

    #region Actions

    def Action_LabelEditorToggle(self):
        self.view.state_label = not self.view.state_label
        self.label_editor_button.setChecked(self.view.state_label)
        self.label_editor.setVisible(self.view.state_label)

    def Action_ColorPickerToggle(self):
        self.view.state_pickcolor = not self.view.state_pickcolor
        self.color_picker_button.setChecked(self.view.state_pickcolor)

    def Action_SnapToggle(self):
        self.view.Snap_Hold(not self.view.state_snaphold)
    
    def Action_CreateFile( self ):
        ref_board = self.Dialog_Save( "New File Location", "board_000000" )
        if ref_board != None:
            self.ref_state.ref_board = ref_board
            self.Data_Load( ref_board )
            self.view.setEnabled(True)
            self.view.Set_File_Path( self.ref_state.ref_board )

    def Action_OpenFile( self ):
        ref_board = self.Dialog_Load( "Open File Location" )
        if ref_board != None:
            self.ref_state.ref_board = ref_board
            self.Data_Load( ref_board )
            self.view.setEnabled(True)
            self.view.Set_File_Path( self.ref_state.ref_board )
            
    def Action_SaveFile( self ):
        if self.ref_state.ref_board != None: 
            self.view.Board_Save()
        else: self.Action_SaveFileAs()

    def Action_SaveFileAs( self ):
        ref_board = self.Dialog_Save( "Save File Location", "board_000000" )
        if ref_board != None:
            self.ref_state.ref_board = ref_board
            self.view.Board_Save()
            self.view.Set_File_Path( self.ref_state.ref_board )

    def Action_UnloadFile( self ):
        self.view.Pin_Clear()
        self.view.Selection_Clear()
        self.view.Board_Clear()
        self.view.setEnabled(False)
        self.ref_state.ref_board = None

    def Action_ExportFile( self ):
        export_path = self.Dialog_Save( "Export File Location", "export_000000" )
        self.Data_Export( export_path )

    def Action_FileDownload( self ):
        download_folder = self.Dialog_Directory( "Download Folder Location" )
        if download_folder not in [ "", ".", None ]:
            for item in self.ref_state.ref_pins:
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
                        qpixmap = ReferenceCommons.Download_QPixmap( web )
                        name = os.path.split( urllib.parse.urlparse( web ).path )[1]
                        save_path = os.path.join( download_folder, name )
                    # Save
                    if os.path.exists( save_path ) == False:
                        qpixmap.save( save_path )
                    else:
                        self.Message_Log( "ERROR", f"Path already exists { save_path }" )

    #endregion

    #region OnEvent

    def OnEvent_LabelEditorRequest(self, show: bool):
        self.label_editor.setVisible(show)

    def OnEvent_PreviewRequested(self, pixmap: QPixmap):
        self.DockerPage.openPreview(pixmap=pixmap)

    def OnEvent_SnapToggled(self, boolean: bool):
        self.snap_button.setChecked(boolean)
        if boolean: self.snap_button.setIcon(Krita.instance().icon("chain-icon"))
        else: self.snap_button.setIcon(Krita.instance().icon("chain-broken-icon"))

    def OnEvent_ActionsUpdated(self):
        self.color_picker_button.setChecked(self.view.state_pickcolor)
        self.label_editor_button.setChecked(self.view.state_label)
        self.auto_save_checkbox.setChecked(self.view.state_autosave)

    def OnEvent_CameraChanged( self, ref_position, ref_zoom, len_board ):
        self.ref_state.ref_position = ref_position
        self.ref_state.ref_zoom = ref_zoom

    def OnEvent_ColorAnalyseRequested( self, qimage ):
        if ( self.pigment_o_module != None and qimage.isNull() == False ):
            report = self.pigment_o_module.API_Image_Analyse( qimage )
            self.Message_Log( "ANALYSE", f"{ report }" )
        else:
            self.Message_Log( "ERROR", "Pigment.O not present" )

    def OnEvent_FileLocationRequested( self, image_path ):
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
    
    def OnEvent_SavePinsRequested( self, list_reference ):
        if self.view.isEnabled():
            self.ref_state.ref_pins = list_reference
            self.Data_Save( self.ref_state.ref_board )
            self.view.Set_File_Path( self.ref_state.ref_board )

    def OnEvent_DropInside( self, lista ):
        if len( lista ) > 0:
            # Variables
            item = lista[0]
            # Check Source
            check_html = ReferenceCommons.Check_Html( item )
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
    
    def OnEvent_DragDrop( self, image_path, clip ):
        def Drag_Thumbnail( qimage, mimedata ):
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

        # New Documents only consider the path so it excludes clip
        qimage = ReferenceCommons.Image_Clip( image_path, clip )
        check_vector = image_path.endswith( tuple( REFERENCE_FILETYPE_DATA["file_vector"] ) )
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
                Drag_Thumbnail( qimage, mimedata )
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
                Drag_Thumbnail( qimage, mimedata )

    def OnEvent_ThemeChanged( self ):
        # Krita Theme
        theme_value = QApplication.palette().color( QPalette.Window ).value()
        if theme_value > 128:
            self.color_1 = QColor( "#191919" )
            self.color_2 = QColor( "#e5e5e5" )
        else:
            self.color_1 = QColor( "#e5e5e5" )
            self.color_2 = QColor( "#191919" )
        # Update
        self.view.Set_Theme( self.color_1, self.color_2 )

    def OnEvent_ReferencePackStop( self, boolean ):
        pass
        #if boolean == True:
            #self.layout.stop.setIcon( self.qicon_stop_abort )
        #elif boolean == False:
            #self.layout.stop.setIcon( self.qicon_stop_idle )

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
        self.view.Set_Size(self.refrence_container.width(), self.refrence_container.height() - 4, False)
        return super().resizeEvent(a0)
    
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
            check_vector = image_path.endswith( tuple( REFERENCE_FILETYPE_DATA["file_vector"] ) )
            if check_vector == True:
                self.Insert_Vector( image_path )
            else:
                self.Insert_Pixel( image_path, clip )
        else:
            self.Message_Float( "REPORT", "Null Image", "broken-preset" )
    
    def Insert_Reference( self, image_path, clip ):
        if image_path not in ( "", None ) and ( self.canvas() is not None ) and ( self.canvas().view() is not None ):
            # Image
            qimage = ReferenceCommons.Image_Clip( image_path, clip )
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
            qimage = ReferenceCommons.Image_Clip( image_path, clip )
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
    
    def Pin_Image( self, pin: dict ):
        image_path = pin["image_path"]
        check_html = ReferenceCommons.Check_Html( image_path )
        if check_html == True:
            self.Pin_Insert( tipo="image", bx=pin["bx"], by=pin["by"], text=None, path=None, web=image_path )
        else:
            self.Pin_Insert( tipo="image", bx=pin["bx"], by=pin["by"], text=None, path=image_path, web=None )
    
    def Pin_Label( self, pin: dict ):
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
            qpixmap = ReferenceCommons.Download_QPixmap( web )
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
            index = len( self.ref_state.ref_pins )
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
                draw = qpixmap.scaled( int( bw * self.ref_state.ref_zoom ), int( bh * self.ref_state.ref_zoom ), Qt.IgnoreAspectRatio, Qt.FastTransformation )
            else:
                qpixmap = None
                draw = None
            zdata = None

            # PIN
            pin = ReferencePin(**{
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
            })

            # Emit
            self.view.Pin_Insert( pin )

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

    #region Dialog & Data Loading/Saving

    def Dialog_Load( self, title ):
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.AnyFile )
        file_path = file_dialog.getOpenFileName( self, title, Settings.getFileDialogState(), "File( *.eo )" )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        else: Settings.setFileDialogState(os.path.dirname(file_path))
        return file_path
    
    def Dialog_Save( self, title, name ):
        # Variabels
        directory = os.path.join(  Settings.getFileDialogState(), f"{ name }.eo")
        # File Dialog
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.AnyFile )
        file_path = file_dialog.getSaveFileName( self, title,  Settings.getFileDialogState(), "File( *.eo )" )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        else: Settings.setFileDialogState(os.path.dirname(file_path))
        return file_path
    
    def Dialog_Directory( self, title ):
        directory = Settings.getFileDialogState()
        file_dialog = QFileDialog( QWidget( self ) )
        file_dialog.setFileMode( QFileDialog.DirectoryOnly )
        folder_path = file_dialog.getExistingDirectory( self, title, directory )
        if folder_path in [ "", ".", None ]:
            folder_path = None
        else: Settings.setFileDialogState(os.path.dirname(folder_path))
        return folder_path

    def Data_Load( self, path: str, new_file: bool = False ):
        board = None
        ref_board = None

        if ( path not in [ "", ".", None ] and os.path.exists( path ) == True ):
            with open( path, "r", encoding=EO_ENCODING ) as f:
                board = f.readlines()
                ref_board = path

        if (board == None or ref_board == None) and not new_file: return

        self.Progress_Value( 0 )
        self.Progress_Max( len( board ) )

        self.ref_state.load(board, ref_board, new_file)
    
        if len( self.ref_state.ref_pins ) > 0:
            self.view.Board_Insert( self.ref_state.ref_pins )
            self.view.Set_Camera( self.ref_state.ref_position, self.ref_state.ref_zoom )
        elif new_file:
            self.view.Board_Insert( [ ] )
            self.view.Set_Camera( self.ref_state.ref_position, self.ref_state.ref_zoom )


        self.Progress_Value( 0 )
        self.Progress_Max( 1 )
    
    def Data_Save( self, path ):
        if path not in [ "", ".", None ]:
            data = self.ref_state.save()
            with open( path, "w", encoding=EO_ENCODING ) as f:
                f.write( data )
    
    def Data_Export( self, path ):
        if path not in [ "", ".", None ]:
            data = self.ref_state.export()
            with open( path, "w", encoding=EO_ENCODING ) as f:
                f.write( data )
    
    #endregion

    #region Misc

    def Fullscreen_Set(self, boolean: bool):
        if boolean:
            self.footer_panel.setVisible(False)
        else:
            self.footer_panel.setVisible(True)

    def Packer_Stop_Cycle( self ):
        self.view.Set_Stop_Cycle()
    
    def Footer_Update( self ):
        progress_bar = self.progress_bar.isVisible()
        label_editor = self.label_editor.isVisible()
        if progress_bar or label_editor:
            #self.footer_panel.setVisible(True)
            self.footer_panel.setFixedHeight(25)
        else:
            #self.footer_panel.setVisible(True)
            self.footer_panel.setFixedHeight(0)
            

    def Progress_Value( self, value ):
        self.progress_bar.setValue( value )
    
    def Progress_Max( self, value ):
        if value == 1: self.progress_bar.setVisible(False)
        else: self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum( value )
    
    #endregion
