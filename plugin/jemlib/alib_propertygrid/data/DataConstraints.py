from jemlib.alib_datatypes.EnumStr import EnumStr

class DataConstraints:

    class OtherMod(EnumStr):
        Expandable="expandable"
        OverrideType="global_override_type"

    class StrMod(EnumStr):
        Values="values"
        EnumStrValues="enumstr_values"
        ValuesWithIndex="indexed_values"
        Multiline="multiline_string"
        PythonEditor="python_editor"
        ColorPicker="color_picker"
        Placeholder="placeholder"
        
        ActionSelection="action_selection"
        DockerSelection="docker_selection"
        WorkspaceSelection="workspace"
        IconSelection="icon_selection"
        BrushSelection="brush_selection"
        ToolSelection="tool_selection"
        MultiToolSelection="multi_tool_selection"
        

        TouchifyRegistry="touchify_registry"

    class NumberMod(EnumStr):
        Range="range"

    class ListMod(EnumStr):
        Inmovable="inmovable"
        NestedTabs="nested_tabs"
        AddRemoveEditOnly="add_remove_edit_only"
        PropertyView="property_view"
        Subarray="sub_array"
        Locked="locked"
        Icons="icons"
        ItemModifier="item_mod"

    class DictMod(EnumStr):
        ListLike="list_like"

    def listSubArray(sub_id: str, sub_type: type):
        return { "type": DataConstraints.ListMod.Subarray, "sub_id": sub_id, "sub_type": sub_type }

    def listMod(type: ListMod, input: str = None):
        if input:
            return {"type": type, "param": input}
        else:
            return {"type": type}

    def dictMod(type: DictMod):
        return {"type": type}

    def expandable(text: str = None):
         if not text:
            return {"type": DataConstraints.OtherMod.Expandable}
         else:
             return {"type": DataConstraints.OtherMod.Expandable, "text": text}
         

    def strPlaceholder(text: str):
        return {"type":  DataConstraints.StrMod.Placeholder, "text": text}

    def strMod(type: StrMod):
        return {"type": type}
    
    def strValuesWithIndex(items: list):
        return {"type": DataConstraints.StrMod.ValuesWithIndex, "entries": items}

    def strValues(items: list):
        return {"type": DataConstraints.StrMod.Values, "entries": items}
    
    def strEnumValues(items: EnumStr):
        return {"type": DataConstraints.StrMod.EnumStrValues, "entries": items}
    
    @staticmethod
    def typeOverride(type: str):
        return {"type": DataConstraints.OtherMod.OverrideType, "value": type}
    
    def strSelectors():
        return [
            DataConstraints.StrMod.ActionSelection,
            DataConstraints.StrMod.DockerSelection,
            DataConstraints.StrMod.WorkspaceSelection,
            DataConstraints.StrMod.IconSelection,
            DataConstraints.StrMod.BrushSelection,
            DataConstraints.StrMod.MultiToolSelection,
            DataConstraints.StrMod.TouchifyRegistry
        ]

    def range(min: any = None, max: any = None):
        result = {"type": DataConstraints.NumberMod.Range}
        
        if min != None: result["min"] = min
        if max != None: result["max"] = max

        return result
