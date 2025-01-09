from touchify.src.components.python.datatypes.StrEnum import StrEnum

class PropertyGrid_Restrictions:

    class StrMod(StrEnum):
        Actions="action_selection"
        Docker="docker_selection"
        Icon="icon_selection"
        Brush="brush_selection"
        DockerGroup="registry_docker_group_selection"
        Popup="registry_popup_selection"
        CanvasPreset="registry_canvas_preset_selection"
        Menu="registry_menu_selection"
        Script="registry_script_selection"
        Toolshelf="registry_toolshelf_selection"
        Workspace="workspace"

    class ListMod(StrEnum):
        Inmovable="inmovable"
        NestedTabs="nested_tabs"
        AddRemoveEditOnly="add_remove_edit_only"

    def listMod(type: ListMod):
        return {"type": type}

    def expandable():
         return {"type": "expandable"}

    def strMod(type: StrMod):
        return {"type": type}

    def values(items: list):
        return {"type": "values", "entries": items}

    def range(min: any = None, max: any = None):
        result = {"type": "range"}
        
        if min != None: result["min"] = min
        if max != None: result["max"] = max

        return result
