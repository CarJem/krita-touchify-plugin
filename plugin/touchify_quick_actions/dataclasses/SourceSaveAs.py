from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from krita import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.settings.TouchifySettings import TouchifySettings

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

    def propertygrid_listload(self):
        pass

    def propertygrid_labels(self):
        labels = {}
        labels["resource_pack_destination"] = "Resource Pack"
        labels["display_name"] = "Display Name"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["resource_pack"] = DataConstraints.strValuesWithIndex(self.getKnownResourcePacks())
        return restrictions    