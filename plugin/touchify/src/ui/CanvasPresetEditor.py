from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from ..cfg.CfgCanvasPreset import *
from ..ext.KritaSettings import *
from ..ext.extensions_json import *
from ..ext.extensions_krita import *
from touchify.src import stylesheet
import json
import copy

from ..components.krita.KisSliderSpinBox import KisSliderSpinBox
from ..components.krita.KisAngleSelector import KisAngleSelector
from ..components.pyqt.widgets.ColorButton import ColorButton

class CanvasPresetEditor(QDialog):
    def __init__(self, preset: CfgCanvasPreset, parent: QWidget | None = None):
        super().__init__(parent)
        self.accepted.connect(self.updatePreset)
        self.preset: CfgCanvasPreset = preset
        self.setupComponents()
        
    def updatePreset(self):
        self.preset.presetName = self._presetNameEntry.text()
        
        self.preset.subgroup_enabled = self._presetSubgroupGroup.isChecked()
        self.preset.subgroup_name = self._presetSubgroupNameEntry.text()
        
        self.preset.checkers_enabled = self._checkerboard_group.isChecked()
        self.preset.checkers_main_color = KS_Color.fromQt(self._checkerboard_color1.color())
        self.preset.checkers_alt_color = KS_Color.fromQt(self._checkerboard_color2.color())
        self.preset.checkers_size = self._checkerboard_size.value()
        
        self.preset.pixgrid_enabled = self._pixgrid_group.isChecked()
        self.preset.pixgrid_color = KS_Color.fromQt(self._pixgrid_color.color())
        self.preset.pixgrid_threshold = self._pixgrid_threshold.value()
        
        self.preset.selection_enabled = self._selection_group.isChecked()
        self.preset.selection_outline_opacity = self._selection_outline_opacity.value()
        self.preset.selection_overlay_color = KS_Color.fromQt(self._selection_overlay_color.color())
        self.preset.selection_overlay_opacity = self._selection_overlay_opacity.value()
        
        self.preset.border_enabled = self._checkerboard_group.isChecked()
        self.preset.border_color = KS_Color.fromQt(self._border_color.color())
        
    def setupComponents(self):
        self._gridLayout = QFormLayout(self)
        self.setLayout(self._gridLayout)
            
        self._buttonBox = QDialogButtonBox()
        self._saveBtn = self._buttonBox.addButton(QDialogButtonBox.StandardButton.Save)
        self._saveBtn.clicked.connect(self.accept)
        self._cancelBtn = self._buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._cancelBtn.clicked.connect(self.reject)
        
        self._presetNameEntry = QLineEdit()
        self._presetNameEntry.setText(self.preset.presetName)
        
        #region Subgroup
        self._presetSubgroupGroup = QGroupBox(self)
        self._presetSubgroupGroup.setCheckable(True)
        self._presetSubgroupGroup.setChecked(self.preset.subgroup_enabled)
        self._presetSubgroupGroup.setTitle("Preset Subgroup:")
        self._presetSubgroupLayout = QFormLayout(self._presetSubgroupGroup)     
        self._presetSubgroupNameEntry = QLineEdit()
        self._presetSubgroupNameEntry.setText(self.preset.subgroup_name)
        self._presetSubgroupLayout.addRow("Subgroup Name: ", self._presetSubgroupNameEntry)
        self._presetSubgroupGroup.setLayout(self._presetSubgroupLayout)
        #endregion
        
        #region Checkerboard
        self._checkerboard_group = QGroupBox(self)
        self._checkerboard_group.setCheckable(True)
        self._checkerboard_group.setChecked(self.preset.checkers_enabled)
        self._checkerboard_group.setTitle("Transparency Checkerboard:")
        self._checkerboard_layout = QFormLayout(self._checkerboard_group)     
        self._checkerboard_color1 = ColorButton(self, self.preset.checkers_main_color.toQt())
        self._checkerboard_color2 = ColorButton(self, self.preset.checkers_alt_color.toQt())
        self._checkerboard_size = QSpinBox(self)
        self._checkerboard_size.setMinimum(0)
        self._checkerboard_size.setMaximum(256)
        self._checkerboard_size.setSuffix(" px")
        self._checkerboard_size.setValue(self.preset.checkers_size)    
        self._checkerboard_layout.addRow("Color 1: ", self._checkerboard_color1)
        self._checkerboard_layout.addRow("Color 2: ", self._checkerboard_color2)
        self._checkerboard_layout.addRow("Size: ", self._checkerboard_size)
        self._checkerboard_group.setLayout(self._checkerboard_layout)
        #endregion
        
        #region Pixel Grid
        self._pixgrid_group = QGroupBox(self)
        self._pixgrid_group.setCheckable(True)
        self._pixgrid_group.setChecked(self.preset.pixgrid_enabled)
        self._pixgrid_group.setTitle("Selection Overlay:")
        self._pixgrid_layout = QFormLayout(self._pixgrid_group)      
        self._pixgrid_color = ColorButton(self, self.preset.pixgrid_color.toQt())       
        self._pixgrid_threshold = QDoubleSpinBox(self)
        self._pixgrid_threshold.setMinimum(0)
        self._pixgrid_threshold.setMaximum(99)
        self._pixgrid_threshold.setDecimals(2)
        self._pixgrid_threshold.setSuffix("%")
        self._pixgrid_threshold.setValue(self.preset.pixgrid_threshold)    
        self._pixgrid_layout.addRow("Color: ", self._pixgrid_color)
        self._pixgrid_layout.addRow("Start showing at: ", self._pixgrid_threshold)
        self._pixgrid_group.setLayout(self._pixgrid_layout)
        #endregion
        
        #region Selection Overlay
        self._selection_group = QGroupBox(self)
        self._selection_group.setCheckable(True)
        self._selection_group.setChecked(self.preset.selection_enabled)
        self._selection_group.setTitle("Selection Overlay:")
        self._selection_layout = QFormLayout(self._selection_group)      
        self._selection_outline_opacity = KisSliderSpinBox(0, 1, False, self)
        self._selection_outline_opacity.setValue(self.preset.selection_outline_opacity)   
        self._selection_overlay_color = ColorButton(self, self.preset.selection_overlay_color.toQt())     
        self._selection_overlay_opacity = KisSliderSpinBox(0, 1, False, self)
        self._selection_overlay_opacity.setValue(self.preset.selection_overlay_opacity)  
        self._selection_layout.addRow("Outline Opacity: ", self._selection_outline_opacity)
        self._selection_layout.addRow("Overlay Color: ", self._selection_overlay_color)
        self._selection_layout.addRow("Overlay Opacity: ", self._selection_overlay_opacity)
        self._selection_group.setLayout(self._selection_layout)
        #endregion
        
        #region Canvas Border
        self._border_group = QGroupBox(self)
        self._border_group.setCheckable(True)
        self._border_group.setChecked(self.preset.border_enabled)
        self._border_group.setTitle("Canvas Border:")
        self._border_layout = QFormLayout(self._border_group)      
        self._border_color = ColorButton(self, self.preset.border_color.toQt())       
        self._border_layout.addRow("Color: ", self._border_color)
        self._border_group.setLayout(self._border_layout)
        #endregion
        
        self._gridLayout.addRow("Preset Name:", self._presetNameEntry)
        self._gridLayout.addWidget(self._presetSubgroupGroup)
        self._gridLayout.addWidget(self._checkerboard_group)
        self._gridLayout.addWidget(self._border_group)
        self._gridLayout.addWidget(self._pixgrid_group)
        self._gridLayout.addWidget(self._selection_group)
        self._gridLayout.addWidget(self._buttonBox)