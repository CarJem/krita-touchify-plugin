from typing import Any
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from jemlib.alib_vaporjem.extensions.krita_extensions import KritaExtensions
from jemlib.api_touchify.ContextRequirements import ContextRequirements
from krita import *
from jemlib.api_krita import KritaAPI
from jemlib.api_krita.enums.tool import Tool

from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.dialogs.PropertyGrid_Subwindow import PropertyGrid_Subwindow
from jemlib.managers.IconRepository import IconRepository

DATA_INDEX = 3

class PropertyGrid_SelectorDialog(PropertyGrid_Subwindow):
    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)

        self.selector_registry_type = None

        self.list_view = QListWidget()
        self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_view.setMovement(QListView.Movement.Static)
        self.list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.list_view.itemSelectionChanged.connect(self.updateSelected)
        self.list_view.itemClicked.connect(self.updateSelected)

        self.selected_item = "null"

        self.show_status_bar = False
        self.is_checkbox_selector = False

        self.filter_bar = QLineEdit()
        self.filter_bar.setPlaceholderText("Filter...")
        self.filter_bar.textChanged.connect(self.onFilterUpdate)

        self.header = QWidget(self)
        self.header.setContentsMargins(0,0,0,0)

        self.header_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

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
        self.dlg_layout.addWidget(self.list_view)
        self.dlg_layout.addWidget(self.filter_bar)

        self.setLayout(self.dlg_layout)

    def onFilterUpdate(self):
        currentFilter = self.filter_bar.text()
        for i in range(self.list_view.count()):
            currentItem = self.list_view.item(i)
            if currentItem:

                filterAllows = currentFilter.lower() in currentItem.text().lower() or currentFilter.lower() in str(currentItem.data(DATA_INDEX)).lower()

                if filterAllows or currentFilter == "":
                    currentItem.setHidden(False)
                else:
                    currentItem.setHidden(True)
        

    def updateSelected(self):
        if self.show_status_bar:
            self.header_icon.setVisible(True)
            self.header_text.setVisible(True)
        else:
            self.header_icon.setVisible(False)
            self.header_text.setVisible(False)

        if self.is_checkbox_selector:
            itemList: list[QListWidgetItem] = [self.list_view.item(i) for i in range(self.list_view.count())]
            currentItems = [z for z in itemList if z.checkState() == Qt.CheckState.Checked]
            if len(currentItems) > 0:
                self.selected_item = ",".join([z.data(DATA_INDEX) for z in currentItems])
                self.header_icon.setIcon(QIcon())
                self.header_text.setText(self.selected_item)
            else: 
                self.selected_item = "null"
                self.header_icon.setIcon(QIcon())
                self.header_text.setText("")
        else:
            currentItem = self.list_view.currentItem()
            if currentItem:
                self.selected_item = str(currentItem.data(DATA_INDEX))
                self.header_icon.setIcon(currentItem.icon())
                self.header_text.setText(self.selected_item)
            else: 
                self.selected_item = "null"
                self.header_icon.setIcon(QIcon())
                self.header_text.setText("")




    def selectedResult(self):
        return self.selected_item


    def load_list(self, mode, entries: Any = None, selection_input: str | None = None):
        self.list_view.setSelectionRectVisible(True)
        
        self.list_view.setStyleSheet(f"""
            QListWidget::item:selected {{ 
                background-color: palette(alternate-base);
            }}
        """)

        selected_items: list[QListWidgetItem] = []

        if mode == DataConstraints.StrMod.IconSelection:
            self.show_status_bar = True
            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.list_view.setUniformItemSizes(True)
            presets = IconRepository.iconList("krita")
            for preset_key in presets:
                listItem = QListWidgetItem()
                listItem.setIcon(IconRepository.iconLoader(preset_key))
                listItem.setData(DATA_INDEX, preset_key)
                if preset_key == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

            custom_icons = IconRepository.iconList("custom")
            for customIconName in custom_icons:
                listItem = QListWidgetItem()
                listItem.setIcon(IconRepository.iconLoader(customIconName))
                listItem.setData(DATA_INDEX, customIconName)
                if customIconName == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)
            
        elif mode == DataConstraints.StrMod.TouchifyRegistry:
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            for preset_key, value in entries.items():
                displayName = f"{str(value)}\n{preset_key.actual_key}"
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setData(DATA_INDEX, preset_key.actual_key)
                if preset_key.actual_key == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

        elif mode == DataConstraints.StrMod.BrushSelection:
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            presets = KritaAPI.get_presets()
            for preset_key in presets:
                preset = presets[preset_key]
                listItem = QListWidgetItem()
                listItem.setIcon(IconRepository.brushIcon(preset.name(), presets))
                listItem.setText(preset.name())
                listItem.setData(DATA_INDEX, preset_key)
                if preset_key == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

        elif mode == DataConstraints.StrMod.DockerSelection:
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            dockers = KritaAPI.get_dockers()
            for dockerData in dockers:
                displayName = f"{dockerData.windowTitle()}\n---[{dockerData.objectName()}]---"
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setData(DATA_INDEX, dockerData.objectName())
                if dockerData.objectName() == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

        elif mode == DataConstraints.StrMod.ActionSelection:
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            actions = KritaAPI.get_actions()
            for actionData in actions:
                action_text = KritaExtensions.formatActionText(actionData.text())
                action_tooltip = KritaExtensions.formatActionText(actionData.toolTip())

                if action_text != "":
                    displayName = f"{action_text}\n[[{actionData.objectName()}]]"
                elif action_tooltip != "":
                    displayName = f"{action_tooltip}\n[[{actionData.objectName()}]]"
                else:
                    displayName = f"[[{actionData.objectName()}]]\n"

                icon = actionData.icon()
                if icon.isNull(): icon = IconRepository.fallbackIcon()
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setIcon(icon)
                listItem.setData(DATA_INDEX, actionData.objectName())
                if actionData.objectName() == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

        elif mode == DataConstraints.StrMod.ToolSelection:
            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.list_view.setUniformItemSizes(True)
            for value, data in Tool._member_map_.items():
                data: Tool
                listItem = QListWidgetItem()
                listItem.setToolTip(data.pretty_name)
                listItem.setIcon(data.icon)
                listItem.setData(DATA_INDEX, data.value)
                if data.value == selection_input: selected_items.append(listItem)
                self.list_view.addItem(listItem)

        elif mode == DataConstraints.StrMod.RequirementSelection:
            __currentRequirements = selection_input.split(",")
            if "" in __currentRequirements: __currentRequirements.remove("")

            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)

            def addItem(text: str, value: str, icon: QIcon):
                listItem = QListWidgetItem()
                listItem.setFlags(listItem.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                listItem.setCheckState(Qt.CheckState.Unchecked)
                listItem.setToolTip(text)
                listItem.setText(text)
                listItem.setData(DATA_INDEX, value)
                listItem.setIcon(icon)
            
                if value in __currentRequirements: selected_items.append(listItem)
                self.list_view.addItem(listItem)

            self.is_checkbox_selector = True
            for data in ContextRequirements.getRequirements():
                addItem(data['name'], data['value'], data['icon'])

        elif mode == DataConstraints.StrMod.MultiToolSelection:
            __currentRequirements = selection_input.split(",")
            if "" in __currentRequirements: __currentRequirements.remove("")

            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.list_view.setUniformItemSizes(True)

            self.is_checkbox_selector = True
            for value, data in Tool._member_map_.items():
                data: Tool
                listItem = QListWidgetItem()
                listItem.setFlags(listItem.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                listItem.setCheckState(Qt.CheckState.Unchecked)
                listItem.setToolTip(data.pretty_name)
                listItem.setIcon(data.icon)
                listItem.setData(DATA_INDEX, data.value)
                if data.value in __currentRequirements: selected_items.append(listItem)
                self.list_view.addItem(listItem)
        
        self.list_view.model().sort(0, Qt.SortOrder.DescendingOrder)
        
        if self.is_checkbox_selector:
            for item in selected_items:
                item.setCheckState(Qt.CheckState.Checked)
        else:
            for item in selected_items:
                item.setSelected(True)

class PropertyGrid_SelectorDialogItem(QListWidgetItem):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()