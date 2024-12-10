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

    registry_id: str = ""      
    variant: str = "action"

    #Display Params
    display_icon_hide: bool = False
    display_text_hide: bool = False
    display_custom_icon_enabled: bool = False
    display_custom_icon: str = ""
    display_custom_text_enabled: bool = True
    display_custom_text: str = ""

    #Extras Params
    extra_closes_popup: bool = False
    extra_composer_mode: bool = False

    #Action Params
    action_id: str = ""

    #Menu Params
    context_menu_actions: TypedList["CfgTouchifyAction"] = []

    #Brush Params
    brush_name: str = ""
    
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

    json_version: int = 2
    

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
                suffix = self.display_custom_text
            case CfgTouchifyAction.Variants.Brush:
                prefix = "[Brush] "
                suffix = self.brush_name
            case CfgTouchifyAction.Variants.Popup:
                prefix = "[Popup] "
                suffix = self.display_custom_text
            case CfgTouchifyAction.Variants.Workspace:
                prefix = "[Workspace] "
                suffix = self.workspace_id
            case CfgTouchifyAction.Variants.Docker:
                prefix = "[Docker] "
                suffix = self.docker_id
            case CfgTouchifyAction.Variants.DockerGroup:
                prefix = "[Docker Group] "
                suffix = self.display_custom_text
            case CfgTouchifyAction.Variants.CanvasPreset:
                prefix = "[Canvas Preset] "
                suffix = self.display_custom_text
            case _:
                prefix = f"[{self.variant}] "
                suffix = self.display_custom_text
                
        if self.display_custom_text != "":
            suffix = self.display_custom_text
        
        return prefix + suffix


    def forceLoad(self):
        self.context_menu_actions = TypedList(self.context_menu_actions, CfgTouchifyAction)

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["display_custom_text_opt"] = {"items": ["display_custom_text_enabled","display_custom_text"]}
        row["display_custom_icon_opt"] = {"items": ["display_custom_icon_enabled","display_custom_icon"]}
        row["display_opt"] = {"items": ["display_text_hide","display_icon_hide"], "use_labels": True}
        row["extra_opt"] = {"items": ["extra_closes_popup","extra_composer_mode"], "use_labels": True}
        return row

    def propertygrid_sorted(self):
        return [
            "registry_id",
            #Display Params
            "display_custom_text_enabled",
            "display_custom_icon_enabled",
            #Special Options
            "extra_closes_popup",
            #Common Params
            "variant",
            #Action Params
            "action_id",
            #Menu Params
            "context_menu_actions",
            #Brush Params
            "brush_name",
            #Others
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
        if self.variant != CfgTouchifyAction.Variants.Menu:
            result.append("context_menu_actions")            
        if self.variant != CfgTouchifyAction.Variants.Brush:
            result.append("brush_name")
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
        hints["extra_closes_popup"] = "If the action is contained within a Touchify popup, toggling this will make it close when you trigger it"
        return hints

    def propertygrid_labels(self):
        labels = {}
        
        labels["registry_id"] = "Registry ID"
        labels["variant"] = "Action Type"

        labels["display_opt"] = "Display Options"
        labels["display_custom_text_opt"] = "Custom Text"
        labels["display_custom_icon_opt"] = "Custom Icon"
        labels["display_text_hide"] = "Hide Text"
        labels["display_icon_hide"] ="Hide Icon"

        labels["extra_opt"] = "Extra Options"
        labels["extra_closes_popup"] = "Close popup on click"
        labels["extra_composer_mode"] = "Shortcut Composer Compat"

        labels["action_id"] = "Action ID"

        labels["context_menu_actions"] = "Menu Actions"

        labels["brush_name"] = "Brush"
        
        labels["workspace_id"] = "Workspace ID"
        labels["docker_id"] = "Docker ID"
        
        labels["docker_group_data"] = "Group Settings"
        labels["popup_data"] = "Popup Settings"

        labels["canvas_preset_data"] = "Canvas Settings"

        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["display_custom_icon"] = {"type": "icon_selection"}
        restrictions["variant"] = {"type": "values", "entries": self.Variants.values()}
        restrictions["brush_name"] = {"type": "brush_selection"}
        restrictions["action_id"] = {"type": "action_selection"}
        restrictions["workspace_id"] = {"type": "workspace_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["docker_group_data"] = {"type": "expandable"}
        restrictions["popup_data"] = {"type": "expandable"}
        restrictions["canvas_preset_data"] = {"type": "expandable"}
        return restrictions