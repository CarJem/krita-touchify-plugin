from ..action.CfgTouchifyAction import *
from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from .CfgToolshelfPanel import CfgToolshelfPanel
from .CfgToolshelfSection import CfgToolshelfSection
from ..action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
   
class CfgToolshelf:
    panels: TypedList[CfgToolshelfPanel] = []
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    
    canvas_enable_resizing_by_default: bool = False
    dockerButtonHeight: int = 32
    dockerBackHeight: int = 16
    actionHeight: int = 16

    presetName: str = "New Toolshelf Preset"

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        panels = Extensions.default_assignment(args, "panels", [])
        self.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgTouchifyActionCollection)
        sections = Extensions.default_assignment(args, "sections", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)
    

    def __str__(self):
        return self.presetName.replace("\n", "\\n")

    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolshelfPanel)
        self.actions = TypedList(self.actions, CfgTouchifyActionCollection)
        self.sections = TypedList(self.sections, CfgToolshelfSection)

    def propertygrid_sorted(self):
        return [
            "presetName",
            "panels",
            "actions",
            "sections",
            "canvas_enable_resizing_by_default",
            "actionHeight"
            "dockerButtonHeight",
            "dockerBackHeight"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["presetName"] = "Preset Name"
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["sections"] = "Sections"
        labels["dockerButtonHeight"] = "Docker Button Height"
        labels["dockerBackHeight"] = "Back Button Height"
        labels["actionHeight"] = "Action Button Height"
        labels["canvas_enable_resizing_by_default"] = "Enable Canvas Widget\nResizing by Default"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        return restrictions


