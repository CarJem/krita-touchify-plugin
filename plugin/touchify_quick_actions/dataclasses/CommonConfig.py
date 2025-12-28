from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class CommonConfig:

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
            self.max_brush_per_row = 8
            self.spacing_between_buttons = 1
            self.spacing_between_grids = 1
            self.brush_icon_size = 65
            self.list_mode = False
            self.list_column_count = 1
            self.display_brush_names = True
            self.exclusive_uncollapse = False
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_labels(self):
            labels = {}
            labels["max_brush_per_row"] = "Max buttons per row"
            labels["spacing_between_buttons"] = "Spacing between buttons"
            labels["spacing_between_grids"] = "Spacing between grids"
            labels["brush_icon_size"] = "Button icon size"
            labels["list_mode"] = "List mode"
            labels["list_column_count"] = "Number of list columns"
            labels["display_brush_names"] = "Display brush names"
            labels["exclusive_uncollapse"] = "Exclusive uncollapse"
            return labels
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["max_brush_per_row"] = RS.range(min=1)
            restrictions["spacing_between_buttons"] = RS.range(min=0)
            restrictions["spacing_between_grids"] = RS.range(min=0)
            restrictions["brush_icon_size"] = RS.range(min=4)
            restrictions["list_column_count"] = RS.range(min=1)
            return restrictions

        def propertygrid_view_type(self):
            return "form_alt"
        
    def __init__(self, **args) -> None:
        #self.shortcut = CommonConfig.Shortcut()
        self.layout = CommonConfig.Layout()
        JsonExtensions.dictToObject(self, args, [CommonConfig.Shortcut, CommonConfig.Layout])
        
    def propertygrid_sorted(self):
        return [
            "shortcut",
            "layout",
        ]
    
    def propertygrid_hidden(self):
        return [
            "shortcut"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["shortcut"] = "Shortcut"
        labels["layout"] = "Layout"
        return labels
    
    def propertygrid_view_type(self):
        return "sections"
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["layout"] = RS.expandable()
        return restrictions

