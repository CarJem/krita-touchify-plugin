from krita import *
from PyQt5 import QtCore
from .ReferenceCalc import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ReferenceView import ReferenceView

colorpicker_size = 250
cps_a = colorpicker_size * 0.015
cps_b = colorpicker_size - ( cps_a * 2 )
cps_c = colorpicker_size * 0.040
cps_d = colorpicker_size - ( cps_c * 2 )
cps_e = colorpicker_size * 0.105
cps_f = colorpicker_size - ( cps_e * 2 )
cps_g = colorpicker_size * 0.120
cps_h = colorpicker_size - ( cps_g * 2 )

def Import_Pigment_O( ):
    pigment_o_module = None
    try:
        dockers = Krita.instance().dockers()
        for d in dockers:
            if d.objectName() == "pykrita_pigment_o_docker":
                pigment_o_module = d
                break
    except:
        pigment_o_module = None
    return pigment_o_module

def ColorPicker_Event( self: "ReferenceView", ex, ey, qimage_grab ):
    if ( self.state_pickcolor == True and qimage_grab != None ):
        # Event
        ex = Limit_Range( ex, 0, self.ww - 1 )
        ey = Limit_Range( ey, 0, self.hh - 1 )
        # Picker Location
        pos = QPoint( ex, ey )
        point = self.mapToGlobal( pos )
        px = point.x() - ( colorpicker_size * 0.5 )
        py = point.y() - ( colorpicker_size * 0.5 )
        # Pixel RGB ( 0-1 )
        pixel = qimage_grab.pixelColor( ex , ey )
        red = pixel.redF()
        green = pixel.greenF()
        blue = pixel.blueF()

        # Apply Color
        pigment_o = self.pigment_o
        if pigment_o != None:
            if self.state_press == True:
                pigment_o.API_Input_Kelvin( 6500 )
                cor = pigment_o.API_Input_Preview( "RGBImproved Resizing for On Canvas Widgets", red, green, blue, 0 )
            if self.state_press == False:
                cor = pigment_o.API_Input_Apply( "RGB", red, green, blue, 0 )
            red   = cor[ "rgb_d1" ]
            green = cor[ "rgb_d2" ]
            blue  = cor[ "rgb_d3" ]
        else:
            active_document = Krita.instance().activeDocument()
            if active_document == None:
                d_cm = "RGBA"
                d_cd = "U8"
                d_cp = ""
            else:
                d_cm = active_document.colorModel()
                d_cd = active_document.colorDepth()
                d_cp = active_document.colorProfile()
            d_ac = Krita.instance().activeWindow().activeView().canvas()
            # Managed Colors RGB only
            managed_color = ManagedColor( d_cm, d_cd, d_cp )
            comp = managed_color.components()
            if ( d_cm == "A" or d_cm == "GRAYA" ):
                comp = [ red, 1 ]
            if d_cm == "RGBA":
                if ( d_cd == "U8" or d_cd == "U16" ):
                    comp = [ blue, green, red, 1 ]
                if ( d_cd == "F16" or d_cd == "F32" ):
                    comp = [ red, green, blue, 1 ]
            managed_color.setComponents( comp )
            # Color for Canvas
            if d_ac != None:
                display = managed_color.colorForCanvas( d_ac )
                red   = display.redF()
                green = display.greenF()
                blue  = display.blueF()
            # Apply Color
            if self.state_press == False:
                Krita.instance().activeWindow().activeView().setForeGroundColor( managed_color )

        # Display Color
        qcolor = QColor( int( red * 255 ), int( green * 255 ), int( blue * 255 ) )
        hex_code = qcolor.name()
        self.color_active = qcolor
        if self.state_press == False:
            # Previous
            self.color_previous = qcolor
            # Clipboard
            clip_board = QApplication.clipboard()
            clip_board.clear()
            clip_board.setText( f"{ hex_code }" )

def ColorPicker_Render( self: "ReferenceView", painter, ex, ey ):
    # Values
    ex = Limit_Range( ex, 0, self.ww )
    ey = Limit_Range( ey, 0, self.hh )
    ex = int( ex - ( colorpicker_size * 0.5 ) )
    ey = int( ey - ( colorpicker_size * 0.5 ) )

    # Mask Neutral
    mask_neutral = QPainterPath()
    mask_neutral.addEllipse( ex, ey, colorpicker_size, colorpicker_size )
    mask_neutral.addEllipse( ex + cps_g, ey + cps_g, cps_h, cps_h )
    painter.setClipPath( mask_neutral )
    # Color Neutral
    painter.setPen( QtCore.Qt.NoPen )
    painter.setBrush( QBrush( QColor( 128, 128, 128 ) ) )
    painter.drawEllipse( ex, ey, colorpicker_size, colorpicker_size )

    # Mask Previous
    mask_previous = QPainterPath()
    mask_previous.addEllipse( ex + cps_a, ey + cps_a, cps_b, cps_b )
    mask_previous.addEllipse( ex + cps_e, ey + cps_e, cps_f, cps_f )
    painter.setClipPath( mask_previous )
    # Color Previous
    painter.setPen( QtCore.Qt.NoPen )
    painter.setBrush( QBrush( self.color_previous ) )
    painter.drawEllipse( ex, ey, colorpicker_size, colorpicker_size )

    # Mask Active
    mask_previous = QPainterPath()
    mask_previous.addEllipse( ex + cps_c, ey + cps_c, cps_d, cps_d )
    mask_previous.addEllipse( ex + cps_e, ey + cps_e, cps_f, cps_f )
    painter.setClipPath( mask_previous )
    # Color Previous
    painter.setPen( QtCore.Qt.NoPen )
    painter.setBrush( QBrush( self.color_active ) )
    painter.drawEllipse( ex, ey, colorpicker_size, colorpicker_size )

    # Reset Mask
    mask_reset = QPainterPath()
    mask_reset.addRect( 0, 0, self.ww, self.hh )
    painter.setClipPath( mask_reset )