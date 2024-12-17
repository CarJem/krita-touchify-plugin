






class Helpers:
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
        return Helpers.getVersion(args) == -1

class BackwardsCompatibility:

    def Trigger(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "showText", "show_text")
            Helpers.changeVarName(args, "showIcon", "show_icon")
            Helpers.setVersion(args, 1)
        if Helpers.getVersion(args) == 1:
            Helpers.changeVarName(args, "id", "registry_id")

            Helpers.changeVarName(args, "action_composer_mode", "extra_composer_mode")
            Helpers.changeVarName(args, "closes_popup", "extra_closes_popup")

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
            Helpers.setVersion(args, 2)
        return args

    def DockerGroup(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "groupId", "group_id")
            Helpers.changeVarName(args, "tabsMode", "tabs_mode")
            Helpers.setVersion(args, 1)
        return args

    def ToolshelfData(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "actionHeight", "action_height")
            Helpers.changeVarName(args, "presetName", "preset_name")
            Helpers.setVersion(args, 1)
        if Helpers.getVersion(args) == 1:
            Helpers.changeVarName(args, "panels", "pages")
            Helpers.setVersion(args, 2)
        if Helpers.getVersion(args) == 2:
            args["homepage"] = {}
            if "sections" in args: args["homepage"]["sections"] = args["sections"]
            if "actions" in args: args["homepage"]["actions"] = args["actions"]
            if "tab_type" in args: args["homepage"]["tab_type"] = args["tab_type"]
            if "action_height" in args: args["homepage"]["action_height"] = args["action_height"]
            Helpers.setVersion(args, 3)
        return args
    
    def ToolshelfDataPage(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "actionHeight", "action_height")
            Helpers.setVersion(args, 1)
        if Helpers.getVersion(args) == 1:
            Helpers.changeVarName(args, "row", "toolshelf_tab_row")
            Helpers.setVersion(args, 2)
        return args

    def ToolshelfDataSection(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args) or Helpers.getVersion(args) == 1:
            Helpers.changeVarName(args, "id", "docker_id")
            Helpers.changeVarName(args, "action_section_name", "action_section_id")
            Helpers.setVersion(args, 2)
        if Helpers.getVersion(args) == 2:
            Helpers.changeVarName(args, "action_section_alignment_x", "section_alignment_x")
            Helpers.changeVarName(args, "action_section_alignment_y", "section_alignment_y")
            Helpers.setVersion(args, 3)
        if Helpers.getVersion(args) == 3:
            Helpers.changeVarName(args, "section_alignment_x", "action_section_alignment_x")
            Helpers.changeVarName(args, "section_alignment_y", "action_section_alignment_y")
            Helpers.setVersion(args, 4)
        return args
  
    def PopupData(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "btnName", "display_name")
            Helpers.setVersion(args, 1)
        if Helpers.getVersion(args) == 1:
            Helpers.changeVarName(args, "display_name", "window_title")
            if "type" in args:
                if args["type"] == "docker":
                    Helpers.changeVarName(args, "actions_item_width", "docker_width")
                    Helpers.changeVarName(args, "actions_item_height", "docker_height")
            Helpers.setVersion(args, 2)
        if Helpers.getVersion(args) == 2:
            Helpers.changeVarName(args, "opacity", "actions_opacity")
            Helpers.setVersion(args, 3)
        if Helpers.getVersion(args) == 3:
            Helpers.changeVarName(args, "popup_position", "popup_position_x")
            if "popup_position_x" in args: args["popup_position_y"] = args["popup_position_x"]
            Helpers.setVersion(args, 4)
        if Helpers.getVersion(args) == 4:
            Helpers.changeVarName(args, "docker_width", "popup_width")
            Helpers.changeVarName(args, "docker_height", "popup_height")            
            Helpers.setVersion(args, 5)
        return args

    def ToolboxData(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "presetName", "preset_name")
            Helpers.setVersion(args, 1)
        return args
    
    def ToolboxDataItem(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.setVersion(args, 1)

        #print(args)

        return args
