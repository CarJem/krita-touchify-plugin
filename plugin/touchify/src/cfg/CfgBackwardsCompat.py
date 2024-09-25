
class Helpers:
    def setVersion(args: dict[str, any], ver: int):
        args["json_version"] = ver

    def changeVarName(args: dict[str, any], oldName: str, newName: str):
        if oldName in args: args[newName] = args[oldName]

    def isLegacyConfig(args: dict[str, any]):
        return "json_version" not in args

class CfgBackwardsCompat:
    def CfgToolboxItem(args: dict[str, any]):
        if not args: return args
        return args

    def CfgTouchifyAction(args: dict[str, any]):
        if not args: return args
        if "json_version" not in args:
            Helpers.changeVarName(args, "showText", "show_text")
            Helpers.changeVarName(args, "showIcon", "show_icon")
            Helpers.setVersion(args, 1)
        return args

    def CfgTouchifyActionDockerGroup(args: dict[str, any]):
        if not args: return args
        if "json_version" not in args:
            Helpers.changeVarName(args, "groupId", "group_id")
            Helpers.changeVarName(args, "tabsMode", "tabs_mode")
            Helpers.setVersion(args, 1)
        return args

    def CfgToolshelfPanel(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "actionHeight", "action_height")
            Helpers.setVersion(args, 1)
        return args

    def CfgToolshelf(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "actionHeight", "action_height")
            Helpers.changeVarName(args, "presetName", "preset_name")
            Helpers.setVersion(args, 1)
        return args
    
    def CfgTouchifyActionPopup(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "btnName", "display_name")
            Helpers.setVersion(args, 1)
        return args

    def CfgToolbox(args: dict[str, any]):
        if not args: return args
        if Helpers.isLegacyConfig(args):
            Helpers.changeVarName(args, "presetName", "preset_name")
            Helpers.setVersion(args, 1)
        return args