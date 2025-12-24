from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class CommonConfig:

    class Color:
        def __init__(self, **args) -> None:
            self.docker_button_font_color: str = "#000000"
            self.docker_button_background_color: str = "#63666a"
            self.shortcut_button_font_color: str = "#eaeaea"
            self.shortcut_button_background_color: str = "#2a1c2a"
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_view_type(self):
            return "form_alt"

    class Font:
        def __init__(self, **args) -> None:
            self.docker_button_font_size: str = "10px"
            self.shortcut_button_font_size: str = "14px"
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_view_type(self):
            return "form_alt"

    class Shortcut:
        def __init__(self, **args) -> None:
            self.add_brush_to_grid = "W"
            self.choose_left_in_grid = ","
            self.choose_right_in_grid = "."
            self.wrap_around_navigation = True
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_view_type(self):
            return "form_alt"

    class Layout:
        def __init__(self, **args) -> None:
            self.max_shortcut_per_row = 4
            self.max_brush_per_row = 8
            self.spacing_between_buttons = 1
            self.spacing_between_grids = 1
            self.brush_icon_size = 65
            self.display_brush_names = True
            self.exclusive_uncollapse = False
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_view_type(self):
            return "form_alt"

    class BrushSlider:
        def __init__(self, **args) -> None:
            self.max_brush_size = 1000
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_view_type(self):
            return "form_alt"

    def __init__(self, **args) -> None:
        self.color = CommonConfig.Color()
        self.font = CommonConfig.Font()
        self.shortcut = CommonConfig.Shortcut()
        self.layout = CommonConfig.Layout()
        self.brush_slider = CommonConfig.BrushSlider()
        JsonExtensions.dictToObject(self, args, [CommonConfig.Color, CommonConfig.Font, CommonConfig.Shortcut, CommonConfig.Layout, CommonConfig.BrushSlider])
        
    def propertygrid_sorted(self):
        return [
            "color",
            "font",
            "shortcut",
            "layout",
            "brush_slider"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["color"] = "Color"
        labels["font"] = "Font"
        labels["shortcut"] = "Shortcut"
        labels["layout"] = "Layout"
        labels["brush_slider"] = "Brush Slider"
        return labels
    
    def propertygrid_view_type(self):
        return "sections"
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["metadata"] = RS.expandable()
        restrictions["color"] = RS.expandable()
        restrictions["font"] = RS.expandable()
        restrictions["shortcut"] = RS.expandable()
        restrictions["layout"] = RS.expandable()
        restrictions["brush_slider"] = RS.expandable()
        return restrictions

