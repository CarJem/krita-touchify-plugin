from PyQt5.QtWidgets import QWidget
from krita import *
from PyQt5.QtCore import *
from ...ext.KritaSettings import *
from ...ext.KritaExtensions import *
from ...ext.JsonExtensions import JsonExtensions as Extensions

class CfgTouchifyActionCanvasPreset:
    checkers_main_color: KS_Color = KS_Color()
    checkers_alt_color: KS_Color = KS_Color()
    checkers_size: int = 32
    checkers_enabled: bool = False

    pixgrid_color: KS_Color = KS_Color(255, 255, 255)
    pixgrid_threshold: float = 24
    pixgrid_enabled: bool = False

    selection_outline_opacity: float = 1.0
    selection_overlay_color: KS_Color = KS_Color(255, 0, 0)
    selection_overlay_opacity: float = 0.5
    selection_enabled: bool = False

    border_color: KS_Color = KS_Color(128, 128, 128)
    border_enabled: bool = False

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args, [KS_Color])
                               
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
        result = CfgTouchifyActionCanvasPreset()
        
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

       
    def propertygrid_sorted(self):
        return [
            # Checkers Params
            "checkers_enabled",
            "checkers_main_color",
            "checkers_alt_color",
            "checkers_size",
            # PixGrid Params
            "pixgrid_enabled",
            "pixgrid_color",
            "pixgrid_threshold",
            # Selection Params
            "selection_enabled",
            "selection_outline_opacity",
            "selection_overlay_color",
            "selection_overlay_opacity",
            # Border Params
            "border_enabled",
            "border_color"
        ]

    def propertygrid_hidden(self):
        result = []
        if self.checkers_enabled == False:
            result.append("checkers_main_color")
            result.append("checkers_alt_color")
            result.append("checkers_size")
        if self.pixgrid_enabled == False:
            result.append("pixgrid_color")            
            result.append("pixgrid_threshold")            
        if self.selection_enabled == False:
            result.append("selection_outline_opacity")
            result.append("selection_overlay_color")
            result.append("selection_overlay_opacity")
        if self.border_enabled == False:
            result.append("border_color")

        return result

    def propertygrid_labels(self):
        labels = {}
        labels["checkers_enabled"] = "Checkers"
        labels["checkers_main_color"] = "Main Color"
        labels["checkers_alt_color"] = "Alt Color"
        labels["checkers_size"] = "Size"

        labels["pixgrid_enabled"] = "Pixel Grid"
        labels["pixgrid_color"] = "Color"
        labels["pixgrid_threshold"] = "Threshold"

        labels["selection_enabled"] = "Selection Preview"
        labels["selection_outline_opacity"] = "Outline Opacity"
        labels["selection_overlay_color"] = "Overlay Color"
        labels["selection_overlay_opacity"] = "Overlay Opacity"

        labels["border_enabled"] = "Border"
        labels["border_color"] = "Color"
        return labels

    def propertygrid_restrictions(self):   
        restrictions = {}
        restrictions["checkers_size"]  = {"type": "range", "min": 0}
        restrictions["pixgrid_threshold"] = {"type": "range", "min": 0}
        restrictions["selection_outline_opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        restrictions["selection_overlay_opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        return restrictions