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
from touchify.src.components.krita.KisAngleSelector import KisAngleSelector

from krita import *
 
# Zoom percent constants
MAX_ZOOM = 5000
MIN_ZOOM = 0
ZOOM_STEP = 1

useAngleSelector = True

from ...DockerToolbar import DockerToolbar
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .PreviewSection import PreviewSection

class PreviewToolbar(DockerToolbar):

    def __init__(self, parent: "PreviewSection"):
        super().__init__(parent, Qt.Orientation.Horizontal)
        self.setFixedHeight(25)
        self.Section: "PreviewSection" = parent
        self.Components()
        self.Connections()

    def View(self):
        return self.Section.view

    def Components( self ):
        self.zoom_spinbox = QDoubleSpinBox(self)
        self.zoom_spinbox.setRange(MIN_ZOOM, MAX_ZOOM)
        self.zoom_spinbox.setSingleStep(ZOOM_STEP)
        self.zoom_spinbox.setSuffix("%")
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setToolTip("Zoom")

        self.angle_spinbox = KisAngleSelector(self)
        self.angle_spinbox.setFlipOptionsMode("ContextMenu")

        self.reset_button = QToolButton(self)
        self.reset_button.setIcon(Krita.instance().icon("zoom-fit"))
        self.reset_button.setToolTip("Fit to page")

        self.horz_mirror_button = QToolButton(self)
        self.horz_mirror_button.setIcon(Krita.instance().icon("transform_icons_mirror_x"))
        self.horz_mirror_button.setToolTip("Horizontal mirroring")
        self.horz_mirror_button.setCheckable(True)
        self.horz_mirror_button.setChecked(False)

        self.vertical_mirror_button = QToolButton(self)
        self.vertical_mirror_button.setIcon(Krita.instance().icon("transform_icons_mirror_y"))
        self.vertical_mirror_button.setToolTip("Vertical mirroring")
        self.vertical_mirror_button.setCheckable(True)
        self.vertical_mirror_button.setChecked(False)

        self.color_picker_button = QToolButton(self)
        self.color_picker_button.setIcon(Krita.instance().icon("krita_tool_color_sampler"))
        self.color_picker_button.setToolTip("Sample color from image")
        self.color_picker_button.setCheckable(True)
        self.color_picker_button.setChecked(False)

        self.addWidget(self.zoom_spinbox, stretch=1)
        self.addWidget(self.angle_spinbox, stretch=0)
        self.addWidget(self.reset_button)
        self.addWidget(self.horz_mirror_button)
        self.addWidget(self.vertical_mirror_button)
        self.addWidget(self.color_picker_button)

    def Connections( self ):
        self.zoom_spinbox.valueChanged.connect(self.Action_UpdateZoom)
        self.angle_spinbox.angleChanged.connect(self.Action_UpdateRotation)
        self.reset_button.clicked.connect(self.Action_FitImage)
        self.horz_mirror_button.clicked.connect(lambda: self.Action_EditOperation("efx"))
        self.vertical_mirror_button.clicked.connect(lambda: self.Action_EditOperation("efy"))
        self.color_picker_button.clicked.connect(self.Action_ColorPicker)

        self.View().SIGNAL_ZOOM_UPDATED.connect(self.OnEvent_ZoomUpdated)
        self.View().SIGNAL_ROTATION_UPDATED.connect(self.OnEvent_RotationUpdated)
        self.View().SIGNAL_EDIT_OPERATIONS_TOGGLED.connect(self.OnEvent_EditOperationsUpdated)
        self.View().SIGNAL_INCREMENT.connect(self.OnEvent_PreviewIncremented)
        self.View().SIGNAL_FINISHED_LOADING.connect(self.OnEvent_EditOperationsUpdated)


    # region OnEvent Functions

    def OnEvent_PreviewIncremented(self, value: int):
        pass

    def OnEvent_RotationUpdated(self, value: float):
        self.angle_spinbox.angleChanged.disconnect(self.Action_UpdateRotation)
        self.angle_spinbox.setAngle(value)
        self.angle_spinbox.angleChanged.connect(self.Action_UpdateRotation)



    def OnEvent_EditOperationsUpdated(self):
        allow_editing = self.View().state_animation == False and self.View().preview_qpixmap != None and self.View().preview_path != None
        self.horz_mirror_button.setEnabled(allow_editing)
        self.vertical_mirror_button.setEnabled(allow_editing)

        self.horz_mirror_button.setChecked(self.View().edit_invert_h)
        self.vertical_mirror_button.setChecked(self.View().edit_invert_v)
        self.color_picker_button.setChecked(self.View().state_pickcolor)


    def OnEvent_ZoomUpdated(self, value: float):
        factor = 100
        self.zoom_spinbox.valueChanged.disconnect(self.Action_UpdateZoom)
        self.zoom_spinbox.setValue(value*factor)
        self.zoom_spinbox.valueChanged.connect(self.Action_UpdateZoom)
    
    #endregion

    #region Action Functions

    def Action_ColorPicker(self):
        self.View().Toggle_ColorPicker()

    def Action_EditOperation(self, option: str):
        self.View().Edit_Display(option)

    def Action_FitImage(self):
        self.View().Camera_Reset()
        self.View().update()

    def Action_UpdateRotation(self, value: float):
        self.View().Camera_Rotate(value)

    def Action_UpdateZoom(self, value: float):
        factor = 100
        if value == 0: self.View().Camera_Zoom(0, False)
        else: self.View().Camera_Zoom(value / factor, False)
    
    #endregion
    








