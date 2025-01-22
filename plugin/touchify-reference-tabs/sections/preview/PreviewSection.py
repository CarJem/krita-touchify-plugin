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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, qApp
from ...extensions.filetypes import REFERENCE_FILETYPE_DATA

from krita import *

from .PreviewView import PreviewView
from .PreviewToolbar import PreviewToolbar
from .ui.PaginationSlider import PaginationSlider
from ...dataclasses.images import InsertablePin
from ...dataclasses.session import SessionPreview
from ...extensions.commons import Commons
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
        return self.DockerPage.ParentWidget.docker.canvas()

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
        self.preview_container.installEventFilter(self)
        self.preview_container.setContentsMargins(0,0,0,0)
        layout.addWidget(self.preview_container)

        self.view = PreviewView(self.preview_container) 
        self.view.setContentsMargins(0,0,0,0)
        self.view.Set_FileSearch(REFERENCE_FILETYPE_DATA["file_search"])

        self.page_slider = PaginationSlider(self)
        self.page_slider.setVisible(False)
        layout.addWidget(self.page_slider)

        self.tool_panel = PreviewToolbar(self)
        layout.addWidget(self.tool_panel)

    def Connections( self ):
        qApp.paletteChanged.connect(self.OnEvent_ThemeChanged)
        self.OnEvent_ThemeChanged()

        self.view.SIGNAL_PIN_IMAGE.connect( self.OnEvent_PinImage )
        self.view.SIGNAL_RETURN_REQUESTED.connect(self.OnEvent_ReturnRequested)
        self.view.SIGNAL_EXTRA_PANEL.connect(self.OnEvent_ExtraPanel)


    def Session_Load(self, session: SessionPreview):
        match session.path_type:
            case "path":
                self.view.Display_Path(session.path)
            case "pixmap":
                self.view.Display_QPixmap(Commons.Data_QPixmap(session.path))

    def Session_Save(self):
        if self.view.preview_path != None: 
            resulting_path = self.view.preview_path
            resulting_type = "path"
        elif self.view.preview_path == None and self.view.preview_qpixmap != None and isinstance(self.view.preview_qpixmap, QPixmap):
            resulting_path = Commons.Bytes_QPixmap(self.view.preview_qpixmap)
            resulting_type = "pixmap"
        else:
            resulting_path = ""
            resulting_type = ""

        return SessionPreview(
            path=resulting_path,
            path_type=resulting_type
        )

    # OnEvent

    def OnEvent_ExtraPanel( self, state: bool ):
        self.page_slider.setVisible(state)
        self.update()
        
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

    def OnEvent_PinImage( self, pin: InsertablePin ):
        self.DockerPage.PinImage(pin)
    
    def OnEvent_ReturnRequested(self):
        self.DockerPage.OpenPreviousPage()

    def Action_ChangeScaleSetting(self, setting):
        self.scalingMode = setting
        if setting == 1:  self.view.Set_Scale_Method(Qt.TransformationMode.SmoothTransformation)
        elif setting == 2: self.view.Set_Scale_Method(Qt.TransformationMode.FastTransformation)

    def Action_OpenImage(self, image_path: str):
        self.view.Display_Path(image_path)

    def Action_OpenQPixmap(self, pixmap: QPixmap):
        self.view.Display_QPixmap(pixmap)

    def eventFilter(self, a0: QObject, a1: QEvent):
        if a0 == self.preview_container and a1.type() == QEvent.Type.Resize:
            self.view.Set_Size(self.preview_container.width(), self.preview_container.height())    
        return super().eventFilter(a0, a1)
    

    








