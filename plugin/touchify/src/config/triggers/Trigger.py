from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions

from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from touchify.src.alib_propertygrid.data.TouchifyDataConstraints import PropertyGrid_TouchifyRestrictions
from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class Trigger:
     
    class Variants(EnumStr):
        Action = "action"
        Menu = "menu"
        Brush = "brush"
        Popup = "popup"
        Docker = "docker"
        Workspace = "workspace"
        DockerGroup = "docker_group"
        CanvasPreset = "canvas_preset"
        PieWheel = "pie_wheel"
        Script = "script"
        Color = "color"

    def __defaults__(self):
        self.registry_id: str = "NewTrigger"      
        self.variant: str = "action"

        #Display Params
        self.display_icon_hide: bool = False
        self.display_text_hide: bool = False
        self.display_custom_icon_enabled: bool = False
        self.display_custom_icon: str = ""
        self.display_custom_text_enabled: bool = False
        self.display_custom_text: str = ""
        self.display_icon_padding: int = 0

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

        #Script Params
        self.script_id: str = ""

        #Pie Wheel Params
        self.piewheel_id: str = ""

        #Color Params
        self.color_id: str = "#000000"

        self.json_version: int = 2
    

    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.Trigger(args)
        JsonExtensions.dictToObject(self, args, [])

    def getFileName(self):
        return FileExtensions.fileStringify(self.registry_id)
    
    def isActionIcon(self):
        use_custom_icon: bool = self.display_custom_icon_enabled and self.display_custom_icon_enabled != ""
        is_action: bool = self.variant == Trigger.Variants.Action

        if not use_custom_icon and is_action: return True
        else: return False
    
    def hasText(self):
        display_name = self.getDisplayName()
        has_text = display_name != "" and display_name != self.registry_id
        if self.display_text_hide: has_text = False
        return has_text

    def hasIcon(self):
        has_icon = not self.getDisplayIcon().isNull()
        if self.display_icon_hide: has_icon = False
        return has_icon


    def getDisplayIcon(self):
        from jemlib.managers.IconRepository import IconRepository
        from PyQt5.QtGui import QIcon

        use_custom_icon: bool = self.display_custom_icon_enabled and self.display_custom_icon_enabled != ""

        is_brush: bool = self.variant == Trigger.Variants.Brush
        is_action: bool = self.variant == Trigger.Variants.Action

        if use_custom_icon:
            icon = IconRepository.iconLoader(self.display_custom_icon)
        else:
            if is_brush: icon = IconRepository.brushIcon(self.brush_name)
            elif is_action: icon = IconRepository.actionIcon(self.action_id)
            else: icon = QIcon()

        padding = IconRepository.PaddedIcon(icon, self.display_icon_padding)
        result = QIcon(padding)
        return result

    def getDisplayName(self):
        use_custom_text: bool = self.display_custom_text_enabled and self.display_custom_text != ""

        if use_custom_text:
            text: str = self.display_custom_text  
        else:
            match self.variant:
                case Trigger.Variants.Action:
                    text = KritaExtensions.getActionText(self.action_id)
                case Trigger.Variants.Menu:
                    text = self.context_menu_id
                case Trigger.Variants.Brush:
                    text = self.brush_name
                case Trigger.Variants.Popup:
                    text = self.popup_data
                case Trigger.Variants.Workspace:
                    text = self.workspace_id
                case Trigger.Variants.Docker:
                    text = self.docker_id
                case Trigger.Variants.DockerGroup:
                    text = self.docker_group_data
                case Trigger.Variants.CanvasPreset:
                    text = self.canvas_preset_data
                case Trigger.Variants.Script:
                    text = self.script_id
                case Trigger.Variants.PieWheel:
                    text = self.piewheel_id
                case Trigger.Variants.Color:
                    text = self.color_id
                case _:
                    text = self.registry_id

        return text


    def __str__(self):
        match self.variant:
            case Trigger.Variants.Action:
                prefix = "[Action]"
            case Trigger.Variants.Menu:
                prefix = "[Menu]"
            case Trigger.Variants.Brush:
                prefix = "[Brush]"
            case Trigger.Variants.Popup:
                prefix = "[Popup]"
            case Trigger.Variants.Workspace:
                prefix = "[Workspace]"
            case Trigger.Variants.Docker:
                prefix = "[Docker]"
            case Trigger.Variants.DockerGroup:
                prefix = "[Docker Group]"
            case Trigger.Variants.CanvasPreset:
                prefix = "[Canvas Preset]"
            case Trigger.Variants.Script:
                prefix = "[Script]"
            case Trigger.Variants.PieWheel:
                prefix = "[Pie Wheel]"
            case Trigger.Variants.Color:
                prefix = "[Color]"
            case _:
                prefix = f"[{self.variant}]"
        
        return f"{prefix} {self.getDisplayName()}"

    def forceLoad(self):
        pass

    def propertygrid_icon(self):
        return self.getDisplayIcon()

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["display_custom_text_opt"] = {"items": ["display_custom_text_enabled","display_custom_text"]}
        row["display_custom_icon_opt"] = {"items": ["display_custom_icon_enabled","display_custom_icon"]}
        row["display_opt"] = {"items": ["display_text_hide","display_icon_hide"], "use_labels": True}
        row["extra_opt"] = {"items": ["extra_closes_popup","extra_composer_mode"], "use_labels": True}
        return row

    def propertygrid_sorted(self):
        return [
            "#NEW_SECTION",

            "variant",

            "#NEW_COLUMN",

            "action_id",
            "context_menu_id",
            "brush_name",
            "docker_id",
            "workspace_id",
            "docker_group_data",
            "popup_data",
            "canvas_preset_data",
            "script_id",
            "piewheel_id",
            "color_id",

            "#NEW_SECTION",
            
            "display_custom_text_opt",
            "display_opt",

            "#NEW_COLUMN",

            "display_custom_icon_opt",
            "extra_opt",

            "#NEW_SECTION",

            "display_icon_padding",
            "registry_id"
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
        if self.variant != Trigger.Variants.Script:
            result.append("script_id")
        if self.variant != Trigger.Variants.PieWheel:
            result.append("piewheel_id")
        if self.variant != Trigger.Variants.Color:
            result.append("color_id")

        if self.variant == Trigger.Variants.Color:
            result.append("display_opt")
            result.append("display_icon_padding")
            result.append("display_text_hide")
            result.append("display_icon_hide")
            result.append("display_custom_icon_opt")
            result.append("display_custom_text_opt")
            result.append("extra_opt")
            result.append("extra_closes_popup")
            result.append("extra_composer_mode")

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
        labels["display_icon_padding"] = "Icon Padding"

        labels["extra_opt"] = "Extra Options"
        labels["extra_closes_popup"] = "Close popup on click"
        labels["extra_composer_mode"] = "Shortcut Composer Compat"

        labels["action_id"] = "Action ID"

        labels["context_menu_id"] = "Menu ID"

        labels["brush_name"] = "Brush"
        
        labels["workspace_id"] = "Workspace ID"
        labels["docker_id"] = "Docker ID"
        labels["script_id"] = "Script ID"
        labels["color_id"] = "Selected Color"
        
        labels["docker_group_data"] = "Group Settings"
        labels["popup_data"] = "Popup Settings"


        labels["canvas_preset_data"] = "Canvas Settings"

        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["display_custom_icon"] = DataConstraints.strMod(DataConstraints.StrMod.IconSelection)
        restrictions["display_icon_padding"] = DataConstraints.range(min=0)
        restrictions["variant"] = DataConstraints.strValues(self.Variants.values())
        restrictions["brush_name"] = DataConstraints.strMod(DataConstraints.StrMod.BrushSelection)
        restrictions["action_id"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["workspace_id"] = DataConstraints.strMod(DataConstraints.StrMod.WorkspaceSelection)
        restrictions["docker_id"] = DataConstraints.strMod(DataConstraints.StrMod.DockerSelection)
        restrictions["docker_group_data"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.DockerGroupRegistry)
        restrictions["popup_data"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.PopupRegistry)
        restrictions["canvas_preset_data"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.CanvasPresetRegistry)
        restrictions["context_menu_id"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.MenuRegistry)
        restrictions["script_id"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.ScriptRegistry)
        restrictions["piewheel_id"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.PieWheelRegistry)
        restrictions["color_id"] = DataConstraints.strMod(DataConstraints.StrMod.ColorPicker)
        
        return restrictions