from PyQt5 import QtCore, QtGui
from touchify.src.api_krita import KritaAPI

class Paintables:

    @staticmethod
    def Painter_CodeBrackets( color: str, painter: QtGui.QPainter, w2: int, h2: int, side: int ):
        # Painter
        painter.setPen( QtCore.Qt.PenStyle.NoPen )
        painter.setBrush( QtGui.QBrush( QtGui.QColor( color ) ) )
        # Variables
        kw = 0.3 * side
        kh = 0.2 * side
        d = 0.5
        # Polygons
        arrow_left = QtGui.QPolygon( [
            QtCore.QPoint( int( w2 - kw * d ),     int( h2 - kh ) ),
            QtCore.QPoint( int( w2 ),              int( h2 ) ),
            QtCore.QPoint( int( w2 - kw * d ),     int( h2 + kh ) ),
            QtCore.QPoint( int( w2 - kw ),         int( h2 + kh ) ),
            QtCore.QPoint( int( w2 - kw * d ),     int( h2 ) ),
            QtCore.QPoint( int( w2 - kw ),         int( h2 - kh ) ),
        ] )
        arrow_right = QtGui.QPolygon( [
            QtCore.QPoint( int( w2 + kw * d ),     int( h2 - kh ) ),
            QtCore.QPoint( int( w2 + kw ),         int( h2 ) ),
            QtCore.QPoint( int( w2 + kw * d ),     int( h2 + kh ) ),
            QtCore.QPoint( int( w2 ),              int( h2 + kh ) ),
            QtCore.QPoint( int( w2 + kw * d ),     int( h2 ) ),
            QtCore.QPoint( int( w2 ),              int( h2 - kh ) ),
        ] )
        painter.drawPolygon( arrow_left )
        painter.drawPolygon( arrow_right )

    @staticmethod
    def Painter_Icon( name: str ):
        # name = "warning"
        # Variables
        image_size = 500
        icon_size = 200
        icon_margin = int( ( image_size - icon_size ) * 0.5 )
        # QPixmap
        qpixmap = QtGui.QPixmap( image_size, image_size )
        qpixmap.fill( QtCore.Qt.GlobalColor.transparent )
        qicon = KritaAPI.get_icon( name ).pixmap( QtCore.QSize( icon_size, icon_size ) )    
        painter = QtGui.QPainter( qpixmap )
        painter.drawPixmap( icon_margin, icon_margin, qicon )
        painter.end()
        return qpixmap
    
    @staticmethod
    def Painter_Triangle( color: str, painter: QtGui.QPainter, w2: int, h2: int, side: int ):
        # Painter
        painter.setPen( QtCore.Qt.PenStyle.NoPen )
        painter.setBrush( QtGui.QBrush( QtGui.QColor( color ) ) )
        # Variables
        kw = 0.3 * side
        kh = 0.2 * side
        d = 0.5
        # Polygons
        poly_tri = QtGui.QPolygon( [
            QtCore.QPoint( int( w2 - kw ), int( h2 - kh ) ),
            QtCore.QPoint( int( w2 + kw ), int( h2 - kh ) ),
            QtCore.QPoint( int( w2 ),      int( h2 + kh ) ),
            ] )
        painter.drawPolygon( poly_tri )