from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui
import sys
import xml.etree.ElementTree as ET

from .PropertyGridExtensions import *
from .PropertyGrid import *

from ..extras.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard
from .PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from ...ext.typedlist import *
from ...resources import *
from ...ext.extensions import KritaExtensions
from ..CollapsibleBox import CollapsibleBox


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyField(QWidget):

    labelText: str
    variable_data: any

    def __init__(self, variable_name=str, variable_data=any, variable_source=any):
        super().__init__()
        self.setup(variable_name, variable_data, variable_source)
        self.testExpandability()

    def getFieldData(self):
         return [self.variable_name, self.variable_data, self.variable_source]
         
    def setup(self, variable_name=str, variable_data=any, variable_source=any):
        self.variable_name = variable_name
        self.variable_data = variable_data
        self.variable_source = variable_source

        self.labelText = self.variable_name
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)

    def setStackHost(self, host: PropertyGrid):
        self.stackHost = host

    #region Nestables

    def testExpandability(self):
        restric_func = PropertyGridExtensions.getVariable(self.variable_source, "propertygrid_restrictions")
        if callable(restric_func):
            restrictions = restric_func()
            if self.variable_name in restrictions:
                if restrictions[self.variable_name]["type"] == "expandable":
                    self.setupExpandable()

    def setupExpandable(self):
        self.editor = QPushButton()
        self.editor.clicked.connect(self.nested_edit)
        self.editor.setText("Edit...")
        
        editorLayout = QHBoxLayout()
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def nested_edit(self):
        self.nested_dlg = QDialog(self)
        self.nested_dlg.setWindowFlags(Qt.WindowType.Widget)
        self.nested_container = QVBoxLayout()
        self.nested_dlg.btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.nested_dlg.btns.accepted.connect(lambda: self.nested_dlg_accept())
        self.nested_dlg.btns.rejected.connect(lambda: self.nested_dlg_reject())

        from .PropertyGridPanel import PropertyGridPanel
        self.nested_subwindowPropGrid = PropertyGridPanel(self.stackHost)
        self.nested_container.addWidget(self.nested_subwindowPropGrid)
        self.nested_container.addWidget(self.nested_dlg.btns)
        self.nested_dlg.setLayout(self.nested_container)

        self.nested_subwindowPropGrid.updateDataObject(self.variable_data)
        self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.nested_dlg))
        self.nested_dlg.show()

    def nested_dlg_accept(self):
        self.nested_dlg.accept()
        self.stackHost.goBack()
        self.nested_subwindowPropGrid.deleteLater()
    
    def nested_dlg_reject(self):
        self.nested_dlg.reject()
        self.stackHost.goBack()
        self.nested_subwindowPropGrid.deleteLater()

    #endregion
