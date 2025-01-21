# Reference Tabs
# Copyright (C) 2022 Freya Lupen <penguinflyer2222@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pathlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, qApp
from ...extensions.filetypes import REFERENCE_FILETYPE_DATA
from krita import *
from ...extensions.commons import Commons
 
# Zoom percent constants
MAX_ZOOM = 2000
MIN_ZOOM = 100
ZOOM_STEP = 100

useAngleSelector = True

from .PreviewView import PreviewView
from ...extensions.native_actions import NativeActions
from ...dataclasses.InsertInfo import InsertInfo
from ...dataclasses.Clip import Clip
from ...DockerToolbar import DockerToolbar
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...DockerPage import DockerPage

class PreviewSection(QWidget):

    def __init__(self, parent: "DockerPage"):
        super().__init__(parent)
        self.DockerPage: "DockerPage" = parent
        self.Variables()
        self.Components()
        self.Connections()

    def Canvas(self):
        return self.DockerPage.view_widget.docker.canvas()

    def Variables( self ):
        self.fitSetting = 1
        self.scalingMode = 1

    def Components( self ):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,4)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.setAcceptDrops(True)

        self.preview_container = QWidget(self)
        self.preview_container.setContentsMargins(0,0,0,0)
        layout.addWidget(self.preview_container)

        self.view = PreviewView(self.preview_container) 
        self.view.setContentsMargins(0,0,0,0)

        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.setFixedHeight(25)

    def Connections( self ):
        qApp.paletteChanged.connect(self.OnEvent_ThemeChanged)
        self.OnEvent_ThemeChanged()

        self.view.SIGNAL_INCREMENT.connect(self.OnEvent_Increment)
        self.view.SIGNAL_DROP.connect( self.OnEvent_Drop )
        self.view.SIGNAL_DRAG.connect( self.OnEvent_DragDrop )
        self.view.SIGNAL_PIN_IMAGE.connect( self.OnEvent_PinImage )
        self.view.SIGNAL_LOCATION.connect( self.OnEvent_FileLocationRequested )
        self.view.SIGNAL_ANALYSE.connect( self.OnEvent_ColorAnalyseRequested )
        self.view.SIGNAL_NEW_DOCUMENT.connect( self.OnEvent_NewDocument )
        self.view.SIGNAL_INSERT_LAYER.connect( self.OnEvent_InsertLayer )
        self.view.SIGNAL_INSERT_REFERENCE.connect( self.OnEvent_InsertReference )
        self.view.SIGNAL_RETURN_REQUESTED.connect(self.OnEvent_ReturnRequested)


    # OnEvent

    def OnEvent_Drop(self, lista):
        if len( lista ) > 0:
            # Variables
            item = lista[0]
            # Check Source
            check_html = Commons.Check_Html( item )
            if check_html == True:
                self.Action_OpenInternet( item )
            else:
                # Checks
                item = os.path.abspath( item )
                check_dir = os.path.isdir( item )
                check_file = os.path.isfile( item )

                if item and check_file:
                    self.Action_OpenImage(item)

    def OnEvent_Increment(self, value: int):
        pass

    def OnEvent_ColorAnalyseRequested( self, qimage: QImage ):
        self.view.ColorPicker.Analyse(qimage)

    def OnEvent_FileLocationRequested( self, image_path: str ):
        NativeActions.File_Location(image_path)
    
    def OnEvent_DragDrop( self, image_path: str, clip: Clip ):
        NativeActions.Drag_Drop(self, image_path, clip)
        
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

    def OnEvent_NewDocument(self, path: str, clip: Clip):
        NativeActions.Insert_Document(path, clip)

    def OnEvent_InsertLayer(self, path: str, clip: Clip):
        NativeActions.Insert_Layer(path, clip, self.Canvas())

    def OnEvent_InsertReference(self, path: str, clip: Clip):
        NativeActions.Insert_Reference(path, clip, self.Canvas())     

    def OnEvent_PinImage( self, pin: InsertInfo ):
        self.DockerPage.PinImage(pin)
    
    def OnEvent_ReturnRequested(self):
        self.DockerPage.OpenPreviousPage()

    def Action_ChangeScaleSetting(self, setting):
        self.scalingMode = setting
        if setting == 1:  self.view.Set_Scale_Method(Qt.TransformationMode.SmoothTransformation)
        elif setting == 2: self.view.Set_Scale_Method(Qt.TransformationMode.FastTransformation)

    def Action_OpenInternet(self, url: str):
        qpixmap = Commons.Download_QPixmap( url )
        if qpixmap: self.Action_OpenQPixmap(qpixmap)

    def Action_OpenImage(self, image_path: str):
        def File_Extension( path ):
            if path == None:
                extension = None
            else:
                extension = pathlib.Path( path ).suffix
                extension = extension.replace( ".", "" )
            return extension
        
        file_anima = REFERENCE_FILETYPE_DATA["file_anima"]
        file_compact = REFERENCE_FILETYPE_DATA["file_compact"]

        extension = File_Extension( image_path )

        if extension in file_anima:
            self.view.Display_Animation( image_path )

        elif extension in file_compact:
            self.preview_state = "COMPACT"
            self.view.Display_Compact( image_path )

        else:
            self.preview_state = "STATIC"
            self.view.Display_Path( image_path )

    def Action_OpenQPixmap(self, pixmap: QPixmap):
        self.view.Display_QPixmap(pixmap)
    
    def resizeEvent(self, event):
        self.view.Set_Size(self.preview_container.width(), self.preview_container.height(), False)
        super().resizeEvent(event)
    

    








