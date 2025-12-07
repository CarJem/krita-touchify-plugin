import os;

#-----------------#
# Enviornment Variables
BASE_DIR = os.path.dirname(os.path.realpath(__file__)) 
REGISTERED_ACTIONS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/registered_actions.action"
RESOURCE_PACKS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
ASSETS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
#-----------------#
# Action IDs
TOUCHIFY_ACTIONID_CONFIGURE="touchify_configure"

TOUCHIFY_ACTIONID_STYLES_MENU="touchify_styles_menu"
TOUCHIFY_ACTIONID_STYLES_BORDERLESSTOOLBARS="touchify_toolbarBorder"
TOUCHIFY_ACTIONID_STYLES_PRIVACYMODE="Privacy Mode"
TOUCHIFY_ACTIONID_STYLES_TABHEIGHT="touchify_tabHeight"
TOUCHIFY_ACTIONID_STYLES_DOCKEDBRUSHEDITOR="touchify_styles_docked_brush_editor"
TOUCHIFY_ACTIONID_STYLES_DOCKEDBRUSHEDITORZOOMFIX="touchify_styles_brush_editor_zoom_fix"

TOUCHIFY_ACTIONID_WIDGETPAD_PRESETS_MENU = "touchify_canvas_options_menu"
TOUCHIFY_ACTIONID_WIDGETPAD_MENU = "touchify_canvas_layouts_menu"
TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLBOX="touchify_showToolbox"
TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_ALPHA="touchify_showToolshelf"
TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_BETA="touchify_showToolshelfAlt"
TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_GAMMA="touchify_canvas_showtoolshelf_gamma"
TOUCHIFY_ACTIONID_WIDGETPAD_SHOWTOOLSHELF_DELTA="touchify_canvas_showtoolshelf_delta"

TOUCHIFY_ACTIONID_DOCKERUTILS_MENU="touchify_dockerutils_menu"
TOUCHIFY_ACTIONID_DOCKERUTILS_TOGGLEDOWN="touchify_dockerutils_toggledown"
TOUCHIFY_ACTIONID_DOCKERUTILS_TOGGLEUP="touchify_dockerutils_toggleup"
TOUCHIFY_ACTIONID_DOCKERUTILS_TOGGLELEFT="touchify_dockerutils_toggleleft"
TOUCHIFY_ACTIONID_DOCKERUTILS_TOGGLERIGHT="touchify_dockerutils_toggleright"

TOUCHIFY_ACTIONID_OTHER_SHOWPOPUPPALETTE="touchify_showPopupPalette"
TOUCHIFY_ACTIONID_OTHER_SHOWMENUBARPOPUP="touchify_showPopupMenu"

TOUCHIFY_ACTIONID_TRANSFORMTOOL_MENU="Touchify_TransformTool_Menu"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_FREE_FLIPX="Touchify_TransformTool_Free_FlipX"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_FREE_FLIPY="Touchify_TransformTool_Free_FlipY"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_FREE_ROTATECW="Touchify_TransformTool_Free_RotateCW"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_FREE_ROTATECCW="Touchify_TransformTool_Free_RotateCCW"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_RESET="Touchify_TransformTool_Reset"
TOUCHIFY_ACTIONID_TRANSFORMTOOL_APPLY="Touchify_TransformTool_Apply"

TOUCHIFY_ACTIONID_CROPTOOLS_MENU="Touchify_CropToolActions_Menu"
TOUCHIFY_ACTIONID_CROPTOOLS_CENTER="Touchify_CropToolActions_Center"
TOUCHIFY_ACTIONID_CROPTOOLS_GROW="Touchify_CropToolActions_Grow"
TOUCHIFY_ACTIONID_CROPTOOLS_LOCKWIDTH="Touchify_CropToolActions_LockWidth"
TOUCHIFY_ACTIONID_CROPTOOLS_LOCKHEIGHT="Touchify_CropToolActions_LockHeight"
TOUCHIFY_ACTIONID_CROPTOOLS_LOCKRATIO="Touchify_CropToolActions_LockRatio"

TOUCHIFY_ACTIONID_REGISTERED_ACTIONS_MENU="Touchify_RegisteredActions_Menu"
TOUCHIFY_ACTIONID_REGISTERED_ACTION_PREFIX="touchify_registry_"
#-----------------#
# Docker IDs
TOUCHIFY_DOCKERID_TOOLSHELFDOCKER="Touchify/ToolshelfDocker"
TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT="Touchify/ToolshelfDocker_Ext"
TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT="Touchify/ToolshelfDocker_ExtFlt"
TOUCHIFY_DOCKERID_DOCKER_TOOLBOX="Touchify/TouchifyToolbox"
#-----------------#
# Setting Paths
TOUCHIFY_SETTINGPATH_TOOLSHELF="Touchify/Shelves"
TOUCHIFY_SETTINGPATH_TOOLSHELF_LEGACY="Touchify/Toolshelfs"
TOUCHIFY_SETTINGPATH_WIDGETPAD="Touchify/WidgetPads"
TOUCHIFY_SETTINGPATH_POPUPS_FIXED_LOCATIONS="Touchify/Popups/Fixed/Locations"
TOUCHIFY_SETTINGPATH_POPUPS_LAST_LOCATIONS="Touchify/Popups/Normal/Locations"