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


class PropertyField(QWidget):

    propertyChanged = pyqtSignal(bool)

    def __init__(self, variable_name=str, variable_data=any, variable_source=any, is_typed: bool = False):
        super().__init__(parent=None)
        self.is_typed = is_typed
        self.setup(variable_name, variable_data, variable_source)
        self.common_setup()
        
        if not self.is_typed: self.test_restrictions()
         
    def setup(self, variable_name=str, variable_data=any, variable_source=any):
        self.variable_name = variable_name
        self.variable_data = variable_data
        self.variable_source = variable_source
        self.sister_id = None

    def setStackHost(self, host: PropertyGrid):
        self.stack_host = host

    def setVariable(self, source, name, data):
        PropertyUtils_Extensions.setVariable(source, name, data)
        self.propertyChanged.emit(True)

    #region Commons / Nestables

    def common_setup(self):   
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def test_restrictions(self):
        restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source, self.variable_name)
        setup_expandable = False

        for restriction in restrictions:
            if restriction["type"] == "expandable" and setup_expandable == False:
                self.nested_setup(restriction)
                setup_expandable = True

    def nested_setup(self, variableData: dict[str, any]):
        btnText = "Edit..."

        if "text" in variableData:
            btnText = variableData["text"]

        self.editor = QPushButton(self)
        self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.editor.clicked.connect(self.nested_edit)
        self.editor.setText(btnText)
        print(self.editor)

        self.editor_button = QPushButton(self)
        self.editor_button.setMaximumWidth(16)
        self.editor_button.setContentsMargins(0,0,0,0)
        self.editor_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        print(self.editor_button)

        moreMenu = QMenu(self.editor_button)
        copyAct = moreMenu.addAction("Copy")
        copyAct.triggered.connect(self.nested_copy)
        pateAct = moreMenu.addAction("Paste")
        pateAct.triggered.connect(self.nested_paste)
        self.editor_button.setMenu(moreMenu)
        
        self.editorLayout = QHBoxLayout(self)
        self.editorLayout.setSpacing(0)
        self.editorLayout.setContentsMargins(0,0,0,0)
        self.editorLayout.addWidget(self.editor, 1)
        self.editorLayout.addWidget(self.editor_button)
        self.setLayout(self.editorLayout)

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
        self.nested_page_dialog = PropertyGrid_Dialog(self)
        self.nested_page_dialog.setWindowTitle(str(self.variable_name))
        self.nested_page_dialog.setWindowFlags(Qt.WindowType.Widget)
        self.nested_page_layout = QVBoxLayout(self)
        self.nested_page_layout.setContentsMargins(0,0,0,0)
        self.nested_page_layout.setSpacing(0)

        from ..PropertyPage import PropertyPage
        self.nested_page_properties = PropertyPage(self.stack_host)
        self.nested_page_layout.addWidget(self.nested_page_properties)
        self.nested_page_dialog.setLayout(self.nested_page_layout)

        self.nested_page_properties.updateDataObject(self.variable_data)
        self.stack_host.setCurrentIndex(self.stack_host.addWidget(self.nested_page_dialog))
        self.nested_page_dialog.show()

    #endregion
