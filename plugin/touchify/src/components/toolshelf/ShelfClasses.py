from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from krita import *
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.managers.shared.settings import TouchifySettings

class NewContainerOptions:
    def __init__(self) -> None:
        self.container_type: str = "vertical"

    def propertygrid_hidden(self):
        return []

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["container_type"] = "Container Type"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["container_type"] = PropertyGrid_Restrictions.strValues(["vertical", "horizontal", "tab"])
        return restrictions    
    
class PresetSaveAs:
    def __init__(self) -> None:
        self.resource_pack: str = "0"
        self.display_name: str = ""

    def getKnownResourcePacks(self):
        results = []
        results.append("<unset>")
        for entry in TouchifySettings.resourcePacks():
            entry: ResourcePack
            results.append(entry.metadata.registry_name)

        return results

    def propertygrid_hidden(self):
        return []

    def forceLoad(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["resource_pack_destination"] = "Resource Pack"
        labels["display_name"] = "Display Name"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["resource_pack"] = PropertyGrid_Restrictions.strValuesWithIndex(self.getKnownResourcePacks())
        return restrictions    