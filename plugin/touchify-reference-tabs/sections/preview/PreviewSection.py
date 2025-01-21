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

from krita import *
 
# Zoom percent constants
MAX_ZOOM = 5000
MIN_ZOOM = 0
ZOOM_STEP = 1

useAngleSelector = True

from .PreviewView import PreviewView
from ...dataclasses.images import InsertablePin
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
        self.preview_container.setContentsMargins(0,0,0,0)
        layout.addWidget(self.preview_container)

        self.view = PreviewView(self.preview_container) 
        self.view.setContentsMargins(0,0,0,0)

        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.setFixedHeight(25)



        self.zoom_spinbox = QDoubleSpinBox(self)
        self.zoom_spinbox.setRange(MIN_ZOOM, MAX_ZOOM)
        self.zoom_spinbox.setSingleStep(ZOOM_STEP)
        self.zoom_spinbox.setSuffix("%")
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setToolTip("Zoom")

        # - page fit status
        #self.fitButton = QToolButton(self)
        #self.fitButton.setIcon(Krita.instance().icon("zoom-fit"))
        #self.fitButton.setToolTip("Fit to page")
        #self.fitButton.setCheckable(True)
        #self.fitButton.setChecked(False)
        #self.fitButton.toggled.connect(self.enactFit)

        # - hmirrored status
        #self.hMirrorButton = QToolButton(self)
        #self.hMirrorButton.setIcon(Krita.instance().icon("transform_icons_mirror_x"))
        #self.hMirrorButton.setToolTip("Horizontal mirroring")
        #self.hMirrorButton.setCheckable(True)
        #self.hMirrorButton.setChecked(False)
        #self.hMirrorButton.toggled.connect(self.reloadTransforms)

        # - vmirrored status
        #self.vMirrorButton = QToolButton(self)
        #self.vMirrorButton.setIcon(Krita.instance().icon("transform_icons_mirror_y"))
        #self.vMirrorButton.setToolTip("Vertical mirroring")
        #self.vMirrorButton.setCheckable(True)
        #self.vMirrorButton.setChecked(False)
        #self.vMirrorButton.toggled.connect(self.reloadTransforms)

        # - rotate status
        #self.rotateSelector = AngleSelector()
        #self.rotateSelector.setFlipOptionsMode("ContextMenu")
        #self.rotateSelector.angleChanged.connect(self.reloadTransforms)

        # - color picker
        #self.colorSamplerButton = QToolButton(self)
        #self.colorSamplerButton.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        #self.colorSamplerButton.setToolTip("Sample color from image")
        #self.colorSamplerButton.setCheckable(True)
        #self.colorSamplerButton.setChecked(False)
        #self.colorSamplerButton.toggled.connect(self.action_toggleSampleColor)
        #self.colorSamplerButton.setEnabled(False)

        self.tool_panel.addWidget(self.zoom_spinbox, stretch=1)
        #self.tool_panel.addWidget(self.fitButton)
        #self.tool_panel.addWidget(self.hMirrorButton)
        #self.tool_panel.addWidget(self.vMirrorButton)
        #self.tool_panel.addWidget(self.rotateSelector, stretch=0)
        #self.tool_panel.addWidget(self.colorSamplerButton)

    def Connections( self ):
        qApp.paletteChanged.connect(self.OnEvent_ThemeChanged)
        self.OnEvent_ThemeChanged()


        self.zoom_spinbox.valueChanged.connect(self.OnEvent_ZoomIncremented)

        self.view.SIGNAL_INCREMENT.connect(self.OnEvent_Increment)
        self.view.SIGNAL_PIN_IMAGE.connect( self.OnEvent_PinImage )
        self.view.SIGNAL_RETURN_REQUESTED.connect(self.OnEvent_ReturnRequested)
        self.view.SIGNAL_ZOOM_UPDATED.connect(self.OnEvent_ZoomUpdate)


    # OnEvent

    def OnEvent_ZoomUpdate(self, value: float):
        factor = 100
        self.zoom_spinbox.valueChanged.disconnect(self.OnEvent_ZoomIncremented)
        self.zoom_spinbox.setValue(value*factor)
        self.zoom_spinbox.valueChanged.connect(self.OnEvent_ZoomIncremented)


    def OnEvent_ZoomIncremented(self, value: float):
        factor = 100
        if value == 0: self.view.Camera_Zoom(0, False)
        else: self.view.Camera_Zoom(value / factor, False)

    def OnEvent_Increment(self, value: int):
        pass
        
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
    
    def resizeEvent(self, event):
        self.view.Set_Size(self.preview_container.width(), self.preview_container.height())
        super().resizeEvent(event)
    

    








