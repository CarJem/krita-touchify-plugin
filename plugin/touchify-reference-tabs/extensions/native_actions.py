import subprocess
from krita import *
from touchify.src.api_krita import KritaAPI
from .filetypes import REFERENCE_FILETYPE_DATA
from ..dataclasses.images import ImageClip
from .commons import Commons

class NativeActions:

    __Canvas: Canvas = None
    
    @staticmethod
    def OnEvent_CanvasChanged(canvas: Canvas):
        NativeActions.__Canvas = canvas

    @staticmethod
    def File_Location( image_path: str):
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
        Commons.Message_Log( "FILE LOCATION", f"{ image_path }" )

    @staticmethod
    def Drag_Drop( self, image_path: str, clip: ImageClip):
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
        qimage = NativeActions.Image_Clip( image_path, clip )
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

    @staticmethod
    def Image_Clip( image_path: str, clip: ImageClip, insert_size: bool = False, insert_scale: int = 1 ):
        canvas = NativeActions.__Canvas
        qimage = QImage( image_path )
        if qimage.isNull() == False:
            if clip.state == True:
                w = qimage.width()
                h = qimage.height()
                qimage = qimage.copy( int( w * clip.cl ), int( h * clip.ct ), int( w * clip.cw ), int( h * clip.ch ) )
            if ( insert_size == False ) and ( canvas is not None ) and ( canvas.view() is not None ):
                ad = KritaAPI.native().activeDocument()
                iw = ad.width()
                ih = ad.height()
            else:
                size = max( qimage.size().width(), qimage.size().height() )
                iw = size
                ih = size
            qimage = qimage.scaled( iw * insert_scale, ih * insert_scale, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation )
        return qimage

    def Insert_Check():
        doc = KritaAPI.native().documents()
        insert = len( doc ) > 0
        return insert

    def Path_Copy( path ):
        copy = QApplication.clipboard()
        copy.clear()
        copy.setText( path )

    def Drop_Inside( event ):
        # Mimedata
        mimedata = event.mimeData()

        # Has Boolean
        has_text = mimedata.hasText()
        has_html = mimedata.hasHtml()
        has_urls = mimedata.hasUrls()
        has_image = mimedata.hasImage()
        # has_color = mimedata.hasColor()

        # Data
        data_text = mimedata.text()
        data_html = mimedata.html()
        data_urls = mimedata.urls()
        data_image = mimedata.imageData()
        # data_color = mimedata.colorData()

        # Construct Mime Data
        mime_data = []
        if has_text == True and has_html == True and has_image == True:
            mime_data.append( data_text )
        else:
            for i in range( 0, len( data_urls ) ):
                url = os.path.abspath ( data_urls[i].toLocalFile() ) # Local File
                exists = os.path.exists( url )
                if exists == True:
                    mime_data.append( url )
        # Sort
        if len( mime_data ) > 0:
            mime_data.sort()

        # Return
        return mime_data

    def Insert_Document( image_path: str, clip: ImageClip ):
        if image_path not in ( "", None ):
            # Create Document
            document = KritaAPI.native().openDocument( image_path )
            KritaAPI.native().activeWindow().addView( document )
            w = document.width()
            h = document.height()
            # Crop
            if clip.state == True:
                ad = KritaAPI.native().activeDocument()
                ad.crop( int( w * clip.cl ), int( h * clip.ct ), int( w * clip.cw ), int( h * clip.ch ) )
                ad.waitForDone()
                ad.refreshProjection()
                KritaAPI.get_action('reset_display').trigger()
            # Show Message
            Commons.Message_Float( "INSERT", "New Document", "document-new" )
        else:
            Commons.Message_Float( "REPORT", "Null Image", "broken-preset" )
            pass
    
    def Insert_Layer( image_path: str, clip: ImageClip ):
        canvas = NativeActions.__Canvas
        if image_path not in ( "", None ) and ( canvas is not None ) and (canvas.view() is not None ):
            check_vector = image_path.endswith( tuple( REFERENCE_FILETYPE_DATA["file_vector"] ) )
            if check_vector == True:
                NativeActions.Insert_Vector( image_path )
            else:
                NativeActions.Insert_Pixel( image_path, clip )
        else:
            Commons.Message_Float( "REPORT", "Null Image", "broken-preset" )
            pass
    
    def Insert_Reference( image_path: str, clip: ImageClip ):
        canvas = NativeActions.__Canvas
        if image_path not in ( "", None ) and ( canvas is not None ) and ( canvas.view() is not None ):
            # Image
            qimage = NativeActions.Image_Clip( image_path, clip )
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
                KritaAPI.get_action( 'paste_as_reference' ).trigger()
                KritaAPI.native().activeDocument().refreshProjection()
                # Message
                pass
                Commons.Message_Float( "INSERT", "Reference", "krita_tool_reference_images" )
            else:
                pass
                Commons.Message_Float( "REPORT", "Null Image", "broken-preset" )
        else:
            pass
            Commons.Message_Float( "REPORT", "Null Image", "broken-preset" )
    
    def Insert_Vector( image_path: str ):
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
            ad = KritaAPI.native().activeDocument()
            rn = ad.rootNode()
            vl = ad.createVectorLayer( basename )
            rn.addChildNode( vl, None )
            # Input Shape to Layer
            vl.addShapesFromSvg( svg_shape )
        except Exception as e:
            report = e
        Commons.Message_Float( "INSERT", report, "vectorLayer" )
    
    def Insert_Pixel( image_path: str, clip: ImageClip ):
        report = "Pixel"
        try:
            # Variables
            basename = os.path.basename( image_path )
            # Create Layer
            ad = KritaAPI.native().activeDocument()
            rn = ad.rootNode()
            pl = ad.createNode( basename, "paintLayer" )
            rn.addChildNode( pl, None )
            # Qimage Data
            qimage = NativeActions.Image_Clip( image_path, clip )
            ptr = qimage.constBits()
            ptr.setsize( qimage.byteCount() )
            pl.setPixelData( bytes( ptr.asarray() ), 0, 0, qimage.width(), qimage.height() )
            ad.refreshProjection()
        except Exception as e:
            report = e
        Commons.Message_Float( "INSERT", report, "paintLayer" )
    