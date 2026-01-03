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
        Color = "color"
        Brush = "brush"
        Docker = "docker"
        Workspace = "workspace"
        Menu = "#menu"
        Script ="#script"
        
        Shared_Menu = "menu"
        Shared_Popup = "popup"
        Shared_Docker_Group = "docker_group"
        Shared_Canvas_Preset = "canvas_preset"
        Shared_Pie_Wheel = "pie_wheel"
        Shared_Script = "script"

    def __defaults__(self):
        from touchify.src.config.menu.TriggerMenu import TriggerMenu
        from touchify.src.config.script.CustomScript import CustomScript

        self.registry_id: str = "NewTrigger"      
        self.variant: str = "action"

        #Icon Params
        self.display_icon_hide: bool = False
        self.display_icon_padding: int = 0
        self.display_custom_icon_enabled: bool = False
        self.display_custom_icon: str = ""

        #Text Params
        self.display_text_hide: bool = False
        self.display_custom_text_enabled: bool = False
        self.display_custom_text: str = ""

        #Extras Params
        self.extra_closes_popup: bool = False
        self.extra_composer_mode: bool = False

        #Variant Values
        self.action_id: str = ""
        self.brush_name: str = ""
        self.docker_id: str = ""
        self.workspace_id: str = ""      
        self.color_id: str = "#000000"
        self.menu_data: TriggerMenu = TriggerMenu()
        self.script_data: CustomScript = CustomScript()
        
        #Variant Refrences
        self.refrenced_menu: str = ""  
        self.refrenced_dockergroup: str = "none"
        self.refrenced_popup: str = "none"
        self.refrenced_canvaspreset: str = "none"
        self.refrenced_script: str = ""
        self.refrenced_piewheel: str = ""

        self.json_version: int = 3
    

    def __init__(self, **args) -> None:
        from touchify.src.config.menu.TriggerMenu import TriggerMenu
        from touchify.src.config.script.CustomScript import CustomScript

        self.__is_registry = False
        self.__defaults__()
        args = BackwardsCompatibility.Trigger(args)
        JsonExtensions.dictToObject(self, args, [TriggerMenu, CustomScript])

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

        use_custom_icon: bool = self.display_custom_icon_enabled and self.display_custom_icon != ""

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
                case Trigger.Variants.Brush:
                    text = self.brush_name
                case Trigger.Variants.Workspace:
                    text = self.workspace_id
                case Trigger.Variants.Docker:
                    text = self.docker_id
                case Trigger.Variants.Color:
                    text = self.color_id
                case Trigger.Variants.Menu:
                    text = self.menu_data.getDisplayName()
                case Trigger.Variants.Script:
                    text = self.script_data.script_name
                case Trigger.Variants.Shared_Menu:
                    text = self.refrenced_menu
                case Trigger.Variants.Shared_Popup:
                    text = self.refrenced_popup
                case Trigger.Variants.Shared_Docker_Group:
                    text = self.refrenced_dockergroup
                case Trigger.Variants.Shared_Canvas_Preset:
                    text = self.refrenced_canvaspreset
                case Trigger.Variants.Shared_Script:
                    text = self.refrenced_script
                case Trigger.Variants.Shared_Pie_Wheel:
                    text = self.refrenced_piewheel
                case _:
                    text = self.registry_id

        return text


    def __str__(self):
        match self.variant:
            case Trigger.Variants.Action:
                prefix = "[Action]"
            case Trigger.Variants.Menu:
                prefix = "[Menu]"
            case Trigger.Variants.Shared_Menu:
                prefix = "[Menu]"
            case Trigger.Variants.Brush:
                prefix = "[Brush]"
            case Trigger.Variants.Shared_Popup:
                prefix = "[Popup]"
            case Trigger.Variants.Workspace:
                prefix = "[Workspace]"
            case Trigger.Variants.Docker:
                prefix = "[Docker]"
            case Trigger.Variants.Shared_Docker_Group:
                prefix = "[Docker Group]"
            case Trigger.Variants.Shared_Canvas_Preset:
                prefix = "[Canvas Preset]"
            case Trigger.Variants.Script:
                prefix = "[Script]"
            case Trigger.Variants.Shared_Script:
                prefix = "[Script]"
            case Trigger.Variants.Shared_Pie_Wheel:
                prefix = "[Pie Wheel]"
            case Trigger.Variants.Color:
                prefix = "[Color]"
            case _:
                prefix = f"[{self.variant}]"
        
        return f"{prefix} {self.getDisplayName()}"

    def propertygrid_icon(self):
        return self.getDisplayIcon()

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["text_options"] = { "items": ["display_text_hide", "display_custom_text_enabled", "display_custom_text"], "use_labels": True, "flip_labels": True}
        row["icon_options"] = { "items": ["display_icon_hide", "display_icon_padding", "display_custom_icon_enabled", "display_custom_icon"], "use_labels": True, "flip_labels": True}
        row["extra_options"] = {"items": ["extra_closes_popup","extra_composer_mode"], "use_labels": True}
        return row

    def propertygrid_sorted(self):
        return [
            "registry_id",

            "#NEW_SECTION",

            "variant",
            "action_id",
            "brush_name",
            "docker_id",
            "workspace_id",
            "menu_data",
            "script_data",
            "refrenced_menu",
            "refrenced_dockergroup",
            "refrenced_popup",
            "refrenced_canvaspreset",
            "refrenced_script",
            "refrenced_piewheel",
            "color_id",

            "text_options",

            "#NEW_COLUMN",

            "extra_options",
            "icon_options",

            "#NEW_SECTION"


        ]

    def propertygrid_hidden(self):
        result = []

        try:
            if self.__is_registry == False:
                result.append("registry_id")
        except:
            pass



        if self.variant != Trigger.Variants.Action:
            result.append("action_id")
        if self.variant != Trigger.Variants.Shared_Menu:
            result.append("refrenced_menu")            
        if self.variant != Trigger.Variants.Brush:
            result.append("brush_name")
        if self.variant != Trigger.Variants.Workspace:
            result.append("workspace_id")
        if self.variant != Trigger.Variants.Docker:
            result.append("docker_id")
        if self.variant != Trigger.Variants.Shared_Popup:
            result.append("refrenced_popup")
        if self.variant != Trigger.Variants.Shared_Docker_Group:
            result.append("refrenced_dockergroup")
        if self.variant != Trigger.Variants.Shared_Canvas_Preset:
            result.append("refrenced_canvaspreset")
        if self.variant != Trigger.Variants.Shared_Script:
            result.append("refrenced_script")
        if self.variant != Trigger.Variants.Shared_Pie_Wheel:
            result.append("refrenced_piewheel")
        if self.variant != Trigger.Variants.Color:
            result.append("color_id")
        if self.variant != Trigger.Variants.Menu:
            result.append("menu_data")
        if self.variant != Trigger.Variants.Script:
            result.append("script_data")

        if self.variant == Trigger.Variants.Color:
            result.append("display_opt")
            result.append("display_icon_padding")
            result.append("display_text_hide")
            result.append("display_icon_hide")
            result.append("icon_options")
            result.append("text_options")
            result.append("extra_options")
            result.append("extra_closes_popup")
            result.append("extra_composer_mode")

        if self.display_custom_icon_enabled == False:
            result.append("display_custom_icon")
        
        if self.display_custom_text_enabled == False:
            result.append("display_custom_text")

        return result
    
    def propertygrid_hints(self):
        hints = {}
        hints["extra_closes_popup"] = "If the action is contained within a Touchify popup, toggling this will make it close when you trigger it"
        return hints

    def propertygrid_labels(self):
        labels = {}
        
        labels["registry_id"] = "Registry ID"
        labels["variant"] = "Action Type"

        labels["text_options"] = "Text Settings"
        labels["display_text_hide"] = "Hide Text"
        labels["display_custom_text_enabled"] = "Override Text"
        labels["display_custom_text"] = ""
        
        labels["icon_options"] = "Icon Settings"
        labels["display_icon_hide"] ="Hide Icon"
        labels["display_icon_padding"] = "Icon Padding"
        labels["display_custom_icon_enabled"] = "Override Icon"
        labels["display_custom_icon"] = ""
        

        labels["extra_options"] = "Extra Options"
        labels["extra_closes_popup"] = "Close popup on click"
        labels["extra_composer_mode"] = "Shortcut Composer Compat"

        labels["action_id"] = "Action ID"

        labels["refrenced_menu"] = "Menu ID"

        labels["brush_name"] = "Brush"
        
        labels["workspace_id"] = "Workspace ID"
        labels["docker_id"] = "Docker ID"
        labels["refrenced_script"] = "Script ID"
        labels["color_id"] = "Selected Color"
        
        labels["refrenced_dockergroup"] = "Group Settings"
        labels["refrenced_popup"] = "Popup Settings"


        labels["refrenced_canvaspreset"] = "Canvas Settings"

        return labels
    
    def propertygrid_listload(self):
        pass

    def propertygrid_listmod(self, mods: list[any]):
        for mod in mods:
            if mod == PropertyGrid_TouchifyRestrictions.StrListModParams.IsRegistry:
                self.__is_registry = True

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["display_custom_icon"] = DataConstraints.strMod(DataConstraints.StrMod.IconSelection)
        restrictions["display_custom_text"] = DataConstraints.strPlaceholder("(unset text)")
        restrictions["display_icon_padding"] = DataConstraints.range(min=0)
        restrictions["variant"] = DataConstraints.strEnumValues(self.Variants)
        restrictions["brush_name"] = DataConstraints.strMod(DataConstraints.StrMod.BrushSelection)
        restrictions["action_id"] = DataConstraints.strMod(DataConstraints.StrMod.ActionSelection)
        restrictions["workspace_id"] = DataConstraints.strMod(DataConstraints.StrMod.WorkspaceSelection)
        restrictions["docker_id"] = DataConstraints.strMod(DataConstraints.StrMod.DockerSelection)
        restrictions["menu_data"] = DataConstraints.expandable("...")
        restrictions["script_data"] = DataConstraints.expandable("...")
        restrictions["refrenced_dockergroup"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.DockerGroupRegistry)
        restrictions["refrenced_popup"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.PopupRegistry)
        restrictions["refrenced_canvaspreset"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.CanvasPresetRegistry)
        restrictions["refrenced_menu"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.MenuRegistry)
        restrictions["refrenced_script"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.ScriptRegistry)
        restrictions["refrenced_piewheel"] = PropertyGrid_TouchifyRestrictions.strRegistryMod(PropertyGrid_TouchifyRestrictions.StrRegistryMod.PieWheelRegistry)
        restrictions["color_id"] = DataConstraints.strMod(DataConstraints.StrMod.ColorPicker)
        
        return restrictions