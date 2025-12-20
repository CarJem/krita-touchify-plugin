from jemlib.alib_datatypes.EnumStr import EnumStr

from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints

class PropertyGrid_TouchifyRestrictions:

    class StrRegistryMod(EnumStr):
        DockerGroupRegistry="registry_docker_group_selection"
        PopupRegistry="registry_popup_selection"
        CanvasPresetRegistry="registry_canvas_preset_selection"
        MenuRegistry="registry_menu_selection"
        ScriptRegistry="registry_script_selection"
        PieWheelRegistry="registry_piewheel_selection"
        ToolshelfRegistry="registry_toolshelf_selection"
        ShelfRegistry="registry_shelf_selection"





    @staticmethod
    def strRegistryMod(type: StrRegistryMod):

        from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
        from touchify.src.config.docker_group.DockerGroup import DockerGroup
        from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
        from touchify.src.config.popup.PopupData import PopupData
        from touchify.src.config.menu.TriggerMenu import TriggerMenu
        from touchify.src.config.script.CustomScript import CustomScript
        from touchify.src.config.toolshelf.Toolshelf import Toolshelf
        from touchify.src.settings.TouchifySettings import TouchifySettings

        def strRegistryModType():
            if type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.PopupRegistry: return PopupData
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.DockerGroupRegistry: return DockerGroup
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.CanvasPresetRegistry: return CanvasPreset
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.MenuRegistry: return TriggerMenu
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.ShelfRegistry: return Toolshelf
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.ScriptRegistry: return CustomScript
            elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.PieWheelRegistry: return PieWheelData
            else: return None

        registryType = strRegistryModType()
        if not registryType: return {}
        return {"type": DataConstraints.StrMod.TouchifyRegistry, "entries": TouchifySettings.registry(registryType)}