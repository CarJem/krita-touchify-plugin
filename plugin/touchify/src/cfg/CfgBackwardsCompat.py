class CfgBackwardsCompat:
    def CfgTouchifyAction(args: dict[str, any]):
        if args:
            if "showText" in args:
                args["show_text"] = args["showText"]
            if "showIcon" in args:
                args["show_icon"] = args["showIcon"]
        return args

    def CfgTouchifyActionDockerGroup(args: dict[str, any]):
        if args:
            if "groupId" in args:
                args["group_id"] = args["groupId"]
            if "tabsMode" in args:
                args["tabs_mode"] = args["tabsMode"]
        return args

    def CfgToolshelfPanel(args: dict[str, any]):
        if args:
            if "actionHeight" in args:
                args["action_height"] = args["actionHeight"]
        return args

    def CfgToolshelf(args: dict[str, any]):
        if args:
            if "actionHeight" in args:
                args["action_height"] = args["actionHeight"]
            if "presetName" in args:
                args["preset_name"] = args["presetName"]
        return args
    
    def CfgTouchifyActionPopup(args: dict[str, any]):
        if args:
            if "btnName" in args:
                args["display_name"] = args["btnName"]
        return args

    def CfgToolbox(args: dict[str, any]):
        if args:
            if "presetName" in args:
                args["preset_name"] = args["presetName"]
        return args