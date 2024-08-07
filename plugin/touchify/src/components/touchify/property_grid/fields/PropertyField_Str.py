from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .....features.touchify_hotkeys import TouchifyHotkeys
from ....extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from .....ext.TypedList import *
from .....resources import *
from .....ext.extensions_krita import KritaExtensions
from ....CollapsibleBox import CollapsibleBox

from ..utils.PropertyUtils_Extensions import *
from ..PropertyGrid import *
from ..dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from .PropertyField import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyField_Str(PropertyField):
    def __init__(self, variable_name=str, variable_data=str, variable_source=any):
        super(PropertyField, self).__init__()
        self.setup(variable_name, variable_data, variable_source)


        self.is_icon_viewer = False
        self.is_docker_selector = False
        self.is_action_selection = False
        self.is_hotkey_selector = False
        self.is_brush_selection = False
        self.is_combobox = False
        self.combobox_items: list[tuple[str, str]] = []
        
        self.editorHelper: QPushButton | None = None

        restrictions = PropertyUtils_Extensions.getRestrictions(self.variable_source)
        if variable_name in restrictions:
            if restrictions[variable_name]["type"] == "values":
                combobox_items =  list[tuple[str, str]]()
                avaliableItems = list[str](restrictions[variable_name]["entries"])
                for item in avaliableItems:
                    input = (item, item)
                    combobox_items.append(input)                         
                self.combobox_items = combobox_items
                self.is_combobox = True
            elif restrictions[variable_name]["type"] == "action_selection":
                self.is_action_selection = True
            elif restrictions[variable_name]["type"] == "docker_selection":
                self.is_docker_selector = True
            elif restrictions[variable_name]["type"] == "icon_selection":
                self.is_icon_viewer = True
            elif restrictions[variable_name]["type"] == "brush_selection":
                self.is_brush_selection = True
            elif restrictions[variable_name]["type"] == "hotkey_selection":
                combobox_items = list[tuple[str, str]]()
                avaliableItems = TouchifyConfig.instance().hotkey_options_storage
                combobox_items.append(("None", "none"))
                for item in avaliableItems:
                    input = (avaliableItems[item]["displayName"], item)
                    combobox_items.append(input)
                self.combobox_items = combobox_items
                self.is_combobox = True
                

        if self.is_icon_viewer or self.is_docker_selector or self.is_action_selection or self.is_brush_selection:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            self.editorHelper = QPushButton()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(self.variable_data.replace("\n", "\\n")))
            elif self.is_brush_selection: 
                self.editorHelper.setIcon(ResourceManager.brushIcon(self.variable_data.replace("\n", "\\n")))
            else:
                self.editorHelper.setIcon(ResourceManager.iconLoader("properties"))


            editorHelperType = "none"
            if self.is_icon_viewer: editorHelperType = "icons"
            elif self.is_docker_selector: editorHelperType = "dockers"
            elif self.is_action_selection: editorHelperType = "actions"
            elif self.is_brush_selection: editorHelperType = "brushes"

            self.editorHelper.clicked.connect(lambda: self.helperRequested(editorHelperType))

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            editorLayout.addWidget(self.editorHelper)
            self.setLayout(editorLayout)
            self.setLayout(editorLayout)
        elif self.is_combobox:
            self.editor = QComboBox()
            self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
            for item in self.combobox_items:
                self.editor.insertItem(0, item[0])
                self.editor.setItemData(0, item[1], 1)
            index = self.editor.findData(self.variable_data, 1, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.editor.setCurrentIndex(index)
            self.editor.currentIndexChanged.connect(self.currentIndexChanged)

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)
        else:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            editorLayout = QHBoxLayout()
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)


    def dlg_accept(self):
        self.stackHost.goBack()
        self.dlg.accept()
    
    def dlg_reject(self):
        self.stackHost.goBack()
        self.dlg.reject()

    def helperRequested(self, mode):
        self.dlg = PropertyGrid_SelectorDialog(self.stackHost)
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(lambda: self.dlg_accept())
        self.btns.rejected.connect(lambda: self.dlg_reject())
        self.dlg.dlgLayout.addWidget(self.btns)

        self.dlg.load_list(mode)
        self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.dlg))
        if self.dlg.exec_():
            result = self.dlg.selectedResult()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(result))
            elif self.is_brush_selection:
                self.editorHelper.setIcon(ResourceManager.brushIcon(result))
            self.editor.setText(result)
            

    def currentIndexChanged(self):
        self.variable_data = str(self.editor.currentData(1)).replace("\\n", "\n")
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)

    def textChanged(self):
        self.variable_data = self.editor.text().replace("\\n", "\n")
        
        if self.editorHelper:
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(self.variable_data.replace("\n", "\\n")))
            elif self.is_brush_selection: 
                self.editorHelper.setIcon(ResourceManager.brushIcon(self.variable_data.replace("\n", "\\n")))
        
        super().setVariable(self.variable_source, self.variable_name, self.variable_data)
