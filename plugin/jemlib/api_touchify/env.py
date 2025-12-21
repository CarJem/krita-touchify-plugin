class TouchifyEnv:
    
    class ActionID:
        CONFIGURE="touchify_configure"

        class Styles:
            MENU="touchify_styles_menu"
            BORDERLESSTOOLBARS="touchify_toolbarBorder"
            PRIVACYMODE="Privacy Mode"
            TABHEIGHT="touchify_tabHeight"
            DOCKEDBRUSHEDITOR="touchify_styles_docked_brush_editor"
            DOCKEDBRUSHEDITORZOOMFIX="touchify_styles_brush_editor_zoom_fix"

        class DockerUtils:
            MENU="touchify_dockerutils_menu"
            TOGGLEDOWN="touchify_dockerutils_toggledown"
            TOGGLEUP="touchify_dockerutils_toggleup"
            TOGGLELEFT="touchify_dockerutils_toggleleft"
            TOGGLERIGHT="touchify_dockerutils_toggleright"

        class Other:
            SHOWPOPUPPALETTE="touchify_showPopupPalette"
            SHOWMENUBARPOPUP="touchify_showPopupMenu"

        class TransformTool:
            MENU="Touchify_TransformTool_Menu"
            FREE_FLIPX="Touchify_TransformTool_Free_FlipX"
            FREE_FLIPY="Touchify_TransformTool_Free_FlipY"
            FREE_ROTATECW="Touchify_TransformTool_Free_RotateCW"
            FREE_ROTATECCW="Touchify_TransformTool_Free_RotateCCW"
            RESET="Touchify_TransformTool_Reset"
            APPLY="Touchify_TransformTool_Apply"

        class CropTools:
            MENU="Touchify_CropToolActions_Menu"
            CENTER="Touchify_CropToolActions_Center"
            GROW="Touchify_CropToolActions_Grow"
            LOCKWIDTH="Touchify_CropToolActions_LockWidth"
            LOCKHEIGHT="Touchify_CropToolActions_LockHeight"
            LOCKRATIO="Touchify_CropToolActions_LockRatio"

        class RegisteredActions:
            MENU="Touchify_RegisteredActions_Menu"
            PREFIX="touchify_registry_"
            
    class InternalPopups:
        BRUSH_PICKER="touchify_internal_brush_picker"
        GRADIENT_CHOOSER="gradient_chooser_popup"
        PATTERN_CHOOSER="pattern_chooser_popup"

    class Title:
        CORE_DOCKERS_PREFIX="Touchify Core:"
        ADDON_DOCKERS_PREFIX="Touchify Addon:"
        CLONE_DOCKERS_PREFIX="Touchify Clone:"
        REGISTERED_ACTIONS="Registered Actions"
    
    class DockerID:
        TOOLBOX="Touchify/TouchifyToolbox"
        TOOLSHELFDOCKER="Touchify/ToolshelfDocker"
        WIDGETPAD="Touchify/WidgetPad"
        SUB_VIEW="Touchify/SubView"
    
    class SettingsPath:
        TOOLSHELF="Touchify/Shelves"
        TOOLSHELF_NOPRESETDATA="Touchify/Shelves/NoPresetData"
        WIDGETPAD="Touchify/WidgetPads"
        TOOLBOX_NOPRESETDATA="Touchify/Toolbox/NoPresetData"
        TOUCHIFY="Touchify"
        SUB_VIEW="Touchify/SubView"