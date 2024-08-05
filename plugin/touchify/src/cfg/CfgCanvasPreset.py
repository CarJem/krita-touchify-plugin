from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from ..ext.KritaSettings import *
from ..ext.extensions_json import *
from ..ext.extensions_krita import *

class CfgCanvasPreset:
    def __init__(self):
        self.presetName = "New Preset"
        
        self.subgroup_enabled: bool = False
        self.subgroup_name: str = ""
        
        self.checkers_main_color: KS_Color = KS_Color()
        self.checkers_alt_color: KS_Color = KS_Color()
        self.checkers_size: int = 32
        self.checkers_enabled: bool = False
        
        self.pixgrid_color: KS_Color = KS_Color(255, 255, 255)
        self.pixgrid_threshold: float = 24
        self.pixgrid_enabled: bool = False
        
        self.selection_outline_opacity: float = 1.0
        self.selection_overlay_color: KS_Color = KS_Color(255, 0, 0)
        self.selection_overlay_opacity: float = 0.5
        self.selection_enabled: bool = False
        
        self.border_color: KS_Color = KS_Color(128, 128, 128)
        self.border_enabled: bool = False
             
    def loads(self, _dict: dict[str, any]):
        if _dict is not None:
            for key, value in _dict.items():
                if hasattr(self, key):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif isinstance(getattr(self, key), KS_Color):
                        setattr(self, key, KS_Color(value["r"], value["g"], value["b"]))
                               
    def activate(self): 
        if self.checkers_enabled:
            KritaSettings.writeSettingColor("", "checkerscolor", self.checkers_main_color)
            KritaSettings.writeSettingColor("", "checkerscolor2", self.checkers_alt_color)
            KritaSettings.writeSettingInt("", "checkSize", self.checkers_size)
            
        if self.pixgrid_enabled:
            KritaSettings.writeSettingColor("", "pixelGridColor", self.pixgrid_color)
            KritaSettings.writeSettingFloat("", "pixelGridDrawingThreshold", self.pixgrid_threshold)
        
        if self.selection_enabled:
            KritaSettings.writeSettingFloat("", "selectionOutlineOpacity", self.selection_outline_opacity)
            KritaSettings.writeSettingColor("", "selectionOverlayMaskColor", self.selection_overlay_color.setOpacityFloat(self.selection_overlay_opacity))
        
        if self.border_enabled:
            KritaSettings.writeSettingColor("", "canvasBorderColor", self.border_color)
        
    def current():
        result = CfgCanvasPreset()
        
        result.checkers_main_color = KritaSettings.readSettingColor("", "checkerscolor", KS_Color())
        result.checkers_alt_color = KritaSettings.readSettingColor("", "checkerscolor2", KS_Color())
        result.checkers_size = KritaSettings.readSettingInt("", "checkSize", 32)
            
        result.pixgrid_color = KritaSettings.readSettingColor("", "pixelGridColor", KS_Color(255, 255, 255))
        result.pixgrid_threshold = KritaSettings.readSettingFloat("", "pixelGridDrawingThreshold", 24)
        
        result.selection_outline_opacity = KritaSettings.readSettingFloat("", "selectionOutlineOpacity", 1.0)
        
        selection_overlay: KS_AlphaColor = KritaSettings.readSettingAlphaColor("", "selectionOverlayMaskColor", KS_AlphaColor(255,0,0,128))
        result.selection_overlay_color = selection_overlay.noAlpha()
        result.selection_overlay_opacity = selection_overlay.getOpacityFloat()
        
        result.border_color = KritaSettings.readSettingColor("", "canvasBorderColor", KS_Color(128, 128, 128))
    
        return result
    