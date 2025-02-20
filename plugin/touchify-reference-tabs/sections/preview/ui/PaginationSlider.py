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

import random
from PyQt5.QtCore import Qt

from krita import *
from touchify.src.api_krita import KritaAPI

from ....DockerToolbar import DockerToolbar
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..PreviewSection import PreviewSection

class PaginationSlider(DockerToolbar):
    SIGNAL_VISIBILITY_CHANGED = pyqtSignal()
    
    def __init__(self, parent: "PreviewSection"):
        super().__init__(parent, Qt.Orientation.Horizontal)
        self.setFixedHeight(25)
        self.Section: "PreviewSection" = parent
        self.Components()
        self.Connections()

    def View(self):
        return self.Section.view

    def Components( self ):
        self.path_label = QLabel(self)
        self.path_label.setVisible(False)
        self.path_label.setText(None)

        self.animation_slider = QSlider(self)
        self.animation_slider.setOrientation(Qt.Orientation.Horizontal)
        self.animation_slider.setMinimum(0)
        self.animation_slider.setVisible(False)
        self.animation_slider.setValue(1)

        self.page_label = QLabel(self)
        self.page_label.setText("Page:")

        self.page_index_box = QSpinBox(self)
        self.page_index_box.setMinimum(1)
        self.page_index_box.setValue(1)

        self.page_count_label = QLabel(self)
        self.page_count_label.setText("/ 0")

        self.play_pause_button = QToolButton(self)
        self.play_pause_button.setVisible(False)
        self.play_pause_button.setIcon(KritaAPI.get_icon("media-playback-stop"))

        self.left_button = QToolButton(self)
        self.left_button.setIcon(KritaAPI.get_icon("prevframe"))

        self.right_button = QToolButton(self)
        self.right_button.setIcon(KritaAPI.get_icon("nextframe"))

        self.addWidget(self.path_label, stretch=1)
        self.addWidget(self.animation_slider, stretch=1)
        self.addWidget(self.page_label)
        self.addWidget(self.page_index_box)
        self.addWidget(self.page_count_label)
        self.addWidget(self.play_pause_button)
        self.addWidget(self.left_button)
        self.addWidget(self.right_button)

    def Connections( self ):
        self.left_button.clicked.connect(self.Action_PageLeft)
        self.right_button.clicked.connect(self.Action_PageRight)
        self.page_index_box.valueChanged.connect(self.Action_PageChangeAlt)
        self.play_pause_button.clicked.connect(self.Action_PlayPause)
        self.animation_slider.valueChanged.connect(self.Action_PageChange)

        self.View().SIGNAL_INCREMENT.connect(self.OnEvent_PreviewIncremented)
        self.View().SIGNAL_EXTRA_MAX.connect(self.OnEvent_ExtraMax)
        self.View().SIGNAL_EXTRA_VALUE.connect(self.OnEvent_ExtraValue)
        self.View().SIGNAL_EXTRA_LABEL.connect(self.OnEvent_ExtraLabel)
        self.View().SIGNAL_RANDOM.connect(self.OnEvent_RandomIndexRequested)


    # region OnEvent Functions

    def OnEvent_PreviewIncremented(self):
        pass

    def OnEvent_ExtraMax(self, value: int):
        self.page_index_box.valueChanged.disconnect(self.Action_PageChangeAlt)
        self.animation_slider.valueChanged.disconnect(self.Action_PageChange)

        self.page_index_box.setMaximum(value+1)
        self.animation_slider.setMaximum(value)
        self.page_count_label.setText(f"/ {value+1}")

        self.animation_slider.valueChanged.connect(self.Action_PageChange)
        self.page_index_box.valueChanged.connect(self.Action_PageChangeAlt)

    def OnEvent_ExtraValue(self, value: int):
        self.page_index_box.valueChanged.disconnect(self.Action_PageChangeAlt)
        self.animation_slider.valueChanged.disconnect(self.Action_PageChange)

        self.page_index_box.setValue(value+1)
        self.animation_slider.setValue(value)

        if self.View().state_animation:
            self.path_label.setVisible(False)
            self.animation_slider.setVisible(True)
            self.play_pause_button.setVisible(True)
        else:
            self.path_label.setVisible(True)
            self.animation_slider.setVisible(False)
            self.play_pause_button.setVisible(False)

        self.animation_slider.valueChanged.connect(self.Action_PageChange)
        self.page_index_box.valueChanged.connect(self.Action_PageChangeAlt)

    def OnEvent_ExtraLabel(self, value: str):
        self.path_label.setText(value)

        if self.View().anim_timer.isActive():
            self.play_pause_button.setIcon(KritaAPI.get_icon("media-playback-stop"))
        else:
            self.play_pause_button.setIcon(KritaAPI.get_icon("media-playback-start"))

        if self.View().state_animation: self.page_label.setText("Frame:")
        elif self.View().state_compact: self.page_label.setText("Page:")
        else: self.page_label.setText("Index:")
        
        

    def OnEvent_RandomIndexRequested(self):
        self.Action_RandomizeIndex()
    
    #endregion

    #region Action Functions

    def Action_PlayPause(self):
        is_playing = self.View().anim_timer.isActive()
        if is_playing: self.View().Anim_Pause()
        else: self.View().Anim_Play()

    def Action_RandomizeIndex(self):
        is_compact = self.View().state_compact
        is_anim = self.View().state_animation
        
        if is_compact: list_size = self.View().comp_count
        elif is_anim: list_size = self.View().anim_count
        else: list_size = None

        if list_size == None: return

        random.seed( int( QtCore.QTime.currentTime( ).toString( 'hhmmssms' ) ) )
        new_index = random.randint( 0, list_size )

        if is_compact: self.View().Comp_Index(new_index)
        elif is_anim: self.View().Anim_Frame(new_index)

    def Action_PageChangeAlt(self, value: int):
        actual_value = value - 1
        if self.View().state_compact: self.View().Comp_Index(actual_value)
        elif self.View().state_animation: self.View().Anim_Frame(actual_value)

    def Action_PageChange(self, value: int):
        if self.View().state_compact: self.View().Comp_Index(value)
        elif self.View().state_animation: self.View().Anim_Frame(value)

    def Action_PageLeft(self):
        if self.View().state_compact: self.View().Comp_Back()
        elif self.View().state_animation: self.View().Anim_Back()

    def Action_PageRight(self):
        if self.View().state_compact: self.View().Comp_Forward()
        elif self.View().state_animation: self.View().Anim_Forward()
    
    #endregion

    #region Event Functions

    def hideEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().hideEvent(a0)
    
    def showEvent(self, a0):
        self.SIGNAL_VISIBILITY_CHANGED.emit()
        return super().showEvent(a0)
    
    #endregion