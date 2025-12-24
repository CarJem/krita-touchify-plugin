"""Data persistence and configuration management.

Handles loading/saving of grid data and common configuration files.
"""


from typing import TYPE_CHECKING
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from jemlib.api_touchify.env import TouchifyEnv
from jemlib.managers.KritaSettings import KritaSettings
from touchify_quick_actions.dataclasses.CommonConfig import CommonConfig

if TYPE_CHECKING:
    from touchify_quick_actions.dataclasses.GridConfig import GridConfig, GridInfo

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

def load_grids_data() -> tuple[list["GridInfo"], int]:
    """Load grids data from file, resolving preset names to objects."""
    from touchify_quick_actions.dataclasses.GridConfig import GridConfig
    grid_config: GridConfig = JsonExtensions.loadClass(KritaSettings.readSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "grid_config", ""), GridConfig)
    return grid_config.grids, len(grid_config.grids)

def save_grids_data(grids: list["GridInfo"]) -> bool:
    """Save grids data to file."""
    try:
        from touchify_quick_actions.dataclasses.GridConfig import GridConfig
        cfg = GridConfig()
        cfg.grids = grids
        json_str = JsonExtensions.saveClass(cfg.dump())
        KritaSettings.writeSetting(TouchifyEnv.SettingsPath.QUICK_ACTIONS, "grid_config", json_str, False)
        return True
    except Exception as e:
        print(f"Error writing Grid Config: {e}")
        return False
