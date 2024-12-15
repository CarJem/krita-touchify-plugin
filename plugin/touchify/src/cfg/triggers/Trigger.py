from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.StrEnum import StrEnum
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility

class Trigger:
     
    class Variants(StrEnum):
        Action = "action"
        Menu = "menu"
        Brush = "brush"
        Popup = "popup"
        Docker = "docker"
        Workspace = "workspace"
        DockerGroup = "docker_group"
        CanvasPreset = "canvas_preset"

    def __defaults__(self):
        self.registry_id: str = ""      
        self.variant: str = "action"

        #Display Params
        self.display_icon_hide: bool = False
        self.display_text_hide: bool = False
        self.display_custom_icon_enabled: bool = False
        self.display_custom_icon: str = ""
        self.display_custom_text_enabled: bool = True
        self.display_custom_text: str = ""

        #Extras Params
        self.extra_closes_popup: bool = False
        self.extra_composer_mode: bool = False

        #Action Params
        self.action_id: str = ""

        #Menu Params
        self.context_menu_id: str = ""

        #Brush Params
        self.brush_name: str = ""
        
        #Docker Params
        self.docker_id: str = ""
        
        #Workspace Params
        self.workspace_id: str = ""
        
        #Docker Group Params
        self.docker_group_data: str = "none"
        
        #Popup Params
        self.popup_data: str = "none"

        #Canvas Preset Params
        self.canvas_preset_data: str = "none"

        self.json_version: int = 2
    

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.Trigger(args)
        Extensions.dictToObject(self, args, [])

    def getFileName(self):
        return FileExtensions.fileStringify(self.registry_id)
        
    def __str__(self):
        match self.variant:
            case Trigger.Variants.Action:
                prefix = "[Action]"
                suffix = self.action_id
            case Trigger.Variants.Menu:
                prefix = "[Menu]"
                suffix = self.display_custom_text
            case Trigger.Variants.Brush:
                prefix = "[Brush]"
                suffix = self.brush_name
            case Trigger.Variants.Popup:
                prefix = "[Popup]"
                suffix = self.display_custom_text
            case Trigger.Variants.Workspace:
                prefix = "[Workspace]"
                suffix = self.workspace_id
            case Trigger.Variants.Docker:
                prefix = "[Docker]"
                suffix = self.docker_id
            case Trigger.Variants.DockerGroup:
                prefix = "[Docker Group]"
                suffix = self.display_custom_text
            case Trigger.Variants.CanvasPreset:
                prefix = "[Canvas Preset]"
                suffix = self.display_custom_text
            case _:
                prefix = f"[{self.variant}]"
                suffix = self.display_custom_text
                
        if self.display_custom_text != "":
            suffix = self.display_custom_text
        
        return f"{suffix} {prefix}"


    def forceLoad(self):
        pass
    

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

            "#NEW_SECTION",
            
            "display_custom_text_opt",
            "display_custom_icon_opt",
            "display_opt",

            "#NEW_COLUMN",

            "variant",
            "action_id",
            "context_menu_id",
            "brush_name",
            "docker_id",
            "workspace_id",
            "docker_group_data",
            "popup_data",
            "canvas_preset_data"
            "extra_opt",
        ]

    def propertygrid_hidden(self):
        result = []
        if self.variant != Trigger.Variants.Action:
            result.append("action_id")
        if self.variant != Trigger.Variants.Menu:
            result.append("context_menu_id")            
        if self.variant != Trigger.Variants.Brush:
            result.append("brush_name")
        if self.variant != Trigger.Variants.Workspace:
            result.append("workspace_id")
        if self.variant != Trigger.Variants.Docker:
            result.append("docker_id")
        if self.variant != Trigger.Variants.Popup:
            result.append("popup_data")
        if self.variant != Trigger.Variants.DockerGroup:
            result.append("docker_group_data")
        if self.variant != Trigger.Variants.CanvasPreset:
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

        labels["context_menu_id"] = "Menu ID"

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
        restrictions["docker_group_data"] = {"type": "registry_docker_group_selection"}
        restrictions["popup_data"] = {"type": "registry_popup_selection"}
        restrictions["canvas_preset_data"] = {"type": "registry_canvas_preset_selection"}
        restrictions["context_menu_id"] = {"type": "registry_menu_selection"}
        return restrictions