from touchify.src.components.krita.settings import KS_Color
from touchify.src.components.python.file_extensions import FileExtensions
from touchify.src.components.python.json_extensions import JsonExtensions as Extensions
from touchify.src.components.python.datatypes.TypedList import TypedList

from typing import TYPE_CHECKING

from touchify.src.components.touchify.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
if TYPE_CHECKING:
    from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup

class PieWheelData:

    def __defaults__(self):
        self.registry_name: str = "New Pie Wheel"

        self.id: str = "NewPieWheel"
        self.icon_radius_scale: float = 1.5
        self.pie_radius_scale: float = 1.5
        self.background_color: KS_Color = KS_Color()
        self.active_color: KS_Color = KS_Color()
        self.pie_opacity: int = 75

        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items: TypedList[TriggerGroup] = []

        self.json_version: int = 1


    def __init__(self, **args) -> None:
        self.__defaults__()
        Extensions.dictToObject(self, args, [KS_Color])
        
        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items = Extensions.init_list(args, "actions_items", TriggerGroup)

    def __str__(self):
        return self.registry_name
    
    def getFileName(self):
        return FileExtensions.fileStringify(self.id)

    def forceLoad(self):
        from touchify.src.cfg.triggers.TriggerGroup import TriggerGroup
        self.actions_items = TypedList(self.actions_items, TriggerGroup)


    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row
     
    def propertygrid_sorted(self):
        return [
            "registry_name",
            "id",
            "icon_radius_scale",
            "pie_radius_scale",
            "background_color",
            "active_color",
            "pie_opacity",
            "actions_items",
        ]
    
    def propertygrid_hidden(self):
        result = []
        return result

    def propertygrid_labels(self):
        labels = {}
        labels["registry_name"] = "Display name"
        labels["id"] = "Pie Wheel ID"
        labels["actions_items"] = "Actions"
        labels["icon_radius_scale"] = "Icon Radius"
        labels["pie_radius_scale"] = "Pie Radius"
        labels["pie_opacity"] = "Pie Opacity"
        labels["background_color"] = "Background Color"
        labels["active_color"] = "Active Color"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["icon_radius_scale"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["pie_radius_scale"] = PropertyGrid_Restrictions.range(min=0)
        restrictions["pie_opacity"] = PropertyGrid_Restrictions.range(min=0, max=100)
        return restrictions