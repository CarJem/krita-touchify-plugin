import os
from PyQt5.QtGui import *
import urllib
from PyQt5.QtWidgets import QFileDialog
from .settings import Settings

class Commons:

    @staticmethod
    def Message_Log( operation, message ):
        pass
    
    @staticmethod
    def Message_Warnning( operation, message ):
        pass

    @staticmethod
    def Message_Float( operation, message, icon ):
        pass

    @staticmethod
    def Dialog_Load( self, title ):
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
        file_path = file_dialog.getOpenFileName( self, title, Settings.getFileDialogState(), "File( *.eo )" )[0]
        if file_path in [ "", ".", None ]:
            file_path = None
        else: Settings.setFileDialogState(os.path.dirname(file_path))
        return file_path
    
    @staticmethod
    def Dialog_Save( self, title, name ):
        # File Dialog
        file_dialog = QFileDialog( self )
        file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
        file_path = file_dialog.getSaveFileName( self, title,  Settings.getFileDialogState(), "File( *.eo )" )[0]
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
    def Data_QPixmap( tipo: str, path: str, web: str):

        if tipo == "image" and path != None:
            path = os.path.abspath( path )
            with open( path, "r" ) as f:
                data = f.read()
            return data

        elif tipo == "image" and web != None:
            qpixmap = Commons.Download_Data( web )
            try:
                width = int( qpixmap.width() )
                height = int( qpixmap.height() )
            except:
                Commons.Message_Warnning( "ERROR", "access failed")
        else:
            return None
    
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
    