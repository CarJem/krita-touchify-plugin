from copy import deepcopy
from typing import TYPE_CHECKING
from jemlib.alib_datatypes.EnumStr import EnumStr


from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints


if TYPE_CHECKING:
    from jemlib.alib_propertygrid.fields.PropertyField_Str import PropertyField_Str

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

    class StrListModParams(EnumStr):
        IsRegistry="IsRegistry"

    @staticmethod
    def registryListMod():
        return DataConstraints.listMod(DataConstraints.ListMod.ItemModifier, PropertyGrid_TouchifyRestrictions.StrListModParams.IsRegistry)

    @staticmethod
    def registryReferenceEditor(src: "PropertyField_Str", registryType: str, current_data: str):

        from touchify.src.settings.TouchifySettings import TouchifySettings
        registryType = PropertyGrid_TouchifyRestrictions.strRegistryModType(registryType)
        if not registryType: return

        targetItem = TouchifySettings.registry(registryType).get(current_data)
        if not targetItem:
            return
        
        from jemlib.alib_propertygrid.dialogs.PropertyGrid_Subwindow import PropertyGrid_Subwindow
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QVBoxLayout

        src.nested_page_dialog = PropertyGrid_Subwindow(src)
        src.nested_page_dialog.setWindowTitle("Editor")
        src.nested_page_dialog.setWindowFlags(Qt.WindowType.Widget)
        src.nested_page_layout = QVBoxLayout(src)
        src.nested_page_layout.setContentsMargins(0,0,0,0)
        src.nested_page_layout.setSpacing(0)

        from jemlib.alib_propertygrid.PropertyViewport import PropertyViewport
        src.nested_page_properties = PropertyViewport(src.getParentContainer(), src.praser)
        src.nested_page_layout.addWidget(src.nested_page_properties)
        src.nested_page_dialog.setLayout(src.nested_page_layout)

        src.nested_page_properties.setDataObject(deepcopy(targetItem))
        src.getParentContainer().navigateForwards(src.nested_page_dialog)
        src.nested_page_dialog.show()

    @staticmethod
    def strRegistryModType(type: StrRegistryMod):
        from touchify.src.config.canvas_preset.CanvasPreset import CanvasPreset
        from touchify.src.config.docker_group.DockerGroup import DockerGroup
        from touchify.src.config.pie_wheel.PieWheelData import PieWheelData
        from touchify.src.config.popup.PopupData import PopupData
        from touchify.src.config.context_menu.ContextMenu import ContextMenu
        from touchify.src.config.script.CustomScript import CustomScript
        from touchify.src.config.toolshelf.Toolshelf import Toolshelf

        if type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.PopupRegistry: return PopupData
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.DockerGroupRegistry: return DockerGroup
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.CanvasPresetRegistry: return CanvasPreset
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.MenuRegistry: return ContextMenu
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.ShelfRegistry: return Toolshelf
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.ScriptRegistry: return CustomScript
        elif type == PropertyGrid_TouchifyRestrictions.StrRegistryMod.PieWheelRegistry: return PieWheelData
        else: return None

    @staticmethod
    def strRegistryMod(type: StrRegistryMod):
        from touchify.src.settings.TouchifySettings import TouchifySettings
        registryType =PropertyGrid_TouchifyRestrictions.strRegistryModType(type)
        if not registryType: return {}
        return {"type": DataConstraints.StrMod.TouchifyRegistry, "entries": TouchifySettings.registry(registryType), "registry_type": type, "callback": PropertyGrid_TouchifyRestrictions.registryReferenceEditor }