from .CfgDockerGroup import CfgDockerGroupItem
from ..ext.StrEnum import StrEnum
from ..ext.TypedList import TypedList
from ..ext.extensions_json import JsonExtensions as Extensions


    
class CfgTouchifyAction:
    
    class ActionType(StrEnum):
        Action = "action"
        Menu = "menu"
        Brush = "brush"
        Popup = "popup"
        Docker = "docker"
        Workspace = "workspace"
        
        
    icon: str = ""
    row: int = 0
    text: str = ""
    use_icon: bool = True
    text_and_icon: bool = False
    action_type: str = "action"

    #Action Params
    action_id: str = ""
    action_use_default_icon: bool = False

    #Menu Params
    context_menu_actions: TypedList["CfgTouchifyAction"] = []
    context_menu_name: str = ""

    #Brush Params
    brush_name: str = ""
    brush_override_icon: bool = False
    
    #Docker Params
    docker_id: str = ""
    
    #Workspace Params
    workspace_id: str = ""
    
    #Docker Group Params
    docker_group_data: CfgDockerGroupItem

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        
        context_menu_actions = Extensions.default_assignment(args, "context_menu_actions", [])
        self.context_menu_actions = Extensions.list_assignment(context_menu_actions, CfgTouchifyAction)

    def __str__(self):
        name = self.action_id.replace("\n", "\\n")
        match self.action_type:
            case CfgTouchifyAction.ActionType.Action:
                prefix = "[Action] "
            case CfgTouchifyAction.ActionType.Menu:
                prefix = "[Menu] "
            case CfgTouchifyAction.ActionType.Brush:
                prefix = "[Brush] "
            case CfgTouchifyAction.ActionType.Popup:
                prefix = "[Popup] "
            case CfgTouchifyAction.ActionType.Workspace:
                prefix = "[Workspace] "
            case CfgTouchifyAction.ActionType.Docker:
                prefix = "[Docker] "
            case _:
                prefix = ""
        
        return prefix + name

    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, CfgTouchifyAction)

    def propertygrid_hidden(self):
        result = []
        if self.action_type != CfgTouchifyAction.ActionType.Action:
            result.append("action_id")
            result.append("action_use_default_icon")
        if self.action_type != CfgTouchifyAction.ActionType.Menu:
            result.append("context_menu_name")
            result.append("context_menu_actions")            
        if self.action_type != CfgTouchifyAction.ActionType.Brush:
            result.append("brush_name")
            result.append("brush_override_icon")
        if self.action_type != CfgTouchifyAction.ActionType.Workspace:
            result.append("workspace_id")
        if self.action_type != CfgTouchifyAction.ActionType.Docker:
            result.append("docker_id")

        return result

    def propertygrid_labels(self):
        labels = {}
        labels["action_id"] = "Action ID"
        labels["icon"] = "Display Icon"
        labels["row"] = "Tab Row"
        labels["text"] = "Text"
        labels["action_type"] = "Action Type"
        labels["use_icon"] = "Use Icon"
        labels["text_and_icon"] = "Show Text & Icon"

        labels["action_use_default_icon"] = "Use Default Icon"

        labels["context_menu_name"] = "Menu Name"
        labels["context_menu_actions"] = "Menu Actions"

        labels["brush_name"] = "Brush"
        labels["brush_override_icon"] = "Override Brush Icon"
        
        labels["workspace_id"] = "Workspace ID"
        
        labels["docker_id"] = "Docker ID"
        
        labels["docker_group_tabs_mode"] = "Tabs Mode"
        labels["docker_group_tab_id"] = "Tab ID"
        labels["docker_group_dockers"] = "Dockers"

        return labels

    def propertygrid_groups(self):
        groups = {}
        return groups

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["action_type"] = {"type": "values", "entries": self.ActionType.values()}
        restrictions["brush_name"] = {"type": "brush_selection"}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["action_id"] = {"type": "action_selection"}
        restrictions["workspace_id"] = {"type": "workspace_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        return restrictions