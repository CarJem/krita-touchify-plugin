from .CfgPopupInfo import CfgPopupInfo
from ..ext.extensions_json import JsonExtensions as Extensions
from ..ext.extensions import TypedList


class CfgPopup:
    id: str = ""
    btnName: str = ""
    popupType: str = "popup"
    icon: str = ""
    type: str = "actions"
    docker_id: str = ""
    opacity: float = 1.0
    grid_width: int = 3
    grid_padding: int = 2
    item_width: int = 100
    item_height: int = 100
    icon_width: int = 30
    icon_height: int = 30
    hotkeyNumber: int = 0
    items: TypedList[CfgPopupInfo] = []

    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["item_size"] = {"name": "Item Size", "items": ["item_width","item_height"]}
        row["icon_size"] = {"name": "Icon Size", "items": ["icon_width","icon_height"]}
        return row


    def propertygrid_groups(self):
        action_mode_settings = [
            "opacity",
            "grid_width",
            "grid_padding",
            "icon_width",
            "icon_height",
            "items",
        ]

        docker_mode_settings = [
            "docker_id"
        ]

        groups = {}
        groups["actions_mode"] = {"name": "Actions Mode Settings", "items": action_mode_settings}
        groups["docker_mode"] = {"name": "Docker Mode Settings", "items": docker_mode_settings}
        return groups

    def __init__(self, **args) -> None:
        Extensions.dictToObject(self, args)
        items = Extensions.default_assignment(args, "items", [])
        self.items = Extensions.list_assignment(items, CfgPopupInfo)

    def __str__(self):
        return self.btnName.replace("\n", "\\n")

    def forceLoad(self):
        self.items = TypedList(self.items, CfgPopupInfo)
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Popup ID (must be unique)"
        labels["btnName"] = "Display Name"
        labels["popupType"] = "Window Type"
        labels["icon"] = "Preview Icon"
        labels["type"] = "Popup Type"
        labels["docker_id"] = "Docker ID"
        labels["opacity"] = "Popup Opacity"
        labels["grid_width"] = "Action Grid Width"
        labels["grid_padding"] = "Action Grid Padding"
        labels["item_width"] = "Docker / Action Item Width"
        labels["item_height"] = "Docker / Action Item Height"
        labels["icon_width"] = "Action Icon Width"
        labels["icon_height"] = "Action Icon Height"
        labels["hotkeyNumber"] = "Activation Hotkey"
        labels["autoConceal"] = "Auto Conceal"
        labels["items"] = "Actions"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": ["actions", "docker"]}
        restrictions["popupType"] = {"type": "values", "entries": ["popup", "window"]}
        restrictions["opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        return restrictions