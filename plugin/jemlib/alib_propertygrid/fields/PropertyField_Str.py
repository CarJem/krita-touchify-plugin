from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_propertygrid.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from jemlib.alib_widgets.textedit.PythonEditor import PythonEditor
from jemlib.alib_datatypes.TypedList import *
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.managers.IconRepository import *


from jemlib.alib_propertygrid.PropertyGrid import *
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from jemlib.alib_propertygrid.fields.PropertyField import *

if TYPE_CHECKING:
    from jemlib.alib_propertygrid.data.DataHandler import DataHandler



class PropertyField_Str(PropertyField[str]):
    def __init__(self, handler: "DataHandler", property: DataPath[str]):
        super().__init__(handler, property, True)


        self.is_icon_viewer = False
        self.is_brush_selection = False
        self.is_special_selector = False
        self.special_selector_type = "none"
        self.special_selector_entries: dict = {}
        self.is_multiline_string = False
        self.is_python_editor = False
        self.is_combobox = False
        self.combobox_items: list[tuple[str, str]] = []
        
        self.editorHelper: QPushButton | None = None

        self.test_restrictions(self.propertyData.variableName())

        if self.is_special_selector:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.propertyData.variableData().replace("\n", "\\n"))

            self.editorHelper = QPushButton()


            if self.special_selector_type == "icons": 
                self.editorHelper.setIcon(IconRepository.iconLoader(self.propertyData.variableData().replace("\n", "\\n")))
            elif self.special_selector_type == "brushes":
                self.editorHelper.setIcon(IconRepository.brushIcon(self.propertyData.variableData().replace("\n", "\\n")))
            else:
                self.editorHelper.setIcon(IconRepository.iconLoader("properties"))

            self.editorHelper.clicked.connect(lambda: self.helperRequested(self.special_selector_type, self.special_selector_entries))

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            editorLayout.addWidget(self.editorHelper)
            self.setLayout(editorLayout)
        elif self.is_combobox:
            self.editor = QComboBox(self)
            self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
            for item in self.combobox_items:
                self.editor.insertItem(0, item[0])
                self.editor.setItemData(0, item[1], 1)
            index = self.editor.findData(self.propertyData.variableData(), 1, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.editor.setCurrentIndex(index)
                
            self.editor.currentIndexChanged.connect(self.currentIndexChanged)

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)
        else:
            if self.is_python_editor:
                self.editor = PythonEditor(self)
                self.editor.setMinimumHeight(300)
                self.editor.textChanged.connect(self.multilineTextChanged)
                self.editor.setPlainText(self.propertyData.variableData())                
            elif self.is_multiline_string:
                self.editor = QPlainTextEdit(self)
                self.editor.setMinimumHeight(300)
                self.editor.textChanged.connect(self.multilineTextChanged)
                self.editor.setPlainText(self.propertyData.variableData())
            else:
                self.editor = QLineEdit(self)
                self.editor.textChanged.connect(self.textChanged)
                self.editor.setText(self.propertyData.variableData().replace("\n", "\\n"))

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

    def test_restrictions(self, variable_name: str):
        restrictions = self.praser.getObjectConstraints(self.propertyData)
        list_setup = False

        for restriction in restrictions:
            if list_setup == False:
                if restriction["type"] == DataConstraints.StrMod.Multiline:
                    self.is_multiline_string = True
                elif restriction["type"] == DataConstraints.StrMod.PythonEdtior:
                    self.is_python_editor = True
                elif restriction["type"] == DataConstraints.StrMod.Values:
                    combobox_items =  list[tuple[str, str]]()
                    avaliableItems = list[str](restriction["entries"])
                    for item in avaliableItems:
                        input = (item, item)
                        combobox_items.append(input)                         
                    self.combobox_items = combobox_items
                    self.is_combobox = True
                    list_setup = True
                elif restriction["type"] == DataConstraints.StrMod.ValuesWithIndex:
                    combobox_items =  list[tuple[str, str]]()
                    avaliableItems = list[str](restriction["entries"])
                    for idx, item in enumerate(avaliableItems):
                        input = (item, str(idx))
                        combobox_items.append(input)                         
                    self.combobox_items = combobox_items
                    self.is_combobox = True
                    list_setup = True
                elif restriction["type"] in DataConstraints.strSelectors():
                    self.is_special_selector = True
                    self.special_selector_type = restriction["type"]
                    if "entries" in restriction and restriction["type"] == DataConstraints.StrMod.TouchifyRegistry:
                        self.special_selector_entries = dict(restriction["entries"])
                    list_setup = True
                


    def dlg_accept(self):
        self.stack_host.goBack()
        self.dlg.accept()
    
    def dlg_reject(self):
        self.stack_host.goBack()
        self.dlg.reject()

    def helperRequested(self, mode, entries):
        self.dlg = PropertyGrid_SelectorDialog(self.stack_host)
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.dlg.header_buttons.accepted.connect(lambda: self.dlg_accept())
        self.dlg.header_buttons.rejected.connect(lambda: self.dlg_reject())

        self.dlg.load_list(mode, entries, self.propertyData.variableData())
        self.stack_host.setCurrentIndex(self.stack_host.addWidget(self.dlg))
        if self.dlg.exec_():
            result = self.dlg.selectedResult()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(IconRepository.iconLoader(result))
            elif self.is_brush_selection:
                self.editorHelper.setIcon(IconRepository.brushIcon(result))
            self.editor.setText(result)
            

    def currentIndexChanged(self):
        newData = str(self.editor.currentData(1)).replace("\\n", "\n")
        super().setVariable(newData)

    def multilineTextChanged(self):
        plain_text_editor: QPlainTextEdit = self.editor
        if isinstance(plain_text_editor, QPlainTextEdit):
            newData = plain_text_editor.toPlainText()
            super().setVariable(newData)

    def textChanged(self):
        newData = self.editor.text().replace("\\n", "\n")
        
        if self.editorHelper:
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(IconRepository.iconLoader(newData.replace("\n", "\\n")))
            elif self.is_brush_selection: 
                self.editorHelper.setIcon(IconRepository.brushIcon(newData.replace("\n", "\\n")))
        
        super().setVariable(newData)
