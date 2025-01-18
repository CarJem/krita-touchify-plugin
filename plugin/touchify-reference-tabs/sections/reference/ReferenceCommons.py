import os
from PyQt5.QtGui import *
import urllib
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ReferencePin import ReferencePin

class ReferenceCommons:

    def Message_Log( self, operation, message ):
        pass
        
    def Message_Warnning( self, operation, message ):
        pass

    def Message_Float( self, operation, message, icon ):
        pass

    def Data_QPixmap( tipo: str, path: str, web: str):

        if tipo == "image" and path != None:
            path = os.path.abspath( path )
            with open( path, "r" ) as f:
                data = f.read()
            return data

        elif tipo == "image" and web != None:
            qpixmap = ReferenceCommons.Download_Data( web )
            try:
                width = int( qpixmap.width() )
                height = int( qpixmap.height() )
            except:
                ReferenceCommons.Message_Warnning( "ERROR", "access failed")
        else:
            return None
    
    @staticmethod
    def Bytes_Python( path ):
        with open( path, "rb" ) as f:
            data = f.read()
        return data
    
    @staticmethod
    def Download_QPixmap( url: str ):
        data = ReferenceCommons.Download_Data( url )
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
    
    #endregion