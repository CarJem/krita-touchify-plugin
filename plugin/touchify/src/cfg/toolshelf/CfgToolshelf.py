import string

from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat
from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from touchify.src.cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from touchify.src.cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from touchify.src.cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions



   
class CfgToolshelf:
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    action_height: int = 16
    tab_type: str = "buttons"
    
    panels: TypedList[CfgToolshelfPanel] = []
    header_options: CfgToolshelfHeaderOptions = CfgToolshelfHeaderOptions()
    preset_name: str = "New Toolshelf Preset"

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolshelf(args)
        Extensions.dictToObject(self, args, [CfgToolshelfHeaderOptions])
        panels = Extensions.default_assignment(args, "panels", [])
        self.panels = Extensions.list_assignment(panels, CfgToolshelfPanel)
        actions = Extensions.default_assignment(args, "actions", [])
        self.actions = Extensions.list_assignment(actions, CfgTouchifyActionCollection)
        sections = Extensions.default_assignment(args, "sections", [])
        self.sections = Extensions.list_assignment(sections, CfgToolshelfSection)

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.preset_name if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        self.panels = TypedList(self.panels, CfgToolshelfPanel)
        self.actions = TypedList(self.actions, CfgTouchifyActionCollection)
        self.sections = TypedList(self.sections, CfgToolshelfSection)

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "panels",
            "actions",
            "sections",
            "header_options",
            "tab_type",
            "action_height"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["panels"] = "Panels"
        labels["actions"] = "Actions"
        labels["sections"] = "Sections"
        labels["tab_type"] = "Tab Type"
        labels["header_options"] = "Header Options"
        labels["action_height"] = "Action Button Height"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["tab_type"] = {"type": "values", "entries": ["buttons", "tabs"]}
        restrictions["header_options"] = {"type": "expandable"}
        return restrictions


