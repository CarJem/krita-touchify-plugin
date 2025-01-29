from touchify.src.datatypes.metaclass.EnumStr import EnumStr

class PropertyGrid_Restrictions:

    class OtherMod(EnumStr):
        Expandable="expandable"

    class StrMod(EnumStr):
        Values="values"
        Multiline="multiline_string"
        PythonEdtior="python_editor"
        
        ActionSelection="action_selection"
        DockerSelection="docker_selection"
        WorkspaceSelection="workspace"
        IconSelection="icon_selection"
        BrushSelection="brush_selection"

        DockerGroupRegistry="registry_docker_group_selection"
        PopupRegistry="registry_popup_selection"
        CanvasPresetRegistry="registry_canvas_preset_selection"
        MenuRegistry="registry_menu_selection"
        ScriptRegistry="registry_script_selection"
        PieWheelRegistry="registry_piewheel_selection"
        ToolshelfRegistry="registry_toolshelf_selection"

    class NumberMod(EnumStr):
        Range="range"

    class ListMod(EnumStr):
        Inmovable="inmovable"
        NestedTabs="nested_tabs"
        AddRemoveEditOnly="add_remove_edit_only"
        PropertyView="property_view"
        Subarray="sub_array"

    def listSubArray(sub_id: str, sub_type: type):
        return { "type": PropertyGrid_Restrictions.ListMod.Subarray, "sub_id": sub_id, "sub_type": sub_type }

    def listMod(type: ListMod):
        return {"type": type}

    def expandable():
         return {"type": PropertyGrid_Restrictions.OtherMod.Expandable}

    def strMod(type: StrMod):
        return {"type": type}

    def strValues(items: list):
        return {"type": PropertyGrid_Restrictions.StrMod.Values, "entries": items}
    
    def strSelectors():
        return [
            PropertyGrid_Restrictions.StrMod.ActionSelection,
            PropertyGrid_Restrictions.StrMod.DockerSelection,
            PropertyGrid_Restrictions.StrMod.WorkspaceSelection,
            PropertyGrid_Restrictions.StrMod.IconSelection,
            PropertyGrid_Restrictions.StrMod.BrushSelection,
            PropertyGrid_Restrictions.StrMod.DockerGroupRegistry,
            PropertyGrid_Restrictions.StrMod.PopupRegistry,
            PropertyGrid_Restrictions.StrMod.CanvasPresetRegistry,
            PropertyGrid_Restrictions.StrMod.MenuRegistry,
            PropertyGrid_Restrictions.StrMod.ScriptRegistry,
            PropertyGrid_Restrictions.StrMod.PieWheelRegistry,
            PropertyGrid_Restrictions.StrMod.ToolshelfRegistry
        ]

    def range(min: any = None, max: any = None):
        result = {"type": PropertyGrid_Restrictions.NumberMod.Range}
        
        if min != None: result["min"] = min
        if max != None: result["max"] = max

        return result
