
from typing import Any
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from touchify.src.api_krita.wrappers.window import WindowAPI
from touchify.src.components.property_grid.PropertyGrid import PropertyGrid
import copy

from krita import *
from touchify.src.components.property_grid.utils.PropertyGrid_Restrictions import PropertyGrid_Restrictions
from touchify.src.config.resource_pack.ResourcePack import ResourcePack
from touchify.src.managers.shared.settings import TouchifySettings

class ShelfOptionsDialog(QDialog):

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

    def __init__(self, qwin: WindowAPI, options: Any):
        super().__init__(qwin.qwindow.window())
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.qwin = qwin.qwindow
        
        self.editableConfig = copy.deepcopy(options)
        self.propertyGrid = PropertyGrid(self)
        self.propertyGrid.updateDataObject(self.editableConfig)

        self.container = QVBoxLayout(self)
        self.setMinimumSize(600,400)
        self.setBaseSize(800,800)

        self.btns = QDialogButtonBox(self)
        self.btns.addButton(QDialogButtonBox.StandardButton.Save).clicked.connect(self.onSave)
        self.btns.addButton(QDialogButtonBox.StandardButton.Close).clicked.connect(self.onClose)

        self.container.addWidget(self.propertyGrid)
        self.container.addWidget(self.btns)
        self.setLayout(self.container)     

    def onSave(self):
        self.accept()

    def onClose(self):
        self.reject()

