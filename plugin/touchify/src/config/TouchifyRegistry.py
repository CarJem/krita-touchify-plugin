from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.__env__ import BASE_DIR
from touchify.src.config.resource_pack.ResourcePackRegistry import ResourcePackRegistry
from touchify.src.config.TouchifyRegistryPreferences import TouchifyRegistryPreferences
from jemlib.alib_propertygrid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
from touchify.__env__ import *



class TouchifyRegistry:

    def __init__(self):
        self.__base_dir__ = BASE_DIR            
        self.resources: ResourcePackRegistry = ResourcePackRegistry()
        self.preferences: TouchifyRegistryPreferences = TouchifyRegistryPreferences()
        self.load()

    def propertygrid_labels(self):
        labels = {}
        labels["resources"] = "Resource Packs"
        labels["preferences"] = "Preferences"
        return labels
    
    def propertygrid_view_type(self):
        return "tabs"
    
    def propertygrid_sorted(self):
        return [
            "resources",
            "preferences"
        ]
    
    def propertygrid_sisters(self):
        row: dict[str, list[str]] = {}
        return row
    
    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["resources"] = PropertyGrid_Restrictions.expandable()
        restrictions["preferences"] = PropertyGrid_Restrictions.expandable()
        return restrictions
    
    def save(self):
        self.resources.save()
        self.preferences.save()

    def load(self):
        self.resources.load()
        self.preferences.load()
        