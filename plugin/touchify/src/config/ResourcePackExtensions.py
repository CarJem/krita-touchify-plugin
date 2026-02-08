from typing import TYPE_CHECKING
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from krita import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from touchify.src.settings.TouchifySettings import TouchifySettings

if TYPE_CHECKING:
    from touchify.src.config.ResourcePack import ResourcePack

class ResourcePackExtensions:
    class PresetSaveAs:
        def __init__(self) -> None:
            self.resource_pack: str = "0"
            self.display_name: str = ""
            self.new_resourcepack_name: str = "New Resource Pack"

        def getKnownResourcePacks(self):
            results = []
            results.append("<unset>")
            results.append("<new>")
            for entry in TouchifySettings.resourcePacks():
                entry: "ResourcePack"
                results.append(entry.metadata.registry_name)

            return results
        
        def propertygrid_sorted(self):
            return [
                "display_name",
                "resource_pack",
                "new_resourcepack_name"
            ]


        def propertygrid_hidden(self):
            result = []
            if self.resource_pack != "1":
                result.append("new_resourcepack_name")
            return result

        def propertygrid_listload(self):
            pass

        def propertygrid_labels(self):
            labels = {}
            labels["resource_pack"] = "Resource Pack"
            labels["new_resourcepack_name"] = "Pack Name"
            labels["new_resourcepack_id"] = "Pack Id"
            labels["display_name"] = "Display Name"
            return labels

        def propertygrid_restrictions(self):
            restrictions = {}
            restrictions["resource_pack"] = DataConstraints.strValuesWithIndex(self.getKnownResourcePacks())
            return restrictions    