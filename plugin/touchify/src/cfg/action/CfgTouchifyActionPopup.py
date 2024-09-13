from .CfgTouchifyActionPopupItem import CfgTouchifyActionPopupItem
from ...ext.extensions_json import JsonExtensions as Extensions
from ...ext.extensions import TypedList
from ..CfgBackwardsCompat import CfgBackwardsCompat


class CfgTouchifyActionPopup:
    id: str = ""
    display_name: str = ""
    window_type: str = "popup"
    icon: str = ""
    type: str = "actions"
    opacity: float = 1.0
    
    actions_grid_width: int = 3
    actions_grid_padding: int = 2
    actions_item_width: int = 100
    actions_item_height: int = 100
    actions_icon_width: int = 30
    actions_icon_height: int = 30
    actions_items: TypedList[CfgTouchifyActionPopupItem] = []
    
    docker_id: str = ""

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["item_size"] = {"name": "Item Size", "items": ["actions_item_width","actions_item_height"]}
        row["icon_size"] = {"name": "Icon Size", "items": ["actions_icon_width","actions_icon_height"]}
        return row
    
    def propertygrid_hidden(self):
        action_mode_settings = [
            "opacity",
            "actions_grid_width",
            "actions_grid_padding",
            "actions_icon_width",
            "actions_icon_height",
            "actions_items",
        ]

        docker_mode_settings = [
            "docker_id"
        ]

        result = []
        if self.type != "docker":
            for item in docker_mode_settings:
                result.append(item)
        if self.type != "actions":
            for item in action_mode_settings:
                result.append(item)

        return result

    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgTouchifyActionPopup(args)
        Extensions.dictToObject(self, args)
        items = Extensions.default_assignment(args, "actions_items", [])
        self.actions_items = Extensions.list_assignment(items, CfgTouchifyActionPopupItem)

    def __str__(self):
        return self.display_name.replace("\n", "\\n")

    def forceLoad(self):
        self.actions_items = TypedList(self.actions_items, CfgTouchifyActionPopupItem)
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Popup ID (must be unique)"
        labels["display_name"] = "Display Name"
        labels["window_type"] = "Window Type"
        labels["icon"] = "Preview Icon"
        labels["type"] = "Popup Type"
        labels["docker_id"] = "Docker ID"
        labels["opacity"] = "Popup Opacity"
        labels["actions_grid_width"] = "Action Grid Width"
        labels["actions_grid_padding"] = "Action Grid Padding"
        labels["actions_item_width"] = "Docker / Action Item Width"
        labels["actions_item_height"] = "Docker / Action Item Height"
        labels["actions_icon_width"] = "Action Icon Width"
        labels["actions_icon_height"] = "Action Icon Height"
        labels["actions_items"] = "Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": ["actions", "docker"]}
        restrictions["window_type"] = {"type": "values", "entries": ["popup", "window"]}
        restrictions["opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        return restrictions