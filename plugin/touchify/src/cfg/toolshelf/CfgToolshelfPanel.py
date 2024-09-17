from ..action.CfgTouchifyAction import *
from ...ext.types.TypedList import TypedList
from ...ext.JsonExtensions import JsonExtensions as Extensions
from .CfgToolshelfSection import CfgToolshelfSection
from ..action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from ..CfgBackwardsCompat import CfgBackwardsCompat


class CfgToolshelfPanel:
    id: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    tab_type: str = "buttons"
    action_height: int = 10

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolshelfPanel(args)
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
    
    def propertygrid_sorted(self):
        return [
            "id",
            "icon",
            "sections",
            "actions"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID (must be unique)"
        labels["icon"] = "Display Icon"
        labels["size_x"] = "Panel Width"
        labels["size_y"] = "Panel Height"
        labels["row"] = "Tab Row"
        labels["tab_type"] = "Tab Type"
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        labels["action_height"] = "Action Button Height"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["tab_type"] = {"type": "values", "entries": ["buttons", "tabs"]}
        return restrictions
