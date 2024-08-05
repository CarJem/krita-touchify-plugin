from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions
    
class CfgToolshelfAction:
    icon: str = ""
    row: int = 0
    text: str = ""
    use_icon: bool = True

    action_type: str = "action"

    action_id: str = ""
    action_use_default_icon: bool = False

    context_menu_actions: TypedList["CfgToolshelfAction"] = []
    context_menu_name: str = ""

    brush_name: str = ""
    brush_override_icon: bool = False

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        context_menu_actions = Extensions.default_assignment(args, "context_menu_actions", [])
        self.context_menu_actions = Extensions.list_assignment(context_menu_actions, CfgToolshelfAction)

    def __str__(self):
        if self.action_type == "brush":
            name = self.brush_name.replace("\n", "\\n") + " (Brush)"
        elif self.action_type == "menu":
            name = self.context_menu_name.replace("\n", "\\n") + " (Menu)"
        else:
            name = self.action_id.replace("\n", "\\n")
        return name

    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, CfgToolshelfAction)

    def propertygrid_hidden(self):
        result = []
        if self.action_type != "action":
            result.append("action_id")
            result.append("action_use_default_icon")
        if self.action_type != "menu":
            result.append("context_menu_name")
            result.append("context_menu_actions")
        if self.action_type != "brush":
            result.append("brush_name")
            result.append("brush_override_icon")
        if self.action_type == "brush" and self.brush_override_icon == False:
            result.append("icon")
            result.append("use_icon")
            result.append("text")
        result.append("text" if self.use_icon else "icon")
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["action_id"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["row"] = "Tab Row"
        labels["action_type"] = "Action Type"
        labels["use_icon"] = "Use Icon"

        labels["action_use_default_icon"] = "Use Default Icon"

        labels["context_menu_name"] = "Menu Name"
        labels["context_menu_actions"] = "Menu Actions"

        labels["brush_name"] = "Brush"
        labels["brush_override_icon"] = "Override Brush Icon"

        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["action_type"] = {"type": "values", "entries": ["action", "menu", "brush"]}
        restrictions["brush_name"] = {"type": "brush_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action_id"] = {"type": "action_selection"}
        return restrictions