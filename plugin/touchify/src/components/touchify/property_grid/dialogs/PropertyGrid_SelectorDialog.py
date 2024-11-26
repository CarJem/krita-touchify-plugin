from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from krita import *
from touchify.src.stylesheet import Stylesheet
from touchify.src.components.touchify.property_grid.dialogs.PropertyGrid_Dialog import PropertyGrid_Dialog

from touchify.src.resources import ResourceManager


DATA_INDEX = 3

class PropertyGrid_SelectorDialogItem(QListWidgetItem):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

class PropertyGrid_SelectorDialog(PropertyGrid_Dialog):
    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)

        self.list_view = QListWidget()
        self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_view.setMovement(QListView.Movement.Static)
        self.list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)
        self.list_view.itemSelectionChanged.connect(self.updateSelected)
        self.list_view.itemClicked.connect(self.updateSelected)

        self.selected_item = "null"

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
        self.header_layout.setSpacing(0)
        self.header_layout.setContentsMargins(0,6,0,6)
        self.header_layout.addWidget(self.header_icon)
        self.header_layout.addWidget(self.header_text, 1)
        self.header_layout.addWidget(self.header_buttons)
        self.header.setLayout(self.header_layout)

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

    def load_list(self, mode):
        self.list_view.setSelectionRectVisible(True)
        self.list_view.setStyleSheet(Stylesheet.instance().propertygrid_selectordialog_listview)
        if mode == "icons":
            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.list_view.setUniformItemSizes(True)
            presets = ResourceManager.getIconList()
            for preset_key in presets:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(preset_key))
                listItem.setData(DATA_INDEX, preset_key)
                self.list_view.addItem(listItem)

            custom_icons = ResourceManager.getCustomIconList()
            for customIconName in custom_icons:
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.iconLoader(customIconName))
                listItem.setData(DATA_INDEX, customIconName)
                self.list_view.addItem(listItem)
        elif mode == "brushes":
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            presets = ResourceManager.getBrushPresets()
            for preset_key in presets:
                preset = presets[preset_key]
                listItem = QListWidgetItem()
                listItem.setIcon(ResourceManager.brushIcon(preset.name()))
                listItem.setText(preset.name())
                listItem.setData(DATA_INDEX, preset_key)
                self.list_view.addItem(listItem)
        elif mode == "dockers":
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            dockers = Krita.instance().dockers()
            for dockerData in dockers:
                displayName = f"{dockerData.windowTitle()}\n---[{dockerData.objectName()}]---"
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setData(DATA_INDEX, dockerData.objectName())
                self.list_view.addItem(listItem)
        elif mode == "actions":
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.list_view.setUniformItemSizes(True)
            actions = Krita.instance().actions()
            for actionData in actions:
                displayName = f"{actionData.toolTip()}\n---[{actionData.objectName()}]---"
                icon = actionData.icon()
                listItem = QListWidgetItem()
                listItem.setText(displayName)
                listItem.setIcon(icon)
                listItem.setData(DATA_INDEX, actionData.objectName())
                self.list_view.addItem(listItem)
        
        self.list_view.model().sort(0, Qt.SortOrder.DescendingOrder)