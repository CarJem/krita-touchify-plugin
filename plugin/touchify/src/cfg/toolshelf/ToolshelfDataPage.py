from touchify.src.cfg.toolshelf.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.ext.types.StrEnum import StrEnum
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility


class ToolshelfDataPage:


    class TabType(StrEnum):
        Buttons = "buttons"
        Tabs = "tabs"
    
    def __defaults__(self):
        self.id: str = ""
        self.display_name: str = ""
        self.actions: TypedList[TriggerGroup] = []
        self.sections: TypedList[ToolshelfDataSection] = []
        self.tab_type: str = "buttons"
        self.action_height: int = 10

        self.icon: str = ""
        self.toolshelf_tab_row: int = 0

        self.size_x: int = 0
        self.size_y: int = 0
        self.min_size_x: int = 0
        self.min_size_y: int = 0
        self.max_size_x: int = 0
        self.max_size_y: int = 0

        self.json_version: int = 2

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfDataPage(args)
        Extensions.dictToObject(self, args)
        self.sections = Extensions.init_list(args, "sections", ToolshelfDataSection)
        self.actions = Extensions.init_list(args, "actions", TriggerGroup)

    def hasDisplayName(self):
        return self.display_name != None and self.display_name != "" and self.display_name.isspace() == False

    def forceLoad(self):
        self.sections = TypedList(self.sections, ToolshelfDataSection)
        self.actions = TypedList(self.actions, TriggerGroup)

    def __str__(self):
        name = self.id.replace("\n", "\\n")
        return name
    
    def propertygrid_hints(self):
        hints = {}
        hints["id"] = "The internal ID for this panel; best that it be something unique"
        hints["display_name"] = "The display text used for this panel when needed"
        hints["icon"] = "The custom icon used when this panel is used as a page for a toolshelf or when needed"
        hints["size"] = "the size of this panel; leave set to 0 for automatic sizing"
        hints["max_size"] = "the maximum size of this panel; leave set to 0 for automatic sizing"
        hints["min_size"] = "the minimum size of this panel; leave set to 0 for automatic sizing"
        return hints
    
    def propertygrid_view_type(self):
        return "tabs_vertical"
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["page_options"] = {"items": [ "toolshelf_tab_row", "tab_type", "action_height", "size", "max_size", "min_size"], "is_group": True}
        row["metadata"] = {"items": [ "id", "display_name", "icon"], "is_group": True}

        row["size"] = {"items": ["size_x","size_y"]}
        row["max_size"] = {"items": ["max_size_x","max_size_y"]}
        row["min_size"] = {"items": ["min_size_x","min_size_y"]}
        return row
    
    def propertygrid_sorted(self):
        return [
            "metadata",
            "page_options",
            "sections",
            "actions"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["metadata"] = "Metadata"
        labels["id"] = "Panel ID"
        labels["display_name"] = "Display Name"
        labels["icon"] = "Display Icon"


        labels["page_options"] = "Settings"
        labels["action_height"] = "Action Button Height"
        labels["tab_type"] = "Tab Type"
        labels["toolshelf_tab_row"] = "Toolshelf Tab Row"
        labels["size"] = "Panel Width / Height"
        labels["max_size"] = "Panel Max Width / Height"
        labels["min_size"] = "Panel Min Width / Height"
        
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["toolshelf_tab_row"] = {"type": "range", "min": 0}
        restrictions["size_x"] = {"type": "range", "min": 0}
        restrictions["size_y"] = {"type": "range", "min": 0}
        restrictions["max_size_x"] = {"type": "range", "min": 0}
        restrictions["max_size_y"] = {"type": "range", "min": 0}
        restrictions["min_size_x"] = {"type": "range", "min": 0}
        restrictions["min_size_y"] = {"type": "range", "min": 0}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["tab_type"] = {"type": "values", "entries": self.TabType.values()}
        return restrictions
