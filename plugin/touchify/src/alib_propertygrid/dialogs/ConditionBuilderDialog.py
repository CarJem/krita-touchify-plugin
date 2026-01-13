from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from jemlib.alib_propertygrid.dialogs.PropertyGrid_Subview import PropertyGrid_Subview
from jemlib.api_touchify.ContextRequirements import ContextRequirements
from krita import *


DATA_INDEX = 3

class ConditionBuilderDialog(PropertyGrid_Subview):
    @staticmethod
    def Setup(dlg: "ConditionBuilderDialog", parent: QWidget, mode: str, options: dict[str, any]):
        return PropertyGrid_Subview.Setup(dlg, parent, mode, options, cls=ConditionBuilderDialog)

    def initContents(self):
        self.__selectedConditions: list[ContextRequirements.Rule] = []

        self.__listView = QListWidget(self)
        self.__listView.setResizeMode(QListView.ResizeMode.Adjust)
        self.__listView.setMovement(QListView.Movement.Static)
        self.__listView.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.__listView.setStyleSheet(f"""
            QListWidget::item:selected {{ 
                background-color: palette(alternate-base);
            }}
        """)

        self.filter_bar = QLineEdit(self)
        self.filter_bar.setPlaceholderText("Filter...")
        self.filter_bar.textChanged.connect(self.onFilterUpdate)

        self.header = QWidget(self)
        self.header.setContentsMargins(0,0,0,0)

        self.header_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.header_buttons.rejected.connect(self.onClose)
        if 'close_on_save' in self.getOptions():
            if self.getOptions()['close_on_save'] == False:
                self.header_buttons.accepted.connect(self.onApply)
            else:
                self.header_buttons.accepted.connect(self.onSave)
        else:
            self.header_buttons.accepted.connect(self.onSave)

        self.header_text = QLabel(self.header)
        self.header_text.setContentsMargins(0,0,0,0)

        self.header_icon = QPushButton(self.header)
        self.header_icon.setContentsMargins(0,0,0,0)
        self.header_icon.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.header_icon.setFlat(True)

        self.header_layout = QHBoxLayout(self.header)
        self.header.setLayout(self.header_layout)
        self.header_layout.setSpacing(0)
        self.header_layout.setContentsMargins(0,6,0,6)
        self.header_layout.addWidget(self.header_icon)
        self.header_layout.addWidget(self.header_text, 1)
        self.header_layout.addWidget(self.header_buttons)

        self.dlg_layout = QVBoxLayout(self)
        self.dlg_layout.setContentsMargins(0,0,0,0)
        self.dlg_layout.addWidget(self.header)
        self.dlg_layout.addWidget(self.__listView)
        self.dlg_layout.addWidget(self.filter_bar)

        self.setLayout(self.dlg_layout)

    def getAcceptResult(self):
        result = ""
        
        for x in self.__selectedConditions:
            rx = x.export()
            if not rx: continue

            if result != "": result += ","
            result += rx

        return result

    def onFilterUpdate(self):
        currentFilter = self.filter_bar.text()
        for i in range(self.__listView.count()):
            currentItem = self.__listView.item(i)
            if currentItem:

                filterAllows = currentFilter.lower() in currentItem.text().lower() or currentFilter.lower() in str(currentItem.data(DATA_INDEX)).lower()

                if filterAllows or currentFilter == "":
                    currentItem.setHidden(False)
                else:
                    currentItem.setHidden(True)
    
    def onConditionStateChanged(self, rule: ContextRequirements.Rule, disable: bool = False):
        if not rule: return
        other_conditions = [x for x in self.__selectedConditions if x.type == rule.type and x.value == rule.value]
        if len(other_conditions) != 0:
            for x in other_conditions: self.__selectedConditions.remove(x)
        if disable == False: self.__selectedConditions.append(rule)

    def setCurrentConditions(self, input: str):
        self.__selectedConditions = ContextRequirements.parse(input)

    def createItem(self, rule: ContextRequirements.DisplayRule):
        listItem = QListWidgetItem()
        listItem.setToolTip(rule.name)
        listItem.setData(DATA_INDEX, rule.value)
        listItem.setIcon(rule.icon)
        return listItem
    
    def createItemWidget(self, rule: ContextRequirements.DisplayRule):
        itemWidget = QWidget(self)
        itemWidget.setContentsMargins(0,0,0,0)

        __label = QLabel(itemWidget)
        __label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        __label.setText(rule.name)

        __off_checkbox = QRadioButton(itemWidget)
        __off_checkbox.setAutoFillBackground(True)
        __off_checkbox.setText("(off)")
        __off_checkbox.setContentsMargins(0,0,0,0)
        __off_checkbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        __or_checkbox = QRadioButton(itemWidget)
        __or_checkbox.setAutoFillBackground(True)
        __or_checkbox.setText("OR")
        __or_checkbox.setContentsMargins(0,0,0,0)
        __or_checkbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        __and_checkbox = QRadioButton(itemWidget)
        __and_checkbox.setAutoFillBackground(True)
        __and_checkbox.setText("AND")
        __and_checkbox.setContentsMargins(0,0,0,0)
        __and_checkbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        __not_checkbox = QRadioButton(itemWidget)
        __not_checkbox.setAutoFillBackground(True)
        __not_checkbox.setText("NOT")
        __not_checkbox.setContentsMargins(0,0,0,0)
        __not_checkbox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        __editorLayout = QHBoxLayout(itemWidget)
        __editorLayout.setSpacing(0)
        __editorLayout.setContentsMargins(0,0,0,0)
        __editorLayout.addWidget(__label, 1)
        __editorLayout.addWidget(__off_checkbox)
        __editorLayout.addWidget(__or_checkbox)
        __editorLayout.addWidget(__and_checkbox)
        __editorLayout.addWidget(__not_checkbox)
        itemWidget.setLayout(__editorLayout)

        __radio_group = QButtonGroup(itemWidget)
        __radio_group.addButton(__off_checkbox, 0)
        __radio_group.addButton(__or_checkbox, ContextRequirements.Mode.OR)
        __radio_group.addButton(__and_checkbox, ContextRequirements.Mode.AND)
        __radio_group.addButton(__not_checkbox, ContextRequirements.Mode.NOT)


        __or_rule = rule.asRule(ContextRequirements.Mode.OR)
        __and_rule = rule.asRule(ContextRequirements.Mode.AND)
        __not_rule = rule.asRule(ContextRequirements.Mode.NOT)

        if __or_rule in self.__selectedConditions:
            __or_checkbox.setChecked(True)
        elif __and_rule in self.__selectedConditions:
            __and_checkbox.setChecked(True)
        elif __not_rule in self.__selectedConditions:
            __not_checkbox.setChecked(True)
        else:
            __off_checkbox.setChecked(True)

        __or_checkbox.clicked.connect(lambda: self.onConditionStateChanged(__or_rule))
        __and_checkbox.clicked.connect(lambda: self.onConditionStateChanged(__and_rule))
        __not_checkbox.clicked.connect(lambda: self.onConditionStateChanged(__not_rule))
        __off_checkbox.clicked.connect(lambda: self.onConditionStateChanged(__not_rule, True))

        return itemWidget
    
    def loadList(self):
        self.__listView.setSelectionRectVisible(True)
        self.__listView.setViewMode(QListView.ViewMode.ListMode)
        self.__listView.setUniformItemSizes(True)
        for data in ContextRequirements.getKnownValues():
            listItem = self.createItem(data)
            self.__listView.addItem(listItem)
            self.__listView.setItemWidget(listItem, self.createItemWidget(data))