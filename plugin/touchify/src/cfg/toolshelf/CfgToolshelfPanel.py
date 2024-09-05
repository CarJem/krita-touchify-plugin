from ..action.CfgTouchifyAction import *
from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from .CfgToolshelfSection import CfgToolshelfSection
from ..action.CfgTouchifyActionCollection import CfgTouchifyActionCollection

class CfgToolshelfPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    section_show_tabs: bool = False
    section_show_root_actions: bool = False
    
    actionHeight: int = 10

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        sections = Extensions.default_assignment(args, "sections", [])
        actions = Extensions.default_assignment(args, "actions", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)
        self.actions = Extensions.list_assignment(actions, CfgTouchifyActionCollection)

    def forceLoad(self):
        self.sections = TypedList(self.sections, CfgToolshelfSection)
        self.actions = TypedList(self.actions, CfgTouchifyActionCollection)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["size"] = {"name": "Panel Width / Height", "items": ["size_x","size_y"]}
        return row

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID (must be unique)"
        labels["icon"] = "Display Icon"
        labels["size_x"] = "Panel Width"
        labels["size_y"] = "Panel Height"
        labels["row"] = "Tab Row"
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        labels["actionHeight"] = "Action Button Height"
        labels["section_show_tabs"] = "Show Page Tabs"
        labels["section_show_root_actions"] = "Show Root Actions"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        return restrictions
