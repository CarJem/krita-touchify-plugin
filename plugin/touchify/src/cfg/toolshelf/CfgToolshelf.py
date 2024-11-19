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
    pages: TypedList[CfgToolshelfPanel] = []

    action_height: int = 16
    tab_type: str = "buttons"
    
    header_options: CfgToolshelfHeaderOptions = CfgToolshelfHeaderOptions()
    preset_name: str = "New Toolshelf Preset"

    json_version: int = 2

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolshelf(args)
        Extensions.dictToObject(self, args, [CfgToolshelfHeaderOptions])
        self.pages = Extensions.init_list(args, "pages", CfgToolshelfPanel)
        self.actions = Extensions.init_list(args, "actions", CfgTouchifyActionCollection)
        self.sections = Extensions.init_list(args, "sections", CfgToolshelfSection)

    def getFileName(self):
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in self.preset_name if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename.lower()    

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def forceLoad(self):
        self.pages = TypedList(self.pages, CfgToolshelfPanel)
        self.actions = TypedList(self.actions, CfgTouchifyActionCollection)
        self.sections = TypedList(self.sections, CfgToolshelfSection)

    def propertygrid_sorted(self):
        return [
            "preset_name",
            "pages",
            "actions",
            "sections",
            "header_options",
            "tab_type",
            "action_height"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["pages"] = "Pages"
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


