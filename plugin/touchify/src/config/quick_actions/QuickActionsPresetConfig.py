from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints as RS

class QuickActionsPresetConfig:

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
        self.layout = QuickActionsPresetConfig.Layout()
        JsonExtensions.dictToObject(self, args, [QuickActionsPresetConfig.Layout])
        
    def propertygrid_sorted(self):
        return [
            "layout",
        ]
    
    def propertygrid_hidden(self):
        return []

    def propertygrid_labels(self):
        labels = {}
        labels["layout"] = "Layout"
        return labels
    
    def propertygrid_view_type(self):
        return "sections"
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["layout"] = RS.expandable()
        return restrictions

