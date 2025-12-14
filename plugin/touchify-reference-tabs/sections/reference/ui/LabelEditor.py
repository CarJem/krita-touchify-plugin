from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from typing import TYPE_CHECKING
from ....extensions.color_picker import *
from touchify.src.alib_widgets.buttons.ColorButton import ColorButton

if TYPE_CHECKING:
    from ..ReferenceSection import ReferenceSection
    from ..ReferenceView import ReferenceView

class LabelEditor(QWidget):
    SIGNAL_VISIBILITY_CHANGED = pyqtSignal()

    def __init__(self, parent: "ReferenceSection"):
        super().__init__(parent)
        self.section_parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setObjectName("label_panel")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Label Picker
        self.picker_mode = None
        self.picker_pen = QColor( 0, 0, 0 )
        self.picker_bg = QColor( 0, 0, 0 )
        self.picker_cancel = QColor( 0, 0, 0 )

        self.label_panel_layout = QGridLayout(self)
        self.label_panel_layout.setContentsMargins(0,0,0,0)
        self.label_panel_layout.setHorizontalSpacing(0)
        self.label_panel_layout.setVerticalSpacing(0)
        self.label_panel_layout.setObjectName("label_panel_layout")
        self.setLayout(self.label_panel_layout)

        self.label_text = QPushButton(self)
        self.label_text.setContentsMargins(0,0,0,0)
        self.label_text.setMaximumWidth(50)
        self.label_text.setFocusPolicy(Qt.NoFocus)
        self.label_text.setObjectName("label_text")
        self.label_text.setText("Text")
        self.label_panel_layout.addWidget(self.label_text, 0, 1, 1, 1)

        self.label_font = QFontComboBox(self)
        self.label_font.setContentsMargins(0,0,0,0)
        self.label_font.setMaximumWidth(150)
        self.label_font.setObjectName("label_font")
        self.label_panel_layout.addWidget(self.label_font, 0, 2, 1, 1)

        self.label_letter = QSpinBox(self)
        self.label_letter.setContentsMargins(0,0,0,0)
        self.label_letter.setAlignment(Qt.AlignCenter)
        self.label_letter.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.label_letter.setMinimum(1)
        self.label_letter.setMaximum(200)
        self.label_letter.setProperty("value", 10)
        self.label_letter.setObjectName("label_letter")
        self.label_panel_layout.addWidget(self.label_letter, 0, 3, 1, 1)
        
        self.label_pen = ColorButton( self )
        self.label_pen.setColor( QColor( "#e5e5e5" ) )
        self.label_pen.setContentsMargins(0,0,0,0)
        self.label_pen.setObjectName("label_pen")
        self.label_pen.colorChanged.connect( self.updateLabelForeground )
        self.label_panel_layout.addWidget(self.label_pen, 0, 4, 1, 1)

        self.label_bg = ColorButton( self )
        self.label_bg.setColor( QColor( "#191919" ) )
        self.label_bg.setContentsMargins(0,0,0,0)
        self.label_bg.setObjectName("label_bg")
        self.label_bg.colorChanged.connect( self.updateLabelBackground )
        self.label_panel_layout.addWidget(self.label_bg, 0, 5, 1, 1)

        spacerItem = QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.label_panel_layout.addItem(spacerItem, 0, 6, 1, 1)

        self.label_text.clicked.connect( self.updateLabelText )
        self.label_font.currentTextChanged.connect( self.updateLabelFont )
        self.label_letter.valueChanged.connect( self.updateLabelSize )

    def hideEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().hideEvent(a0)
    
    def showEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().showEvent(a0)
    
    def RefState(self):
        return self.section_parent.view

    def setInformation(self, info: "ReferenceView.LabelInfo"):
        # Signals
        self.label_font.blockSignals( True )
        self.label_letter.blockSignals( True )
        self.label_pen.blockSignals( True )
        self.label_bg.blockSignals( True )

        if info.valid:
            self.label_text.setEnabled( True )
            self.label_font.setEnabled( True )
            self.label_letter.setEnabled( True )
            self.label_pen.setEnabled( True )
            self.label_bg.setEnabled( True )
            # Variables
            info_text = info.text
            info_font = info.font
            info_letter = info.letter
            info_pen = info.pen
            info_bg = info.bg
            # ToolTip
            self.label_font.setCurrentText( info_font )
            self.label_letter.setValue( info_letter )
            self.label_pen.setToolTip( info_pen )
            self.label_bg.setToolTip( info_bg )
            # Modules
            self.label_pen.setColor( QColor( info_pen ) )
            self.label_bg.setColor( QColor( info_bg ) )
        else:
            self.label_text.setEnabled( False )
            self.label_font.setEnabled( False )
            self.label_letter.setEnabled( False )
            self.label_pen.setEnabled( False )
            self.label_bg.setEnabled( False )

        # Signals
        self.label_font.blockSignals( False )
        self.label_letter.blockSignals( False )
        self.label_pen.blockSignals( False )
        self.label_bg.blockSignals( False )

    def updateLabelText( self ):
        previous = self.RefState().Get_Label_Infomation()
        if previous != None:
            string, ok = QInputDialog.getMultiLineText( self, "Input Text", "Input Text", previous["text"] )
            if ( ok == True and string != None ):
                self.RefState().Set_Label_Text( string )

    def updateLabelFont( self, font ):
        self.RefState().Set_Label_Font( font )

    def updateLabelSize( self, letter ):
        self.RefState().Set_Label_Letter( letter )

    def updateLabelForeground( self, qcolor: QColor ):
        hex_code = qcolor.name()
        self.RefState().Set_Label_Pen( hex_code )

    def updateLabelBackground( self, qcolor: QColor ):
        hex_code = qcolor.name()
        self.RefState().Set_Label_Bg( hex_code )


        