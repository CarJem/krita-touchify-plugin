








class CompatHelpers:
    def setVersion(args: dict[str, any], ver: int):
        args["json_version"] = ver

    def getVersion(args: dict[str, any]):
        if "json_version" not in args: return -1
        else: 
            try:
                return int(args["json_version"])
            except:
                return -1

    def changeVarName(args: dict[str, any], oldName: str, newName: str):
        if oldName in args: args[newName] = args[oldName]

    def isLegacyConfig(args: dict[str, any]):
        return CompatHelpers.getVersion(args) == -1

class Compat:

    def Trigger(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.changeVarName(args, "showText", "show_text")
            CompatHelpers.changeVarName(args, "showIcon", "show_icon")
            CompatHelpers.setVersion(args, 1)
        if CompatHelpers.getVersion(args) == 1:
            CompatHelpers.changeVarName(args, "id", "registry_id")

            CompatHelpers.changeVarName(args, "action_composer_mode", "extra_composer_mode")
            CompatHelpers.changeVarName(args, "closes_popup", "extra_closes_popup")

            text: str = ""
            icon: str = ""
            show_text: bool = True
            action_use_icon: bool = False
            brush_override_icon: bool = False
            custom_icon: bool = False
            variant: str = "default"

            if "variant" in args: variant = args["variant"]
            if "text" in args: text = args["text"]
            if "icon" in args: icon = args["icon"]
            if "show_text" in args: show_text = args["show_text"]
            if "action_use_icon" in args: action_use_icon = args["action_use_icon"]
            if "brush_override_icon" in args: brush_override_icon = args["brush_override_icon"]

            if variant == "brush":
                custom_icon = brush_override_icon
            elif variant == "action": 
                custom_icon = not action_use_icon
            elif icon != "": 
                custom_icon = True

            args["display_custom_icon_enabled"] = custom_icon
            args["display_custom_text_enabled"] = text != ""

            args["display_custom_text"] = text
            args["display_custom_icon"] = icon

            args["display_text_hide"] = not show_text
            args["display_icon_hide"] = False
            CompatHelpers.setVersion(args, 2)
        if CompatHelpers.getVersion(args) == 2:
            CompatHelpers.changeVarName(args, "context_menu_id", "refrenced_menu")
            CompatHelpers.changeVarName(args, "docker_group_data", "refrenced_dockergroup")
            CompatHelpers.changeVarName(args, "popup_data", "refrenced_popup")
            CompatHelpers.changeVarName(args, "canvas_preset_data", "refrenced_canvaspreset")
            CompatHelpers.changeVarName(args, "script_id", "refrenced_script")
            CompatHelpers.changeVarName(args, "piewheel_id", "refrenced_piewheel")
            CompatHelpers.setVersion(args, 3)
        return args
    
    def TriggerContextMenu(args: dict[str, any]):
        if not args: return args
        
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.setVersion(args, 1)

        if CompatHelpers.getVersion(args) == 1:
            CompatHelpers.setVersion(args, 2)

        return args

    def DockerGroup(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.changeVarName(args, "groupId", "group_id")
            CompatHelpers.changeVarName(args, "tabsMode", "tabs_mode")
            CompatHelpers.setVersion(args, 1)
        return args

    def ToolshelfDock(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.getVersion(args) == 4:
            CompatHelpers.changeVarName(args, "size_x", "docker_size_hint_x")
            CompatHelpers.changeVarName(args, "size_y", "docker_size_hint_y")
            CompatHelpers.setVersion(args, 5)
        if CompatHelpers.getVersion(args) == 5:
            
            CompatHelpers.changeVarName(args, "requires_specific_tool", "section_requirements")
            if "invert_required_tools" in args: mod = "NOT" if bool(args["invert_required_tools"]) else "OR"
            else: mod = "OR"


            if "section_requirements" in args:
                results = str(args["section_requirements"])
                if results != "":
                    results = mod + "||Tool||" + results
                    results = results.replace(",", "," + mod + "||Tool||")
                    args["section_requirements"] = results
                    
            CompatHelpers.setVersion(args, 6)
        return args
  
    def PopupData(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.changeVarName(args, "btnName", "display_name")
            CompatHelpers.setVersion(args, 1)
        if CompatHelpers.getVersion(args) == 1:
            CompatHelpers.changeVarName(args, "display_name", "window_title")
            if "type" in args:
                if args["type"] == "docker":
                    CompatHelpers.changeVarName(args, "actions_item_width", "docker_width")
                    CompatHelpers.changeVarName(args, "actions_item_height", "docker_height")
            CompatHelpers.setVersion(args, 2)
        if CompatHelpers.getVersion(args) == 2:
            CompatHelpers.changeVarName(args, "opacity", "actions_opacity")
            CompatHelpers.setVersion(args, 3)
        if CompatHelpers.getVersion(args) == 3:
            CompatHelpers.changeVarName(args, "popup_position", "popup_position_x")
            if "popup_position_x" in args: args["popup_position_y"] = args["popup_position_x"]
            CompatHelpers.setVersion(args, 4)
        if CompatHelpers.getVersion(args) == 4:
            CompatHelpers.changeVarName(args, "docker_width", "popup_width")
            CompatHelpers.changeVarName(args, "docker_height", "popup_height")            
            CompatHelpers.setVersion(args, 5)
        return args

    def ToolboxData(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.changeVarName(args, "presetName", "preset_name")
            CompatHelpers.setVersion(args, 1)
        return args
    
    def ToolboxDataItem(args: dict[str, any]):
        if not args: return args
        if CompatHelpers.isLegacyConfig(args):
            CompatHelpers.setVersion(args, 1)

        return args
