from .ReferencePin import ReferencePin
from .ReferenceCommons import ReferenceCommons
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
class ReferenceSaveState(QObject):

    ref_position: list[int] = [ 1, 1 ]
    ref_zoom: float = 1
    ref_pins: list[ReferencePin] = []
    ref_board: str = None

    SIGNAL_PROGRESS_VALUE = pyqtSignal(int)


    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.ref_zoom = 1
        self.ref_position = [ 1, 1 ]
        self.ref_pins = []
        self.ref_board = None

    
    def load(self, board: list[str], ref_board: str, new_file: bool):

        if new_file:
            self.ref_pins = []
            self.ref_zoom = 1
            self.ref_position = [ 0.5, 0.5 ]
            return

        # Variables
        count = len( board )

        # Construct Board
        self.ref_pins = []
        self.ref_zoom = 1
        self.ref_position = [ 0.5, 0.5 ]
        if len( board ) > 0:
            if board[0].startswith( "Imagine Board" ) == True:
                for i in range( 1, count ):
                    try:
                        # Progress Bar
                        self.SIGNAL_PROGRESS_VALUE.emit( i )
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
                            self.ref_position = eval( line[n:] )
                        elif line.startswith( "ref_zoom=" ) == True: # Camera Scale
                            n = len( "ref_zoom=" )
                            self.ref_zoom = float( line[n:] )
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
                            pin_data = ReferencePin(**line)
                            self.ref_pins.append( pin_data )
                    except:
                        pass

        #endregion

    def save( self ):
        # Header
        data = "Imagine Board"
        # Type of save
        data += f"\nconnect"
        # Camera
        data += f"\nref_position={ self.ref_position }"
        data += f"\nref_zoom={ self.ref_zoom }"
        for item in self.ref_pins:
            result = item.dict()
            # Clean
            result["qpixmap"] = None
            result["draw"] = None
            result["zdata"] = None
            # String
            data += f"\n{ result }"
        return data
    
    def export( self ):
        # Header
        data = "Imagine Board"
        # Type of save
        data += f"\ndata"
        # Camera
        data += f"\nref_position={ self.ref_position }"
        data += f"\nref_zoom={ self.ref_zoom }"
        for item in self.ref_pins:
            result = item.dict()
            # ZData
            path = result["path"]
            web = result["web"]
            if path != None:
                result["zdata"] = ReferenceCommons.Bytes_Python( path )
            elif web != None:
                result["zdata"] = ReferenceCommons.Download_Data( web )
            else:
                result["zdata"] = None
            # Clean
            result["qpixmap"] = None
            result["draw"] = None
            # String
            data += f"\n{ result }"
        return data