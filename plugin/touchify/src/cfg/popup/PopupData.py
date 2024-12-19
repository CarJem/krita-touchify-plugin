from touchify.src.cfg.docker_group.DockerGroupItem import DockerGroupItem
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.cfg.BackwardsCompatibility import BackwardsCompatibility
from touchify.src.ext.types.StrEnum import StrEnum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup

class PopupData:

    class DockersTabType(StrEnum):
        Buttons = "buttons"
        Tabs = "tabs"

    class Variants(StrEnum):
        Actions = "actions"
        Docker = "docker"
        MultipleDockers = "multiple_dockers"
        Toolshelf = "toolshelf"

    class WindowType(StrEnum):
        Popup = "popup"
        Window = "window"

    class ClosingMethod(StrEnum):
        Default = "default"
        Deactivation = "deactivation"
        MouseLeave = "mouse_leave"

    class PopupPosition(StrEnum):
        Default = "default"
        Start = "start"
        Center = "center"
        End = "end"

    def __defaults__(self):
        self.id: str = "NewPopup"
        self.window_type: str = "popup"
        self.window_title: str = ""

        self.window_docking_allowed: bool = False
        self.window_remember_location: bool = False
        
        self.type: str = "actions"
        self.closing_method: str = "default"

        self.popup_position_x: str = "default"
        self.popup_position_y: str = "default"

        self.popup_width: int = 0
        self.popup_height: int = 0

        self.popup_min_width: int = 0
        self.popup_min_height: int = 0
        
        self.actions_item_width: int = 100
        self.actions_item_height: int = 100
        self.actions_icon_size: int = 30

        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items: TypedList[TriggerGroup] = []

        self.docker_id: str = ""

        self.dockers_list: TypedList[DockerGroupItem] = []
        self.dockers_tab_type: str = "tabs"
        
        
        
        self.toolshelf_id: str = ""

        self.json_version: int = 5




    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.PopupData(args)        
        Extensions.dictToObject(self, args, [])
        
        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items = Extensions.init_list(args, "actions_items", TriggerGroup)

        self.dockers_list = Extensions.init_list(args, "dockers_list", DockerGroupItem)

    def __str__(self):
        return self.window_title.replace("\n", "\\n")
    
    def getFileName(self):
        return FileExtensions.fileStringify(self.id)

    def forceLoad(self):
        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items = TypedList(self.actions_items, TriggerGroup)
        self.dockers_list = TypedList(self.dockers_list, DockerGroupItem)



    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        row["actions_item_size"] = {"items": ["actions_item_width","actions_item_height"]}
        row["popup_position"] = {"items": ["popup_position_x","popup_position_y"]}
        row["popup_min_size"] = {"items": ["popup_min_width","popup_min_height"]}
        row["popup_size"] = {"items": ["popup_width","popup_height"]}
        return row
     
    def propertygrid_sorted(self):
        common_settings = [
            "id",
            "window_title",
            "closing_method",
            "popup_position",
            "popup_size",
            "popup_min_size",
            "window_type"   
        ]

        window_type_settings = [
            "window_docking_allowed",
            "window_remember_location"
        ]

        popup_type_settings = [

        ]

        mode_settings = [
            "type"
        ]
        
        action_mode_settings = [
            "actions_items",
            "actions_item_size",
            "actions_icon_size"
        ]

        docker_mode_single_settings = [
            "docker_id"
        ]

        docker_mode_multiple_settings = [
            "dockers_list",
            "dockers_tab_type"
        ]

        docker_mode_settings = [

        ]

        toolshelf_mode_settings = [
            "toolshelf_id"
        ]


        return common_settings + \
                window_type_settings + \
                popup_type_settings + \
                mode_settings + \
                action_mode_settings + \
                docker_mode_settings + \
                docker_mode_single_settings + \
                docker_mode_multiple_settings + \
                toolshelf_mode_settings
    
    def propertygrid_hidden(self):
        result = []

        common_settings = [
            "id",
            "window_title",
            "closing_method",
            "popup_position",
            "popup_size",
            "popup_min_size",
            "window_type"   
        ]

        window_type_settings = [
            "window_docking_allowed",
            "window_remember_location"
        ]

        popup_type_settings = [

        ]

        mode_settings = [
            "type"
        ]
        
        action_mode_settings = [
            "actions_items",
            "actions_item_size",
            "actions_icon_size"
        ]

        docker_mode_single_settings = [
            "docker_id"
        ]

        docker_mode_multiple_settings = [
            "dockers_list",
            "dockers_tab_type"
        ]

        docker_mode_settings = [

        ]

        toolshelf_mode_settings = [
            "toolshelf_id"
        ]

        if self.window_type != PopupData.WindowType.Window:
            for item in window_type_settings:
                result.append(item)
        if self.window_type != PopupData.WindowType.Popup:
            for item in popup_type_settings:
                result.append(item)


        if self.type != PopupData.Variants.Docker:
            for item in docker_mode_single_settings:
                result.append(item)
        if self.type != PopupData.Variants.MultipleDockers:
            for item in docker_mode_multiple_settings:
                result.append(item)
        if self.type != PopupData.Variants.Docker and self.type != PopupData.Variants.MultipleDockers:
            for item in docker_mode_settings:
                result.append(item)
            

        if self.type != PopupData.Variants.Actions:
            for item in action_mode_settings:
                result.append(item)
        if self.type != PopupData.Variants.Toolshelf:
            for item in toolshelf_mode_settings:
                result.append(item)

        return result

    def propertygrid_labels(self):
        labels = {}
        labels["id"] = "Popup ID"
        labels["window_type"] = "Window Type"
        labels["window_docking_allowed"] = "Allow window docking"
        labels["window_remember_location"] = "Remember window location"
        labels["type"] = "Popup Type"
        labels["docker_id"] = "Docker ID"
        labels["dockers_list"] = "Dockers"
        labels["popup_size"] = "Base Size"
        labels["popup_min_size"] = "Minimum Size"
        labels["actions_item_size"] = "Item Size"
        labels["actions_icon_size"] = "Icon Size"
        labels["actions_items"] = "Actions"
        labels["toolshelf_id"] = "Toolshelf ID"
        labels["window_title"] = "Window Title"
        labels["closing_method"] = "Closing Method"
        labels["popup_position"] = "Popup Position"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["docker_id"] = {"type": "docker_selection"}
        restrictions["type"] = {"type": "values", "entries": self.Variants.values()}
        restrictions["window_type"] = {"type": "values", "entries": self.WindowType.values()}
        restrictions["popup_position_x"] = {"type": "values", "entries": self.PopupPosition.values()}
        restrictions["popup_position_y"] = {"type": "values", "entries": self.PopupPosition.values()}
        restrictions["closing_method"] = {"type": "values", "entries": self.ClosingMethod.values()}
        restrictions["dockers_tab_type"] = {"type": "values", "entries": self.DockersTabType.values()}
        restrictions["toolshelf_id"] = {"type": "registry_toolshelf_selection"}

        restrictions["actions_item_height"] = {"type": "range", "min": 0}
        restrictions["actions_item_width"] = {"type": "range", "min": 0}
        restrictions["popup_width"] = {"type": "range", "min": 0}
        restrictions["popup_height"] = {"type": "range", "min": 0}

        return restrictions