from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET
from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions import KritaExtensions
from ..CollapsibleBox import CollapsibleBox

from .PropertyGridExtensions import *
from .PropertyGridHost import *
from .IconSelector import IconSelector
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
        self.is_combobox = False
        self.combobox_items = []

        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
        if callable(restric_func):
            restrictions = restric_func()
            if variable_name in restrictions:
                if restrictions[variable_name]["type"] == "values":
                    self.combobox_items = restrictions[variable_name]["entries"]
                    self.is_combobox = True
                elif restrictions[variable_name]["type"] == "action_selection":
                    self.is_action_selection = True
                elif restrictions[variable_name]["type"] == "docker_selection":
                    self.is_docker_selector = True
                elif restrictions[variable_name]["type"] == "icon_selection":
                    self.is_icon_viewer = True
                    

        if self.is_icon_viewer or self.is_docker_selector or self.is_action_selection:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            self.editorHelper = QPushButton()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(ResourceManager.iconLoader(self.variable_data.replace("\n", "\\n")))
            else:
                self.editorHelper.setIcon(ResourceManager.iconLoader("properties"))


            editorHelperType = "none"
            if self.is_icon_viewer: editorHelperType = "icons"
            elif self.is_docker_selector: editorHelperType = "dockers"
            elif self.is_action_selection: editorHelperType = "actions"

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
            self.editor.insertItems(0, self.combobox_items)
            index = self.editor.findText(self.variable_data, Qt.MatchFlag.MatchFixedString)
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
        self.dlg = IconSelector(self.stackHost)
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
            self.editor.setText(result)

    def currentIndexChanged(self):
        self.variable_data = str(self.editor.currentText()).replace("\\n", "\n")
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)

    def textChanged(self):
        self.variable_data = self.editor.text().replace("\\n", "\n")
        PropertyGridExtensions.setVariable(self.variable_source, self.variable_name, self.variable_data)
