import string
from ..action.CfgTouchifyAction import *
from ...ext.TypedList import TypedList
from ...ext.extensions_json import JsonExtensions as Extensions
from .CfgToolshelfPanel import CfgToolshelfPanel
from .CfgToolshelfSection import CfgToolshelfSection
from ..action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from .CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
   
class CfgToolshelf:
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    actionHeight: int = 16
    tab_type: str = "buttons"
    
    panels: TypedList[CfgToolshelfPanel] = []
    header_options: CfgToolshelfHeaderOptions = CfgToolshelfHeaderOptions()
    presetName: str = "New Toolshelf Preset"

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args, [CfgToolshelfHeaderOptions])
        panels = Extensions.default_assignment(args, "panels", [])
        self.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgTouchifyActionCollection)
        sections = Extensions.default_assignment(args, "sections", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.presetName if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

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
            "header_options",
            "tabType",
            "actionHeight"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["presetName"] = "Preset Name"
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["sections"] = "Sections"
        labels["tabType"] = "Tab Type"
        labels["actionHeight"] = "Action Button Height"
        labels["header_options"] = "Header Options"
        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["tabType"] = {"type": "values", "entries": ["buttons", "tabs"]}
        restrictions["header_options"] = {"type": "expandable"}
        return restrictions


