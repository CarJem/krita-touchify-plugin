from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_propertygrid.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from jemlib.alib_widgets.buttons.ColorButton import ColorButton
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
        self.touchify_registry_type: str = "none"
        self.is_touchify_registry_selector = False
        self.touchify_registry_callback = None
        self.special_selector_entries: dict = {}
        self.is_multiline_string = False
        self.is_python_editor = False
        self.is_color_picker = False
        self.is_combobox = False
        self.placeholder_text = None
        self.combobox_items: list[tuple[str, str]] = []
        
        self.editorHelper: QPushButton | None = None

        self.test_restrictions(self.propertyData.variableName())

        if self.is_color_picker: self.create_color_picker()
        elif self.is_special_selector: self.create_special_selector()
        elif self.is_combobox: self.create_combobox()
        else: self.create_textbox()


    def test_restrictions(self, variable_name: str):
        restrictions = self.praser.getObjectConstraints(self.propertyData)
        list_setup = False

        for restriction in restrictions:
            if list_setup == False:
                if restriction["type"] == DataConstraints.StrMod.Placeholder:
                    self.placeholder_text = restriction["text"]
                elif restriction["type"] == DataConstraints.StrMod.ColorPicker:
                    self.is_color_picker = True
                elif restriction["type"] == DataConstraints.StrMod.PythonEditor:
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
                elif restriction["type"] == DataConstraints.StrMod.EnumStrValues:
                    combobox_items =  list[tuple[str, str]]()
                    avaliableItems: EnumStr = restriction["entries"]
                    for name, value in avaliableItems.to_dict().items():
                        input = (name.replace("_", " "), value)
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
                        self.is_touchify_registry_selector = True
                        self.touchify_registry_type = restriction["registry_type"]
                        self.touchify_registry_callback = restriction["callback"]
                        self.special_selector_entries = dict(restriction["entries"])
                    list_setup = True


    def create_combobox(self):
        self.editor = QComboBox(self)
        self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
        for item in self.combobox_items:
            self.editor.insertItem(0, item[0])
            self.editor.setItemData(0, item[1], 1)
        index = self.editor.findData(self.propertyData.variableData(), 1, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.editor.setCurrentIndex(index)
            
        self.editor.currentIndexChanged.connect(self.onCurrentIndexChanged)

        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)
        
    def create_textbox(self):
        if self.is_python_editor:
            self.editor = PythonEditor(self)
            self.editor.setPlaceholderText(self.placeholder_text)
            self.editor.setMinimumHeight(300)
            self.editor.textChanged.connect(self.onMultilineTextChanged)
            self.editor.setPlainText(self.propertyData.variableData())                
        elif self.is_multiline_string:
            self.editor = QPlainTextEdit(self)
            self.editor.setPlaceholderText(self.placeholder_text)
            self.editor.setMinimumHeight(300)
            self.editor.textChanged.connect(self.onMultilineTextChanged)
            self.editor.setPlainText(self.propertyData.variableData())
        else:
            self.editor = QLineEdit(self)
            self.editor.setPlaceholderText(self.placeholder_text)
            self.editor.textChanged.connect(self.onTextChanged)
            self.editor.setText(self.propertyData.variableData().replace("\n", "\\n"))

        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def create_special_selector(self):
        self.editor = QLineEdit(self)
        self.editor.textChanged.connect(self.onTextChanged)
        self.editor.setText(self.propertyData.variableData().replace("\n", "\\n"))

        self.editorHelper = QPushButton(self)
        self.editorInspector = None

        if self.special_selector_type == DataConstraints.StrMod.IconSelection: 
            self.is_icon_viewer = True
            self.editor.setFixedHeight(24)
            self.editor.setContentsMargins(0,0,0,0)
            self.editorHelper.setFixedSize(24,24)
            self.editorHelper.setContentsMargins(0,0,0,0)
            self.editorHelper.setIcon(IconRepository.iconLoader(self.propertyData.variableData().replace("\n", "\\n")))
            self.editor.setPlaceholderText("(unset icon)")
        elif self.special_selector_type == DataConstraints.StrMod.BrushSelection:
            self.is_brush_selection = True
            self.editor.setFixedHeight(24)
            self.editor.setContentsMargins(0,0,0,0)
            self.editorHelper.setFixedSize(24,24)
            self.editorHelper.setContentsMargins(0,0,0,0)
            self.editorHelper.setIcon(IconRepository.brushIcon(self.propertyData.variableData().replace("\n", "\\n")))
            self.editor.setPlaceholderText("(unset brush)")
        elif self.is_touchify_registry_selector:
            self.editor.setFixedHeight(24)
            self.editor.setContentsMargins(0,0,0,0)

            #self.editorInspector = QPushButton()
            #self.editorInspector.setFixedSize(24,24)
            #self.editorInspector.setContentsMargins(0,0,0,0)
            #self.editorInspector.setText("...")
            #self.editorInspector.clicked.connect(self.onTouchifyInspectorRequested)

            self.editorHelper.setFixedSize(24,24)
            self.editorHelper.setContentsMargins(0,0,0,0)
            self.editorHelper.setIcon(IconRepository.iconLoader("properties"))
        else:
            self.editor.setFixedHeight(24)
            self.editor.setContentsMargins(0,0,0,0)
            self.editorHelper.setFixedSize(24,24)
            self.editorHelper.setContentsMargins(0,0,0,0)
            self.editorHelper.setIcon(IconRepository.iconLoader("properties"))

        self.editorHelper.clicked.connect(lambda: self.onHelperRequested(self.special_selector_type, self.special_selector_entries))
        


        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        if self.editorInspector: editorLayout.addWidget(self.editorInspector)
        editorLayout.addWidget(self.editorHelper)
        self.setLayout(editorLayout)

    def create_color_picker(self):
        color_str = self.propertyData.variableData()
        current_color = QColor(color_str)
        if not current_color.isValid(): current_color = QColor("black")

        self.editor = ColorButton(self)
        self.editor.setColor(current_color)
        self.editor.colorChanged.connect(self.onColorChanged)

        editorLayout = QHBoxLayout(self)
        editorLayout.setSpacing(0)
        editorLayout.setContentsMargins(0,0,0,0)
        editorLayout.addWidget(self.editor)
        self.setLayout(editorLayout)

    def onHelperDlgAccept(self):
        self.getParentContainer().navigateBackwards()
        self.dlg.accept()
    
    def onHelperDlgReject(self):
        self.getParentContainer().navigateBackwards()
        self.dlg.reject()

    def onHelperRequested(self, mode, entries):
        self.dlg = PropertyGrid_SelectorDialog(self.getParentContainer())
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.dlg.header_buttons.accepted.connect(lambda: self.onHelperDlgAccept())
        self.dlg.header_buttons.rejected.connect(lambda: self.onHelperDlgReject())

        self.dlg.load_list(mode, entries, self.propertyData.variableData())
        self.getParentContainer().navigateForwards(self.dlg)
        if self.dlg.exec_():
            result = self.dlg.selectedResult()
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(IconRepository.iconLoader(result))
            elif self.is_brush_selection:
                self.editorHelper.setIcon(IconRepository.brushIcon(result))
            self.editor.setText(result)

    def onTouchifyInspectorRequested(self):
        if self.touchify_registry_callback:
            self.touchify_registry_callback(self, self.touchify_registry_type, self.propertyData.variableData())

    def onColorChanged(self):
        new_color = self.editor.color().name(QColor.NameFormat.HexArgb)
        super().setVariable(new_color)

    def onCurrentIndexChanged(self):
        newData = str(self.editor.currentData(1)).replace("\\n", "\n")
        super().setVariable(newData)

    def onMultilineTextChanged(self):
        plain_text_editor: QPlainTextEdit = self.editor
        if isinstance(plain_text_editor, QPlainTextEdit):
            newData = plain_text_editor.toPlainText()
            super().setVariable(newData)

    def onTextChanged(self):
        newData = self.editor.text().replace("\\n", "\n")
        
        if self.editorHelper:
            if self.is_icon_viewer: 
                self.editorHelper.setIcon(IconRepository.iconLoader(newData.replace("\n", "\\n")))
            elif self.is_brush_selection: 
                self.editorHelper.setIcon(IconRepository.brushIcon(newData.replace("\n", "\\n")))
        
        super().setVariable(newData)
