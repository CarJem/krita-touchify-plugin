from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from jemlib.api_touchify.env import *
from jemlib.api_touchify.config.popups.PopupData import PopupData
from touchify.src.settings.TouchifySettings import TouchifySettings
from krita import *

from typing import TYPE_CHECKING

from jemlib.api_touchify.config.toolshelf.ToolshelfData import ToolshelfData
from jemlib.api_touchify.config.toolshelf.ToolshelfArea import ToolshelfArea
from jemlib.api_touchify.config.toolshelf.ToolshelfDock import ToolshelfDock


if TYPE_CHECKING:
    from touchify_toolshelves.src.components.PopupWidget import PopupWidget

class PopupLoader(QObject):
    def __init__(self, parent: "PopupWidget"):
        super().__init__(parent)
        self.rootWidget = parent

    def Section_Actions(self, data: PopupData):
        toolshelf_data: ToolshelfArea = ToolshelfArea()


        action_section: ToolshelfDock = ToolshelfDock()
        action_section.section_type = ToolshelfDock.SectionType.Actions
        action_section.action_section_icon_size =  data.actions_icon_size
        action_section.action_section_display_mode = ToolshelfDock.ActionSectionDisplayMode.Detailed
        action_section.action_section_contents = data.actions_items
        action_section.action_section_btn_height = data.actions_item_height
        action_section.action_section_btn_width = data.actions_item_width
        action_section.min_size_x = data.popup_min_width
        action_section.min_size_y = data.popup_min_height
        action_section.docker_size_hint_x = data.popup_width
        action_section.docker_size_hint_y = data.popup_height

        toolshelf_data.items["action_list"] = action_section
        return toolshelf_data
    
    def Section_Dockers(self, data: PopupData):
        toolshelf_data: ToolshelfArea = ToolshelfArea()

        dockers = [ ]

        if data.type == PopupData.Variants.MultipleDockers:
            from jemlib.api_touchify.config.docker_groups.DockerItem import DockerItem
            for item in data.dockers_list:
                item: DockerItem
                dockers.append(item.id)
        else:
            dockers.append(data.docker_id)

        
        layout_array = []

        for docker_id in dockers:
            docker_section: ToolshelfDock = ToolshelfDock()
            docker_section.section_type = ToolshelfDock.SectionType.Docker
            docker_section.docker_nesting_mode = ToolshelfDock.DockerNestingMode.Docking
            docker_section.docker_unloaded_visibility = ToolshelfDock.DockerUnloadedVisibility.Hidden
            docker_section.docker_id = docker_id
            docker_section.docker_size_hint_x = data.popup_width
            docker_section.docker_size_hint_y = data.popup_height
            docker_section.min_size_x = data.popup_min_width
            docker_section.min_size_y = data.popup_min_height
            toolshelf_data.items[docker_id] = docker_section
            layout_array.append(["dock",docker_id,{}])

        if len(dockers) >= 2:
            toolshelf_data.layout = {
                "main": ["vertical",[["tab",layout_array,{"index": 0}],],{"sizes": [0]}],
                "float": []
            }

        return toolshelf_data
        
    def Section_Shelf(self, data: PopupData):
        toolshelf: ToolshelfData = TouchifySettings.registryItem(data.shelf_id, ToolshelfData)
        return toolshelf.preset_data

    def Init_Section(self, data: PopupData):
        match data.type:
            case PopupData.Variants.Actions:
                return self.Section_Actions(data)
            case PopupData.Variants.Docker | PopupData.Variants.MultipleDockers:
                return self.Section_Dockers(data)
            case PopupData.Variants.Shelf:
                return self.Section_Shelf(data)
            case _:
                return None
