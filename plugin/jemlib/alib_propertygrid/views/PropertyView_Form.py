from PyQt5 import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget


from jemlib.alib_propertygrid.fields.PropertyLabel import PropertyLabel
from jemlib.alib_propertygrid.data.DataHandler import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import *
from jemlib.alib_propertygrid.PropertyGrid import PropertyGrid


from jemlib.alib_propertygrid.views.PropertyView import PropertyView
from jemlib.alib_datatypes.TypedList import *
from jemlib.alib_vaporjem.extensions.pyqt_extensions import CommonHelpers
from jemlib.managers.IconRepository import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Expanding
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from jemlib.alib_propertygrid.PropertyPage import PropertyPage



class PropertyView_Form(QWidget, PropertyView):

    def __init__(self, parent: "PropertyPage", praser: DataHandler):
        QWidget.__init__(self, parent)
        PropertyView.__init__(self, parent, praser)

        self.parent_page: "PropertyPage" = parent

        self.fields: list[PropertyField] = []
        self.labels: list[PropertyLabel] = []

        self.praser = praser

        self.setContentsMargins(0,0,0,0)

        self.gridLayout = QVBoxLayout(self)
        self.gridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.gridLayout)


    def setStackHost(self, host: PropertyGrid):
        for field in self.fields:
            field.setStackHost(host)
    
    def onPropertyChanged(self, value: bool):
        self.updateVisibility()

    def updateVisibility(self):
        if self.item == None:
            return
        
        hiddenItems = PropertyView.getHiddenVariableNames(self)

        for field in self.fields:     
            
            if field.propertyData.variableName() in hiddenItems or (field.sister_id != None and field.sister_id in hiddenItems): field.setHidden(True)
            else: field.setHidden(False)

        for label in self.labels:     
            if label.variable_name in hiddenItems: label.setHidden(True)
            else: label.setHidden(False)

    def createLabel(self, varName: str, labelData: dict, hintData: dict, is_nested: bool = False):
        labelText = self.praser.getPropertyLabel(labelData, varName)
        hintText = self.praser.getPropertyTextHint(hintData, varName)
        header = PropertyLabel(self, varName, labelText, hintText, is_nested)
        self.labels.append(header)
        return header
    
    def createField(self, source: any, _varName: str):
        variable = self.praser.getPropertyVariable(source, _varName)
        field = self.praser.getPropertyField(variable)
        if field:
            field.setParent(self)
            field.propertyChanged.connect(self.parent_page.onPropertyChanged)
            field.setStackHost(self.parent_page.stackHost)
            field.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)
            self.fields.append(field)
            return field
        return None

    def createSisterField(self, source: any, sister_id: str, sister_data: dict[str, any], labelData: dict, hintData: dict):
        sister_items = list[str](sister_data["items"])

        use_labels: bool = False
        if "use_labels" in sister_data:
            use_labels = bool(sister_data["use_labels"])

        flip_labels: bool = False
        if "flip_labels" in sister_data:
            flip_labels = bool(sister_data["flip_labels"])
        

        sister_field = QWidget(self)
        sister_field.setContentsMargins(0,0,0,0)
        
        if use_labels:
            layout = QFormLayout(sister_field)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)
        else:
            layout = QHBoxLayout(sister_field)
            layout.setContentsMargins(0,0,0,0)
            layout.setSpacing(0)

        for index, variable_name in enumerate(sister_items):
            field = self.createField(source, variable_name)
            field.sister_id = sister_id

            if use_labels:
                header = self.createLabel(variable_name, labelData, hintData, True)
                if flip_labels:
                    header.setMaximumWidth(250)
                    layout.addRow(header, field)
                else:
                    field.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
                    layout.addRow(field, header)

                header.setStyleSheet("font-style: italic;")
                header.setContentsMargins(5,0,5,0)
            else:
                layout.addWidget(field, 1)

        return sister_field
    
    def unloadPropertyView(self):
        self.fields.clear()
        self.labels.clear()
        
        CommonHelpers.clearLayout(self.gridLayout)

    def updateDataObject(self, item):

        def createColumn(sectionLayout: QBoxLayout):
            formLayout = QFormLayout()
            formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            formLayout.setSpacing(0)
            formLayout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
            formLayout.setContentsMargins(2, 2, 2, 2)
            sectionLayout.addLayout(formLayout)
            return formLayout

        def createSection():
            sectionLayout = QHBoxLayout()
            sectionLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
            sectionLayout.setSpacing(0)
            sectionLayout.setContentsMargins(0,0,0,0)
            self.gridLayout.addLayout(sectionLayout)
            return sectionLayout
            


        PropertyView.updateDataObject(self, item)
        self.unloadPropertyView()

        if self.item == None:
            return

        labelData = self.praser.getObjectVariableLabels(item)
        hintData = self.praser.getObjectVariableTextHints(item)
        variable_data, known_sisters, sister_data = PropertyView.getClassVariablesWithSisters(self, item)

        no_labels = "no_labels" in self.parent_page.modifiers
        
        sectionLayout = createSection()
        formLayout = createColumn(sectionLayout)

        for variable_id in variable_data:    
            variable_id: str     
            field = None
            if variable_id.startswith("#"):
                if variable_id == "#NEW_SECTION":
                    sectionLayout = createSection()
                    formLayout = createColumn(sectionLayout)
                elif variable_id == "#NEW_COLUMN":
                    formLayout = createColumn(sectionLayout)
            elif variable_id in known_sisters:
                sister_info = sister_data[variable_id]

                is_group = False
                if "is_group" in sister_info:
                    is_group = bool(sister_info["is_group"])
                    
                if is_group == False:
                    field = self.createSisterField(item, variable_id, sister_info, labelData, hintData)
            else:
                field = self.createField(item, variable_id)

            if field == None: continue

            field.setContentsMargins(6,0,0,0)

            if no_labels:
                field.setContentsMargins(0,25,0,0)
                formLayout.addRow(field)
            else:
                label = self.createLabel(variable_id, labelData, hintData)
                label.setStyleSheet("font-weight: bold;")
                #label.setMaximumWidth(250)
                label.setContentsMargins(5,0,5,0)
                formLayout.addRow(label)
                formLayout.addRow(field)




        self.updateVisibility()

