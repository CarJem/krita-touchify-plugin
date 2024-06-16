from .CfgPopupInfo import PopupInfo
from ..ext.extensions import Extensions, TypedList


class Popup:
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
    items: TypedList[PopupInfo] = []


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
        groups["general"] = {"name": "General Settings", "items": ["id", "icon", "hotkeyNumber"]}
        groups["actions_mode"] = {"name": "Actions Mode Settings", "items": action_mode_settings}
        groups["docker_mode"] = {"name": "Docker Mode Settings", "items": docker_mode_settings}
        return groups

    def create(args):
        obj = Popup()
        Extensions.dictToObject(obj, args)
        items = Extensions.default_assignment(args, "items", [])
        obj.items = Extensions.list_assignment(items, PopupInfo)
        return obj

    def __str__(self):
        return self.btnName.replace("\n", "\\n")

    def forceLoad(self):
        self.items = TypedList(self.items, PopupInfo)
        pass

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon"] = {"type": "icon_selection"}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": ["actions", "docker"]}
        restrictions["popupType"] = {"type": "values", "entries": ["popup", "window", "toolbox"]}
        restrictions["opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        restrictions["hotkeyNumber"] = {"type": "range", "min": 0, "max": 10}
        return restrictions