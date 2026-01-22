from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class QuickActionsPresetConfig:

    class Shortcut:
        def __init__(self, **args) -> None:
            self.enable_add_brush_to_grid: bool = False
            self.add_brush_to_grid = "W"
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_sisters(self):
            row: dict[str, list[str]] = {}
            row["add_brush_to_grid_group"] = {"items": ["enable_add_brush_to_grid","add_brush_to_grid"]}
            return row

        
        def propertygrid_labels(self):
            labels = {}
            labels["add_brush_to_grid_group"] = "Add Brush to Grid"
            return labels

        def propertygrid_view_type(self):
            return "form_alt"

    class Layout:

        class TabDisplayType(EnumStr):
            Tabs = "tabs"
            Dropdown = "dropdown"

        def __init__(self, **args) -> None:
            self.display_pages_as: str = "tabs"
            JsonExtensions.dictToObject(self, args, [])

        def propertygrid_labels(self):
            labels = {}
            labels["display_pages_as"] = "Display pages as"
            return labels
        
        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["display_pages_as"] = RS.strEnumValues(self.TabDisplayType)
            return restrictions

        def propertygrid_view_type(self):
            return "form_alt"
        
    def __init__(self, **args) -> None:
        self.shortcut = QuickActionsPresetConfig.Shortcut()
        self.layout = QuickActionsPresetConfig.Layout()
        JsonExtensions.dictToObject(self, args, [QuickActionsPresetConfig.Shortcut, QuickActionsPresetConfig.Layout])
        
    def propertygrid_sorted(self):
        return [
            "shortcut",
            "layout",
        ]
    
    def propertygrid_hidden(self):
        return []

    def propertygrid_labels(self):
        labels = {}
        labels["shortcut"] = "Shortcuts"
        labels["layout"] = "Layout"
        return labels
    
    def propertygrid_view_type(self):
        return "sections"
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["layout"] = RS.expandable()
        restrictions["shortcut"] = RS.expandable()
        return restrictions

