from touchify.src.cfg.action.CfgTouchifyActionPopupItem import CfgTouchifyActionPopupItem
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat
from touchify.src.ext.types.StrEnum import StrEnum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf

class CfgTouchifyActionPopup:

    class Variants(StrEnum):
        Actions = "actions"
        Docker = "docker"
        Toolshelf = "toolshelf"

    class WindowType(StrEnum):
        Popup = "popup"
        Window = "window"


    id: str = ""
    window_type: str = "popup"
    window_title: str = ""
    type: str = "actions"
    opacity: float = 1.0
    
    actions_grid_width: int = 3
    actions_grid_padding: int = 2
    actions_item_width: int = 100
    actions_item_height: int = 100
    actions_icon_width: int = 30
    actions_icon_height: int = 30
    actions_items: TypedList[CfgTouchifyActionPopupItem] = []
    actions_close_on_click: bool = False
    
    docker_id: str = ""
    docker_width: int = 0
    docker_height: int = 0

    json_version: int = 2


    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["action_item_size"] = {"name": "Item Size", "items": ["actions_item_width","actions_item_height"]}
        row["docker_item_size"] = {"name": "Docker Size", "items": ["docker_width","docker_height"]}
        row["action_icon_size"] = {"name": "Icon Size", "items": ["actions_icon_width","actions_icon_height"]}
        return row
    
    def propertygrid_hidden(self):
        action_mode_settings = [
            "opacity",
            "actions_grid_width",
            "actions_grid_padding",
            "actions_icon_width",
            "actions_icon_height",
            "actions_items",
            "actions_item_width",
            "actions_item_height",
            "actions_close_on_click",
            "action_item_size"
        ]

        docker_mode_settings = [
            "docker_id",
            "docker_width",
            "docker_height",
            "docker_item_size"
        ]

        toolshelf_mode_settings = [
            "toolshelf_data"
        ]

        result = []
        if self.type != CfgTouchifyActionPopup.Variants.Docker:
            for item in docker_mode_settings:
                result.append(item)
        if self.type != CfgTouchifyActionPopup.Variants.Actions:
            for item in action_mode_settings:
                result.append(item)
        if self.type != CfgTouchifyActionPopup.Variants.Toolshelf:
            for item in toolshelf_mode_settings:
                result.append(item)

        return result

    def __init__(self, **args) -> None:
        from touchify.src.cfg.toolshelf.CfgToolshelf import CfgToolshelf
        self.toolshelf_data: CfgToolshelf = CfgToolshelf()
        args = CfgBackwardsCompat.CfgTouchifyActionPopup(args)        
        Extensions.dictToObject(self, args, [CfgToolshelf])
        items = Extensions.default_assignment(args, "actions_items", [])
        self.actions_items = Extensions.list_assignment(items, CfgTouchifyActionPopupItem)

    def __str__(self):
        return self.id.replace("\n", "\\n")

    def forceLoad(self):
        self.actions_items = TypedList(self.actions_items, CfgTouchifyActionPopupItem)
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Popup ID"
        labels["window_type"] = "Window Type"
        labels["type"] = "Popup Type"
        labels["docker_id"] = "Docker ID"
        labels["opacity"] = "Popup Opacity"
        labels["actions_grid_width"] = "Action Grid Width"
        labels["actions_grid_padding"] = "Action Grid Padding"
        labels["docker_width"] = "Docker Width"
        labels["docker_height"] = "Docker Height"
        labels["actions_item_width"] = "Action Item Width"
        labels["actions_item_height"] = "Action Item Height"
        labels["actions_icon_width"] = "Action Icon Width"
        labels["actions_icon_height"] = "Action Icon Height"
        labels["actions_items"] = "Actions"
        labels["actions_close_on_click"] = "Close on Click"
        labels["toolshelf_data"] = "Toolshelf Data"
        labels["window_title"] = "Window Title"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": self.Variants.values()}
        restrictions["window_type"] = {"type": "values", "entries": self.WindowType.values()}
        restrictions["opacity"] = {"type": "range", "min": 0.0, "max": 1.0}
        restrictions["toolshelf_data"] = {"type": "expandable"}
        return restrictions