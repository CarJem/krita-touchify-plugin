"""Configuration utilities for accessing common settings.

Provides cached access to configuration values with lazy loading.
"""


from typing import TYPE_CHECKING
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings
from touchify_quick_actions.dataclasses.CommonConfig import CommonConfig


if TYPE_CHECKING:
    from touchify_quick_actions.dataclasses.GridInfo import GridInfo

# Module-level cache for configuration
_config_cache = None


def get_common_config() -> CommonConfig:
    """Get common configuration, cached for performance."""
    global _config_cache
    if _config_cache is None:
        _config_cache = load_common_config()
    return _config_cache

def reload_common_config() -> CommonConfig:
    """Clear cache and reload configuration from disk."""
    global _config_cache
    _config_cache = None
    return get_common_config()

def load_common_config() -> CommonConfig:
    """Load common configuration, falling back to defaults."""
    return JsonExtensions.loadClass(KritaSettings.readSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "common_config", ""), CommonConfig)

def save_common_config(config: CommonConfig) -> bool:
    """Save common configuration to file."""
    try:
        json_str = JsonExtensions.saveClass(config)
        KritaSettings.writeSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "common_config", json_str, False)
        return True
    except Exception as e:
        print(f"Error writing Common Config: {e}")
        return False

def get_spacing_between_buttons(grid_info: "GridInfo" = None) -> int:
    """Get spacing between buttons from config."""
    if not grid_info.layout.override_global_style:
        return get_common_config().layout.spacing_between_buttons
    return grid_info.layout.spacing_between_buttons

def get_spacing_between_grids() -> int:
    """Get spacing between grids from config."""
    return get_common_config().layout.spacing_between_grids

def get_brush_icon_size(grid_info: "GridInfo" = None) -> int:
    """Get brush icon size from config."""
    if not grid_info.layout.override_global_style:
        return get_common_config().layout.brush_icon_size
    return grid_info.layout.brush_icon_size

def get_display_brush_names(grid_info: "GridInfo" = None) -> bool:
    """Get whether brush names should be displayed below icons."""
    if not grid_info.layout.override_global_style:
        return get_common_config().layout.display_brush_names
    return grid_info.layout.display_brush_names

def get_choose_left_key() -> str:
    """Get the keyboard shortcut for choosing left brush in grid."""
    return get_common_config().shortcut.choose_left_in_grid

def get_choose_right_key() -> str:
    """Get the keyboard shortcut for choosing right brush in grid."""
    return get_common_config().shortcut.choose_right_in_grid

def get_wrap_around_navigation() -> bool:
    """Get whether wrap-around navigation is enabled."""
    return get_common_config().shortcut.wrap_around_navigation

def get_exclusive_uncollapse() -> bool:
    """Get whether exclusive uncollapse mode is enabled.
    
    When enabled, only one group can be uncollapsed at a time.
    The uncollapsed group becomes the active_grid.
    """
    return get_common_config().layout.exclusive_uncollapse

def get_font_px(font_size_str: str) -> int:
    """Convert font size string (e.g., '12px') to integer pixels."""
    try:
        return int(str(font_size_str).replace("px", ""))
    except (ValueError, TypeError):
        return 12

def get_list_mode(grid_info: "GridInfo") -> bool:
    if not grid_info.layout.override_global_style:
        return get_common_config().layout.list_mode
    return grid_info.layout.list_mode

def get_list_column_count(grid_info: "GridInfo") -> int:
    if not grid_info.layout.override_global_style:
        return get_common_config().layout.list_column_count
    return grid_info.layout.list_column_count

def get_brush_name_font_size(grid_info: "GridInfo" = None) -> int:
    """Calculate font size for brush names based on icon size.
    
    Scales proportionally with brush_icon_size slider, clamped between
    min and max thresholds for readability.
    """
    icon_size = get_brush_icon_size(grid_info)

    if get_list_mode(grid_info):
        _BRUSH_NAME_MIN_FONT_SIZE = 10
        _BRUSH_NAME_MAX_FONT_SIZE = 15
        _BRUSH_NAME_BASE_FONT_SIZE = 12
        _BRUSH_NAME_REFERENCE_ICON_SIZE = 65
    else:
        _BRUSH_NAME_MIN_FONT_SIZE = 7
        _BRUSH_NAME_MAX_FONT_SIZE = 12
        _BRUSH_NAME_BASE_FONT_SIZE = 9
        _BRUSH_NAME_REFERENCE_ICON_SIZE = 65

    # Scale proportionally from reference size
    scale_factor = icon_size / _BRUSH_NAME_REFERENCE_ICON_SIZE
    calculated_size = int(_BRUSH_NAME_BASE_FONT_SIZE * scale_factor)
    # Clamp between min and max
    return max(_BRUSH_NAME_MIN_FONT_SIZE, min(_BRUSH_NAME_MAX_FONT_SIZE, calculated_size))

def get_brush_name_label_height(lines: int = 1, grid_info: "GridInfo" = None) -> int:
    """Calculate height for brush name label based on number of lines.
    
    Args:
        lines: Number of text lines (1 or 2)
    
    Returns:
        Height in pixels for the name label area
    """
    font_size = get_brush_name_font_size(grid_info)
    line_height = int(font_size * 1.3)  # Line height multiplier
    padding = 4  # Top + bottom padding
    return (line_height * lines) + padding
