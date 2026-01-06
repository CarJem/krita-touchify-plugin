from typing import Generic, TypeVar
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_propertygrid.PropertySystem import PropertySystem
from jemlib.alib_propertygrid.data.DataPath import DataPath
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Subwindow import PropertyGrid_Subwindow

from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.PropertyGrid import *

from jemlib.alib_datatypes.TypedList import *
from jemlib.managers.IconRepository import *

T = TypeVar("T")

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler

class PropertyField(QWidget, Generic[T]):

    sigPropertyFieldChanged = pyqtSignal()

    def __init__(self, praser: "DataHandler", property: DataPath[T], is_typed: bool = False):
        super().__init__(parent=None)
        self.is_typed = is_typed
        self.praser = praser
        self.propertyData = property
        self.sister_id = None
        self.__parent_grid = None

        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    
        if not self.is_typed: self.test_restrictions()

    def getParentContainer(self):
        return self.__parent_grid
         
    def setParentContainer(self, host: "PropertyGrid"):
        self.__parent_grid = host

    def setVariable(self, newData: T):
        Logger.logDebug("JemLib", "PropertyField", "setVariable", f"Var: {self.propertyData.variableName()} NewState:{str(newData)}")
        self.propertyData.updateData(newData)
        self.sigPropertyFieldChanged.emit()

    #region Commons / Nestables


    def test_restrictions(self):
        restrictions = self.praser.getObjectConstraints(self.propertyData)
        setup_expandable = False

        for restriction in restrictions:
            if restriction["type"] == DataConstraints.OtherMod.Expandable and setup_expandable == False:
                btnText = "Edit..."

                if "text" in restriction:
                    btnText = restriction["text"]

                self.editor = QPushButton(self)
                self.editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                self.editor.clicked.connect(self.nested_edit)
                self.editor.setText(btnText)
                #print(self.editor)

                self.editor_button = QPushButton(self)
                self.editor_button.setMaximumWidth(16)
                self.editor_button.setContentsMargins(0,0,0,0)
                self.editor_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

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

                setup_expandable = True

    def nested_paste(self):
        item_type: type | None = self.propertyData.variableType()
        
        clipboard_data = PropertySystem.getSettingsClipboard(item_type)
        if clipboard_data != None:
            pastable_data = PropertySystem.deepcopy(clipboard_data)
            self.setVariable(pastable_data)

    def nested_copy(self):
        item_type: type | None = self.propertyData.variableType()
        item_data: any | None = PropertySystem.deepcopy(self.propertyData.variableData())

        if item_data != None and item_type != None:
            PropertySystem.setSettingsClipboard(item_type, item_data)

    def nested_edit(self):
        self.nested_page_dialog = PropertyGrid_Subwindow(self)
        self.nested_page_dialog.setWindowTitle(str(self.propertyData.variableName()))
        self.nested_page_dialog.setWindowFlags(Qt.WindowType.Widget)
        self.nested_page_layout = QVBoxLayout(self)
        self.nested_page_layout.setContentsMargins(0,0,0,0)
        self.nested_page_layout.setSpacing(0)

        from ..PropertyViewport import PropertyViewport
        self.nested_page_properties = PropertyViewport(self.getParentContainer(), self.praser)
        self.nested_page_layout.addWidget(self.nested_page_properties)
        self.nested_page_dialog.setLayout(self.nested_page_layout)

        self.nested_page_properties.setDataObject(self.propertyData.variableData())
        self.getParentContainer().navigateForwards(self.nested_page_dialog)
        self.nested_page_dialog.show()

    #endregion
