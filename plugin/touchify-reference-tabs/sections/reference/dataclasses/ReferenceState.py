import os

import urllib
from .ReferencePin import ReferencePin
from ....extensions.commons import Commons
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

EO_ENCODING = "utf-8"

class ReferenceState(QObject):

    ref_position: list[int] = [ 1, 1 ]
    ref_zoom: float = 1
    ref_pins: list[ReferencePin] = []
    ref_path: str = None

    SIGNAL_PROGRESS_VALUE = pyqtSignal(int)
    SIGNAL_PROGRESS_MAX = pyqtSignal(int)
    SIGNAL_DATA_LOADED = pyqtSignal(bool)
    SIGNAL_DATA_UNLOADED = pyqtSignal()
    SIGNAL_DATA_SAVE = pyqtSignal()


    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.ref_zoom = 1
        self.ref_position = [ 1, 1 ]
        self.ref_pins = []
        self.ref_path = None

    def path(self):
        return self.ref_path

    def pins(self):
        return self.ref_pins

    def zoom(self):
        return self.ref_zoom

    def pos(self):
        return self.ref_position

    def loaded(self):
        return self.ref_path != None

    
    def __Private_Data_Load(self, board: list[str], ref_board: str, new_file: bool):

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
                            self.ref_path = ref_board
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

    def __Private_Data_Save( self ):
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
    
    def __Private_Data_Export( self ):
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
                result["zdata"] = Commons.Bytes_Python( path )
            elif web != None:
                result["zdata"] = Commons.Download_Data( web )
            else:
                result["zdata"] = None
            # Clean
            result["qpixmap"] = None
            result["draw"] = None
            # String
            data += f"\n{ result }"
        return data

    def __Private_Data_Download( self, download_folder: str ):
        for item in self.ref_pins:
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
                    qpixmap = Commons.Download_QPixmap( web )
                    name = os.path.split( urllib.parse.urlparse( web ).path )[1]
                    save_path = os.path.join( download_folder, name )
                # Save
                if os.path.exists( save_path ) == False:
                    qpixmap.save( save_path )
                else:
                    self.Message_Log( "ERROR", f"Path already exists { save_path }" )


    def Data_Load( self, path: str, new_file: bool = False ):
        self.ref_path = path

        board = None
        ref_board = None

        if ( path not in [ "", ".", None ] and os.path.exists( path ) == True ):
            with open( path, "r", encoding=EO_ENCODING ) as f:
                board = f.readlines()
                ref_board = path

        if (board == None or ref_board == None) and not new_file: return

        self.SIGNAL_PROGRESS_VALUE.emit(0)
        self.SIGNAL_PROGRESS_MAX.emit(len(board))

        self.__Private_Data_Load(board, ref_board, new_file)

        self.SIGNAL_PROGRESS_VALUE.emit(0)
        self.SIGNAL_PROGRESS_MAX.emit(1)

        self.SIGNAL_DATA_LOADED.emit(new_file)

    def Data_Save( self ):
        self.SIGNAL_DATA_SAVE.emit()

    def Data_Save_St( self, list_reference: list[ReferencePin] ):
        self.ref_pins = list_reference
        path = self.ref_path

        if path not in [ "", ".", None ]:
            data = self.__Private_Data_Save()
            with open( path, "w", encoding=EO_ENCODING ) as f:
                f.write( data )

    def Data_Update( self, ref_position: list[int], ref_zoom: float, len_board: int ):
        self.ref_position = ref_position
        self.ref_zoom = ref_zoom

    def Data_Export( self, path ):
        if path not in [ "", ".", None ]:
            data = self.__Private_Data_Export()
            with open( path, "w", encoding=EO_ENCODING ) as f:
                f.write( data )

    def Data_Download( self, download_folder: str ):
        if download_folder not in [ "", ".", None ]:
            self.__Private_Data_Download(download_folder)

    def Data_Unload(self):
        self.ref_path = None
        self.SIGNAL_DATA_UNLOADED.emit()
