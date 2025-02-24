import os
from PyQt5.QtGui import *
import urllib
from PyQt5.QtWidgets import QFileDialog
from .settings import Settings
from PyQt5.QtCore import *

class Commons:

    @staticmethod
    def Message_Log( operation, message ):
        pass
    
    @staticmethod
    def Message_Warnning( operation, message ):
        pass

    @staticmethod
    def Message_Float( operation, message, icon ):
        print(operation, message)

    @staticmethod
    def Dialog_Load( self, title: str, filter: str ):
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
        file_path = file_dialog.getOpenFileName( self, title, Settings.getFileDialogState(), filter )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        else: Settings.setFileDialogState(os.path.dirname(file_path))
        return file_path
    
    @staticmethod
    def Dialog_Save( self, title, name: str, filter: str ):
        inital_file_path = os.path.join(Settings.getFileDialogState(), name)
        # File Dialog
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
        file_path = file_dialog.getSaveFileName( self, title, inital_file_path, filter )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        else: Settings.setFileDialogState(os.path.dirname(file_path))
        return file_path
    
    @staticmethod
    def Dialog_Directory( self, title ):
        directory = Settings.getFileDialogState()
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.DirectoryOnly )
        folder_path = file_dialog.getExistingDirectory( self, title, directory )
        if folder_path in [ "", ".", None ]:
            folder_path = None
        else: Settings.setFileDialogState(os.path.dirname(folder_path))
        return folder_path


    @staticmethod
    def Data_QPixmap( str_data: str):
        data = bytes(str_data, "utf-8")
        pixmap: QPixmap = QPixmap()
        return pixmap.loadFromData(data)
        
    @staticmethod    
    def Bytes_QPixmap( pixmap: QPixmap ):
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, 'PNG')
        return byte_array.data().decode("utf-8")



    
    @staticmethod
    def Bytes_Python( path ):
        with open( path, "rb" ) as f:
            data = f.read()
        return data
    
    @staticmethod
    def Download_QPixmap( url: str ):
        data = Commons.Download_Data( url )
        try:
            qpixmap = QPixmap()
            qpixmap.loadFromData( data )
        except:
            qpixmap = None
        return qpixmap
    
    @staticmethod
    def Download_Data(  url: str ):
        try:
            request = urllib.request.Request( url, headers={ "User-Agent": "Mozilla/5.0" } )
            response = urllib.request.urlopen( request )
            data = response.read()
        except:
            data = None
        return data
    
    @staticmethod
    def Check_Html( url ):
        boolean = False
        result = urllib.parse.urlparse( url )
        scheme = result.scheme
        if scheme == "https":
            boolean = True
        return boolean
    