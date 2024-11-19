from touchify.src.ext.types.StrEnum import StrEnum
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.toolshelf.CfgToolshelfSection import CfgToolshelfSection
from touchify.src.cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat


class CfgToolshelfPanel:


    class TabType(StrEnum):
        Buttons = "buttons"
        Tabs = "tabs"
    
    id: str = ""
    display_name: str = ""
    icon: str = ""
    size_x: int = 0
    size_y: int = 0
    row: int = 0
    actions: TypedList[CfgTouchifyActionCollection] = []
    sections: TypedList[CfgToolshelfSection] = []
    tab_type: str = "buttons"
    action_height: int = 10

    json_version: int = 1

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolshelfPanel(args)
        Extensions.dictToObject(self, args)
        self.sections = Extensions.init_list(args, "sections", CfgToolshelfSection)
        self.actions = Extensions.init_list(args, "actions", CfgTouchifyActionCollection)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def forceLoad(self):
        self.sections = TypedList(self.sections, CfgToolshelfSection)
        self.actions = TypedList(self.actions, CfgTouchifyActionCollection)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name
    
    def propertygrid_hints(self):
        hints = {}
        hints["id"] = "The internal ID for this panel; best that it be something unique"
        hints["display_name"] = "The display text used for this panel when needed"
        hints["icon"] = "The custom icon used when this panel is used as a page for a toolshelf or when needed"
        hints["size"] = "the size of this panel; leave set to 0 for automatic sizing"
        return hints
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["size"] = {"items": ["size_x","size_y"]}
        return row
    
    def propertygrid_sorted(self):
        return [
            "id",
            "display_name",
            "icon",
            "sections",
            "actions"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Panel ID"
        labels["display_name"] = "Display Name"
        labels["icon"] = "Display Icon"
        labels["size"] = "Panel Width / Height"
        labels["row"] = "Tab Row"
        labels["tab_type"] = "Tab Type"
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        labels["action_height"] = "Action Button Height"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["tab_type"] = {"type": "values", "entries": self.TabType.values()}
        return restrictions
