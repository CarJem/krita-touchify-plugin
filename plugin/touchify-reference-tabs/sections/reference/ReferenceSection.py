from urllib.parse import urlparse
from krita import *
from ...extensions.calculations import *
from .ReferenceView import ReferenceView
from ...extensions.filetypes import REFERENCE_FILETYPE_DATA
from ...DockerToolbar import DockerToolbar
from .ui.LabelEditor import LabelEditor
from .dataclasses.ReferenceState import ReferenceState
from .dataclasses.ReferencePin import ReferencePin
from ...extensions.commons import Commons
from .ReferenceToolbar import ReferenceToolbar
from .ui.ProgressBar import ProgressBar
from ...dataclasses.images import InsertablePin
from ...extensions.commons import Settings
from ...dataclasses.session import SessionRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...DockerPage import DockerPage

class ReferenceSection(QWidget):

    def __init__(self, parent: "DockerPage"):
        super().__init__(parent)
        self.DockerPage: "DockerPage" = parent
        self.Variables()
        self.Components()
        self.Connections()

    def Canvas(self):
        return self.DockerPage.ParentWidget.docker.canvas()

    def Variables( self ):
        self.ref_state = ReferenceState(self)
    
    def Components( self ):
        self.central_layout = QVBoxLayout(self)
        self.central_layout.setContentsMargins(0,0,0,0)
        self.central_layout.setSpacing(0)
        self.setLayout(self.central_layout)

        self.refrence_container = QWidget( self )
        self.refrence_container.installEventFilter(self)
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

        self.label_editor = LabelEditor( self )
        self.label_editor.setParent(self.footer_panel)
        self.label_editor.setVisible(False)
        self.footer_panel.addWidget(self.label_editor)     

        self.progress_bar = ProgressBar(self.footer_panel)
        self.progress_bar.setVisible(False)
        self.footer_panel.addWidget(self.progress_bar)

        self.tool_panel = ReferenceToolbar(self)
        self.central_layout.addWidget(self.tool_panel)
    
    def Connections( self ):
        qApp.paletteChanged.connect(self.OnEvent_ThemeChanged)
        self.OnEvent_ThemeChanged()

        self.label_editor.SIGNAL_VISIBILITY_CHANGED.connect(self.OnEvent_FooterItemVisibilityChanged)
        self.progress_bar.SIGNAL_VISIBILITY_CHANGED.connect(self.OnEvent_FooterItemVisibilityChanged)
        
        self.ref_state.SIGNAL_PROGRESS_VALUE.connect(self.OnEvent_ProgressValueChanged)
        self.ref_state.SIGNAL_PROGRESS_MAX.connect(self.OnEvent_ProgressMaxChanged)
        self.ref_state.SIGNAL_DATA_LOADED.connect(self.OnEvent_DataLoaded)
        self.ref_state.SIGNAL_DATA_UNLOADED.connect(self.OnEvent_DataUnloaded)
        self.ref_state.SIGNAL_DATA_SAVE.connect(self.OnEvent_SaveDataRequested)

        self.view.SIGNAL_PIN_IMAGE.connect( self.OnEvent_PinImage )
        self.view.SIGNAL_PIN_LABEL.connect( self.OnEvent_PinLabel )
        self.view.SIGNAL_PIN_SAVE.connect( self.OnEvent_PinSave )
        self.view.SIGNAL_BOARD_SAVE.connect( self.OnEvent_SaveDataRecieved)
        self.view.SIGNAL_CAMERA.connect( self.OnEvent_CameraChanged )
        self.view.SIGNAL_PB_VALUE.connect( self.OnEvent_ProgressValueChanged )
        self.view.SIGNAL_PB_MAX.connect( self.OnEvent_ProgressMaxChanged )
        self.view.SIGNAL_LABEL_PANEL.connect( self.OnEvent_LabelEditorRequest )
        self.view.SIGNAL_LABEL_INFO.connect( self.OnEvent_LabelInfoUpdated )
        self.view.SIGNAL_ACTIONS_UPDATED.connect(self.OnEvent_ActionsUpdated)
        self.view.SIGNAL_PREVIEW_REQUESTED.connect(self.OnEvent_PreviewRequested)



    # Actions
    def setToolbarVisibile(self, boolean: bool):
        if boolean:
            self.footer_panel.setVisible(True)
        else:
            self.footer_panel.setVisible(False)

    def Action_PackerStopCycle( self ):
        self.view.Set_Stop_Cycle()

    def Session_Load(self, session: SessionRef):
        match session.path_type:
            case "path":
                self.ref_state.Data_Load(session.path)

    def Session_Save(self):
        return SessionRef(
            path=self.ref_state.path(),
            path_type="path"
        )

    # OnEvent
    def OnEvent_LabelEditorRequest(self, show: bool):
        self.label_editor.setVisible(show)

    def OnEvent_PreviewRequested(self, pixmap: QPixmap):
        self.DockerPage.OpenPreview(pixmap=pixmap)

    def OnEvent_ActionsUpdated(self):
        pass

    def OnEvent_LabelInfoUpdated(self, info: "ReferenceView.LabelInfo"):
        self.label_editor.setInformation(info)

    def OnEvent_CameraChanged( self, ref_position, ref_zoom, len_board ):
        self.ref_state.Data_Update(ref_position, ref_zoom, len_board)
        
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
    
    def OnEvent_DataLoaded(self, new_file: bool):
        if len( self.ref_state.pins() ) > 0:
            self.view.Board_Insert( self.ref_state.pins() )
            self.view.Set_Camera( self.ref_state.pos(), self.ref_state.zoom() )
        elif new_file:
            self.view.Board_Insert( [ ] )
            self.view.Set_Camera( self.ref_state.pos(), self.ref_state.zoom() )

        self.view.setEnabled(True)
        self.view.Set_File_Path( self.ref_state.path() )

    def OnEvent_DataUnloaded(self):
        self.view.Pin_Clear()
        self.view.Selection_Clear()
        self.view.Board_Clear()
        self.view.setEnabled(False)

    def OnEvent_SaveDataRequested(self):
        self.view.Board_Save()

    def OnEvent_SaveDataRecieved(self, list: list[ReferencePin]):
        self.ref_state.Data_Save_St(list)

    def OnEvent_ProgressValueChanged( self, value: int ):
        self.progress_bar.setValue( value )
    
    def OnEvent_ProgressMaxChanged( self, value: int ):
        if value == 1: self.progress_bar.setVisible(False)
        else: self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum( value )

    def OnEvent_FooterItemVisibilityChanged( self ):
        progress_bar = self.progress_bar.isVisible()
        label_editor = self.label_editor.isVisible()
        if progress_bar or label_editor:
            self.footer_panel.setFixedHeight(25)
        else:
            self.footer_panel.setFixedHeight(0)

    def OnEvent_PinImage( self, pin: InsertablePin ):
        if not self.view.isEnabled(): return

        image_path = pin.image_path
        check_html = Commons.Check_Html( image_path )
        if check_html == True:
            self.Pin_Insert( tipo="image", bx=pin.bx, by=pin.by, text=None, path=None, web=image_path )
        else:
            self.Pin_Insert( tipo="image", bx=pin.bx, by=pin.by, text=None, path=image_path, web=None )
    
    def OnEvent_PinLabel( self, pin: InsertablePin ):
        self.Pin_Insert( tipo="label", bx=pin.bx, by=pin.by, text="Text", path=None, web=None )

    def OnEvent_PinSave( self, qpixmap: QPixmap ):
        pin_index = self.view.pin_index

        if self.view.pin_list[pin_index].web != None:
            parsed_url = urlparse(self.view.pin_list[pin_index].web)
            file_name = os.path.basename(parsed_url.path)
        elif self.view.pin_list[pin_index].path != None:
            file_name = os.path.basename(self.view.pin_list[pin_index].path)
        else:
            file_name = "unknown.png"

        file_path = os.path.join(Settings.getFileDialogState(), file_name)
        file_path = Commons.Dialog_Save(self, "Save Pin Location", file_path, "File( *.png *.jpg *.jpeg *.bmp *.ppm *.xpm *.xbm )" )
        if file_path not in [ "", ".", None ]: 
            qpixmap.save( file_path )
            self.view.pin_list[self.view.pin_index].web = None
            self.view.pin_list[self.view.pin_index].path = file_path

    # Event Overrides
    def eventFilter(self, a0: QObject, a1: QEvent):
        if a0 == self.refrence_container and a1.type() == QEvent.Type.Resize:
            self.view.Set_Size(self.refrence_container.width(), self.refrence_container.height() - 4)    
        return super().eventFilter(a0, a1)
    
    def Pin_Insert( self, tipo: str, bx: int, by: int, text: str, path: str, web: str ):
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
            qpixmap = Commons.Download_QPixmap( web )
            try:
                width = int( qpixmap.width() )
                height = int( qpixmap.height() )
            except:
                Commons.Message_Warnning( "ERROR", "access failed")
        # Label
        if tipo == "label":
            qpixmap = None
            width = 200
            height = 100

        # Valid Reference Pin
        if ( width > 0 and height > 0 ):
            # Fit
            if ( tipo == "image" ):
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
            index = len( self.ref_state.pins() )
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
            pin = ReferencePin(
                # ID
                index= index, # integer
                # Type
                tipo= tipo, # string ("image" "label")
                # State
                render= render, # bool
                active= active, # bool
                select= select, # bool
                pack= pack, # bool
                # Transform
                trz= rotation_z, # float
                tsk= scale_constant, # float ( diameter of circle )
                tsw= scale_width, # float ( width with no rotation )
                tsh= scale_height, # float ( height with no rotation )
                # Bound Box
                bx= bx, # float ( center x )
                by= by, # float ( center y )
                bl= bl, # float ( left )
                br= br, # float ( right )
                bt= bt, # float ( top )
                bb= bb, # float ( bottom )
                bw= bw, # float ( width )
                bh= bh, # float ( height )
                # Clip
                cl= cl, # float
                cr= cr, # float
                ct= ct, # float
                cb= cb, # float
                cw= cw, # float
                ch= ch, # float
                # Dimensions
                area= area, # float
                perimeter= perimeter, # float
                ratio= ratio, # float
                # Edits
                egs= edit_grayscale, # bool
                efx= edit_flip_x, # bool
                efy= edit_flip_y, # bool
                # Text
                text= text, # string
                font= font, # string
                letter= letter, # integer
                pen= pen, # string
                bg= bg, # string
                # Pixmap
                path= path, # string
                web= web, # string
                qpixmap= qpixmap, # QPixmap
                draw= draw, # QPixmap
                zdata= zdata, # string of bytes
            )

            # Emit
            self.view.Pin_Insert( pin )

            # Garbage
            del qpixmap, draw, pin
    


