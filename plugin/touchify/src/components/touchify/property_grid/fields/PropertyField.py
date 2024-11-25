import copy
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *

from touchify.src.ext.types.TypedList import *
from touchify.src.helpers import TouchifyHelpers
from touchify.src.resources import *


ROW_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
ROW_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum

GROUP_SIZE_POLICY_X = QSizePolicy.Policy.Ignored
GROUP_SIZE_POLICY_Y = QSizePolicy.Policy.Minimum


class PropertyField(QWidget):

    propertyChanged = pyqtSignal(bool)

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

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(ROW_SIZE_POLICY_X, ROW_SIZE_POLICY_Y)

    def setStackHost(self, host: PropertyGrid):
        self.stackHost = host

    def setVariable(self, source, name, data):
        self.propertyChanged.emit(True)
        PropertyUtils_Extensions.setVariable(source, name, data)

    #region Nestables

    def testExpandability(self):
        restrictions = PropertyUtils_Extensions.getRestrictions(self.variable_source)
        if self.variable_name in restrictions:
            if restrictions[self.variable_name]["type"] == "expandable":
                self.setupExpandable(restrictions[self.variable_name])

    def setupExpandable(self, variableData: dict[str, any]):
        self.editor = QToolButton()
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        btnText = "Edit..."

        if "text" in variableData:
            btnText = variableData["text"]

        self.editor.clicked.connect(self.nested_edit)
        self.editor.setText(btnText)

        moreMenu = QMenu(self.editor)
        copyAct = moreMenu.addAction("Copy")
        copyAct.triggered.connect(self.nested_copy)
        pateAct = moreMenu.addAction("Paste")
        pateAct.triggered.connect(self.nested_paste)
        self.editor.menu
        self.editor.setMenu(moreMenu)
        
        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def nested_paste(self):
        item_type: type | None = type(self.variable_data)
        
        clipboard_data = TouchifyHelpers.getExtension().getSettingsClipboard(item_type)
        if clipboard_data != None:
            pastable_data = copy.deepcopy(clipboard_data)
            self.variable_data = pastable_data
            self.setVariable(self.variable_source, self.variable_name, pastable_data)

    def nested_copy(self):
        item_type: type | None = type(self.variable_data)
        item_data: any | None = copy.deepcopy(self.variable_data)

        if item_data != None and item_type != None:
            TouchifyHelpers.getExtension().setSettingsClipboard(item_type, item_data)

    def nested_edit(self):
        self.nested_dlg = PropertyGrid_Dialog(self)
        self.nested_dlg.setWindowTitle(str(self.variable_name))
        self.nested_dlg.setWindowFlags(Qt.WindowType.Widget)
        self.nested_container = QVBoxLayout(self)
        self.nested_container.setContentsMargins(0,0,0,0)
        self.nested_container.setSpacing(0)

        from ..PropertyGrid_Panel import PropertyGrid_Panel
        self.nested_subwindowPropGrid = PropertyGrid_Panel(self.stackHost)
        self.nested_container.addWidget(self.nested_subwindowPropGrid)
        self.nested_dlg.setLayout(self.nested_container)

        self.nested_subwindowPropGrid.updateDataObject(self.variable_data)
        self.stackHost.setCurrentIndex(self.stackHost.addWidget(self.nested_dlg))
        self.nested_dlg.show()

    #endregion
