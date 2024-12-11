from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from touchify.src.components.pyqt.event_filters.MouseWheelWidgetAdjustmentGuard import MouseWheelWidgetAdjustmentGuard

from touchify.src.ext.types.TypedList import *
from touchify.src.resources import *

from touchify.src.components.touchify.property_grid.utils.PropertyUtils_Extensions import *
from touchify.src.components.touchify.property_grid.PropertyGrid import *
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from touchify.src.components.touchify.property_grid.fields.PropertyField import *





class PropertyField_Str(PropertyField):
    def __init__(self, variable_name=str, variable_data=str, variable_source=any):
        super().__init__(variable_name, variable_data, variable_source, True)


        self.is_icon_viewer = False
        self.is_docker_selector = False
        self.is_action_selection = False
        self.is_hotkey_selector = False
        self.is_brush_selection = False

        self.is_special_selector = False
        self.special_selector_type = "none"


        self.is_combobox = False
        self.combobox_items: list[tuple[str, str]] = []
        
        self.editorHelper: QPushButton | None = None

        self.test_restrictions(variable_name)

        if self.is_special_selector:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            self.editorHelper = QPushButton()


            if self.special_selector_type == "icons": 
                self.editorHelper.setIcon(ResourceManager.iconLoader(self.variable_data.replace("\n", "\\n")))
            elif self.special_selector_type == "dockers": 
                self.editorHelper.setIcon(ResourceManager.iconLoader("properties"))
            elif self.special_selector_type == "actions":
                self.editorHelper.setIcon(ResourceManager.iconLoader("properties"))
            elif self.special_selector_type == "brushes":
                self.editorHelper.setIcon(ResourceManager.brushIcon(self.variable_data.replace("\n", "\\n")))

            self.editorHelper.clicked.connect(lambda: self.helperRequested(self.special_selector_type))

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            editorLayout.addWidget(self.editorHelper)
            self.setLayout(editorLayout)
            self.setLayout(editorLayout)
        elif self.is_combobox:
            self.editor = QComboBox(self)
            self.editor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.editor.installEventFilter(MouseWheelWidgetAdjustmentGuard(self))
            for item in self.combobox_items:
                self.editor.insertItem(0, item[0])
                self.editor.setItemData(0, item[1], 1)
            index = self.editor.findData(self.variable_data, 1, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.editor.setCurrentIndex(index)
            self.editor.currentIndexChanged.connect(self.currentIndexChanged)

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)
        else:
            self.editor = QLineEdit()
            self.editor.textChanged.connect(self.textChanged)
            self.editor.setText(self.variable_data.replace("\n", "\\n"))

            editorLayout = QHBoxLayout(self)
            editorLayout.setSpacing(0)
            editorLayout.setContentsMargins(0,0,0,0)
            editorLayout.addWidget(self.editor)
            self.setLayout(editorLayout)

    def test_restrictions(self, variable_name: str):
        restrictions = PropertyUtils_Extensions.classRestrictions(self.variable_source, variable_name)
        list_setup = False

        for restriction in restrictions:
            if list_setup == False:
                if restriction["type"] == "values":
                    combobox_items =  list[tuple[str, str]]()
                    avaliableItems = list[str](restriction["entries"])
                    for item in avaliableItems:
                        input = (item, item)
                        combobox_items.append(input)                         
                    self.combobox_items = combobox_items
                    self.is_combobox = True
                    list_setup = True
                elif restriction["type"] == "action_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "actions"
                    list_setup = True
                elif restriction["type"] == "docker_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "dockers"
                    list_setup = True
                elif restriction["type"] == "icon_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "icons"
                    list_setup = True
                elif restriction["type"] == "brush_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "brushes"
                    list_setup = True
                elif restriction["type"] == "registry_docker_group_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "docker_groups"
                    list_setup = True
                elif restriction["type"] == "registry_popup_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "popups"
                    list_setup = True
                elif restriction["type"] == "registry_canvas_preset_selection":
                    self.is_special_selector = True
                    self.special_selector_type = "canvas_presets"
                    list_setup = True
                elif restriction["type"] == "hotkey_selection":
                    combobox_items = list[tuple[str, str]]()
                    avaliableItems = TouchifySettings.instance().hotkey_options_storage
                    combobox_items.append(("None", "none"))
                    for item in avaliableItems:
                        input = (avaliableItems[item]["displayName"], item)
                        combobox_items.append(input)
                    self.combobox_items = combobox_items
                    self.is_combobox = True
                    list_setup = True
                


    def dlg_accept(self):
        self.stack_host.goBack()
        self.dlg.accept()
    
    def dlg_reject(self):
        self.stack_host.goBack()
        self.dlg.reject()

    def helperRequested(self, mode):
        self.dlg = PropertyGrid_SelectorDialog(self.stack_host)
        self.dlg.setWindowFlags(Qt.WindowType.Widget)
        self.dlg.header_buttons.accepted.connect(lambda: self.dlg_accept())
        self.dlg.header_buttons.rejected.connect(lambda: self.dlg_reject())

        self.dlg.load_list(mode)
        self.stack_host.setCurrentIndex(self.stack_host.addWidget(self.dlg))
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
