from touchify.src.config.toolshelf_legacy.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.datatypes.metaclass.EnumStr import EnumStr
from touchify.src.datatypes.sequence.TypedList import TypedList
from touchify.src.extensions.json_extensions import JsonExtensions
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions


class ToolshelfDataPage:


    class TabType(EnumStr):
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

        self.json_version: int = 2

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolshelfDataPage(args)
        JsonExtensions.dictToObject(self, args)
        self.sections = JsonExtensions.init_list(args, "sections", ToolshelfDataSection)
        self.actions = JsonExtensions.init_list(args, "actions", TriggerGroup)

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
        return hints
    
    def propertygrid_view_type(self):
        return "tabs_vertical"
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["page_options"] = {"items": [ "toolshelf_tab_row", "tab_type", "action_height"], "is_group": True}
        row["metadata"] = {"items": [ "id", "display_name", "icon"], "is_group": True}
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
        
        labels["sections"] = "Sections"
        labels["actions"] = "Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["toolshelf_tab_row"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["icon"] = PropertyGrid_Restrictions.strMod(PropertyGrid_Restrictions.StrMod.IconSelection)
        restrictions["tab_type"] = PropertyGrid_Restrictions.strValues(self.TabType.values())
        return restrictions
