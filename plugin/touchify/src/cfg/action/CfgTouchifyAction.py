from touchify.src.cfg.action.CfgTouchifyActionDockerGroup import CfgTouchifyActionDockerGroup
from touchify.src.cfg.action.CfgTouchifyActionPopup import CfgTouchifyActionPopup
from touchify.src.cfg.action.CfgTouchifyActionCanvasPreset import CfgTouchifyActionCanvasPreset
from touchify.src.ext.types.StrEnum import StrEnum
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat

class CfgTouchifyAction:
     
    class Variants(StrEnum):
        Action = "action"
        Menu = "menu"
        Brush = "brush"
        Popup = "popup"
        Docker = "docker"
        Workspace = "workspace"
        DockerGroup = "docker_group"
        CanvasPreset = "canvas_preset"
        
    id: str = ""      
    icon: str = ""
    text: str = ""
    variant: str = "action"
    show_text: bool = False
    show_icon: bool = True
    closes_popup: bool = False

    #Action Params
    action_id: str = ""
    action_use_icon: bool = False
    action_composer_mode: bool = False

    #Menu Params
    context_menu_actions: TypedList["CfgTouchifyAction"] = []

    #Brush Params
    brush_name: str = ""
    brush_override_icon: bool = False
    
    #Docker Params
    docker_id: str = ""
    
    #Workspace Params
    workspace_id: str = ""
    
    #Docker Group Params
    docker_group_data: CfgTouchifyActionDockerGroup = CfgTouchifyActionDockerGroup()
    
    #Popup Params
    popup_data: CfgTouchifyActionPopup = CfgTouchifyActionPopup()

    #Canvas Preset Params
    canvas_preset_data: CfgTouchifyActionCanvasPreset = CfgTouchifyActionCanvasPreset()
    

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgTouchifyAction(args)
        Extensions.dictToObject(self, args, [CfgTouchifyActionPopup, CfgTouchifyActionDockerGroup, CfgTouchifyActionCanvasPreset])
        
        self.context_menu_actions = Extensions.init_list(args, "context_menu_actions", CfgTouchifyAction)
        

    def __str__(self):
        match self.variant:
            case CfgTouchifyAction.Variants.Action:
                prefix = "[Action] "
                suffix = self.action_id
            case CfgTouchifyAction.Variants.Menu:
                prefix = "[Menu] "
                suffix = self.text
            case CfgTouchifyAction.Variants.Brush:
                prefix = "[Brush] "
                suffix = self.brush_name
            case CfgTouchifyAction.Variants.Popup:
                prefix = "[Popup] "
                suffix = self.text
            case CfgTouchifyAction.Variants.Workspace:
                prefix = "[Workspace] "
                suffix = self.workspace_id
            case CfgTouchifyAction.Variants.Docker:
                prefix = "[Docker] "
                suffix = self.docker_id
            case CfgTouchifyAction.Variants.DockerGroup:
                prefix = "[Docker Group] "
                suffix = self.text
            case CfgTouchifyAction.Variants.CanvasPreset:
                prefix = "[Canvas Preset] "
                suffix = self.text
            case _:
                prefix = f"[{self.variant}] "
                suffix = self.text
                
        if self.text != "":
            suffix = self.text
        
        return prefix + suffix

    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, CfgTouchifyAction)
        
    def propertygrid_sorted(self):
        return [
            "id",
            "icon",
            "text",
            "show_text",
            "show_icon",
            "closes_popup",
            "variant",
            #Action Params
            "action_id",
            "action_use_icon",
            "action_composer_mode"
            #Menu Params
            "context_menu_actions",
            #Brush Params
            "brush_name",
            "brush_override_icon",       

            "docker_id",
            "workspace_id",
            "docker_group_data",
            "popup_data",
            "canvas_preset_data"
        ]

    def propertygrid_hidden(self):
        result = []
        if self.variant != CfgTouchifyAction.Variants.Action:
            result.append("action_id")
            result.append("action_use_icon")
            result.append("action_composer_mode")
        if self.variant != CfgTouchifyAction.Variants.Menu:
            result.append("context_menu_actions")            
        if self.variant != CfgTouchifyAction.Variants.Brush:
            result.append("brush_name")
            result.append("brush_override_icon")
        if self.variant != CfgTouchifyAction.Variants.Workspace:
            result.append("workspace_id")
        if self.variant != CfgTouchifyAction.Variants.Docker:
            result.append("docker_id")
        if self.variant != CfgTouchifyAction.Variants.Popup:
            result.append("popup_data")
        if self.variant != CfgTouchifyAction.Variants.DockerGroup:
            result.append("docker_group_data")
        if self.variant != CfgTouchifyAction.Variants.CanvasPreset:
            result.append("canvas_preset_data")

        return result
    
    def propertygrid_hints(self):
        hints = {}
        hints["closes_popup"] = "If the action is contained within a Touchify popup, toggling this will make it close when you trigger it"
        return hints

    def propertygrid_labels(self):
        labels = {}
        
        labels["id"] = "ID"
        labels["icon"] = "Icon"
        labels["text"] = "Text"
        labels["variant"] = "Action Type"
        labels["show_text"] = "Show Text"
        labels["show_icon"] = "Show Icon"
        labels["closes_popup"] = "Close popup on click"
        labels["action_composer_mode"] = "Shortcut Composer Compat"

        labels["action_id"] = "Action ID"
        labels["action_use_icon"] = "Use Action Icon"

        labels["context_menu_actions"] = "Menu Actions"

        labels["brush_name"] = "Brush"
        labels["brush_override_icon"] = "Override Brush Icon"
        
        labels["workspace_id"] = "Workspace ID"
        labels["docker_id"] = "Docker ID"
        
        labels["docker_group_data"] = "Group Settings"
        labels["popup_data"] = "Popup Settings"

        labels["canvas_preset_data"] = "Canvas Settings"

        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["variant"] = {"type": "values", "entries": self.Variants.values()}
        
        restrictions["brush_name"] = {"type": "brush_selection"}
        restrictions["action_id"] = {"type": "action_selection"}
        restrictions["workspace_id"] = {"type": "workspace_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["docker_group_data"] = {"type": "expandable"}
        restrictions["popup_data"] = {"type": "expandable"}
        restrictions["canvas_preset_data"] = {"type": "expandable"}
        return restrictions