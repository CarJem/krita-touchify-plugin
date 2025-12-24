from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints
from jemlib.alib_propertygrid.dialogs.PropertyGrid_SelectorDialog import PropertyGrid_SelectorDialog
from jemlib.managers.IconRepository import IconRepository

from touchify.src.alib_propertygrid.PropertyGridDialog import PropertyGridDialog
from touchify.src.config.triggers.Trigger import Trigger
from touchify_quick_actions_old.QuickActionsListItem import QuickActionsList, QuickActionsListItem
from touchify_quick_actions_old.QuickActionsSettings import QuickActionsSettingsLoader

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from touchify.src.PluginWindow import TouchifyWindow

class QuickActionsWidget(QWidget):    


    def __init__(self, parent: QWidget | None = None):
        super(QuickActionsWidget, self).__init__(parent)

        self.__toolbar_icon_size = QSize(20,20)
        self.__menu_icon_size = QSize(18,18)
        self.__touchifyInstance: "TouchifyWindow" = None

        self.__items: list[QuickActionsListItem] = []

        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(300)

        layout = QGridLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.loader = QuickActionsSettingsLoader(self)

        self.__editor: PropertyGridDialog = None
        

        self.__menuBar = QToolBar(self)
        self.__menuBar.setMaximumHeight(self.__menu_icon_size.height())
        self.__menuBar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        self.__menuBar.setContentsMargins(0,0,0,0)
        layout.addWidget(self.__menuBar, 0, 0)

        self.__listWidget = QuickActionsList(self)
        self.__listWidget.model().rowsMoved.connect(self.moveItems)
        self.__listWidget.sigContextMenuRequested.connect(self.onItemContextMenuRequested)
        layout.addWidget(self.__listWidget, 1, 0)
        
        self.__toolbar = QToolBar(self)
        self.__toolbar.setIconSize(self.__toolbar_icon_size)
        self.__toolbar.setStyleSheet("QToolBar { margin: 0px; padding: 0px; }" "QToolBar::item { margin: 0px; padding: 0px; }")
        layout.addWidget(self.__toolbar, 2, 0)

        self.__options_menu_button = QToolButton(self)
        self.__options_menu_button.setMaximumSize(self.__menu_icon_size)
        self.__options_menu_button.setContentsMargins(0,0,0,0)
        self.__options_menu_button.setPopupMode(QToolButton.InstantPopup)
        self.__options_menu_button.setStyleSheet("QToolButton::menu-indicator { image: none }")
        self.__options_menu_button.setAutoRaise(True)
        self.__options_menu_button.pressed.connect(self.onContextMenuRequested)
        self.__options_menu_button.setIcon(IconRepository.materialIcon("menu"))
        self.__menuBar.addWidget(self.__options_menu_button)

        self.__titleBar = QLabel(self)
        self.__titleBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__titleBar.setContentsMargins(0,0,0,0)
        self.__menuBar.addWidget(self.__createSpacer(self.__titleBar))

        qApp.paletteChanged.connect(self.onPaletteChanged)
        self.onPaletteChanged()

    def setup(self, instance: "TouchifyWindow"):
        self.__touchifyInstance = instance
        self.refresh()

    #region Signals

    def onPaletteChanged(self):
        palette = self.__titleBar.palette()
        palette.setBrush(QPalette.ColorRole.Window, qApp.palette().base())
        self.__titleBar.setPalette(palette)
        self.__titleBar.setBackgroundRole(QPalette.ColorRole.Window)
        self.__titleBar.setAutoFillBackground(True)

        self.__menuBar.setStyleSheet(f"""
            QToolBar {{ 
                margin: 0px; 
                padding: 0px; 
                background-color: palette(base);
            }}
            QToolBar::item {{ 
                margin: 0px; 
                padding: 0px; 
                background-color: palette(base);
            }}
        """)

    def onContextMenuRequested(self):
        contextMenu = QMenu(self)
        
        addAction = contextMenu.addAction("Add Actions... ")
        addAction.triggered.connect(self.showPicker)

        contextMenu.exec(QCursor.pos())

    def onItemContextMenuRequested(self, index: int):
        contextMenu = QMenu(self)

        settingsAction = contextMenu.addAction("Settings...")
        settingsAction.triggered.connect(lambda: self.editItem(index))
        
        removeAction = contextMenu.addAction("Delete")
        removeAction.triggered.connect(lambda: self.removeItem(index))

        contextMenu.exec(QCursor.pos())

    def onItemsMoved(self):
        pass

    #endregion

    #region Action Mgmt

    def showPicker(self):
        def accept():
            new_item = self.loader.createActionTrigger(dlg.selected_item)
            self.addItem(new_item)
        
        def reject():
            dlg.reject()

        dlg = PropertyGrid_SelectorDialog(None)
        dlg.header_buttons.buttons()[0].setText("Insert")
        dlg.header_buttons.buttons()[1].setText("Cancel")
        dlg.header_buttons.accepted.connect(accept)
        dlg.header_buttons.rejected.connect(reject)
        dlg.load_list(DataConstraints.StrMod.ActionSelection)
        dlg.exec()

    def moveItems(self, parent: QModelIndex, start_index: int, end_index: int, destination: QModelIndex, dest_row: int):
        print(f"moved: {start_index}:{end_index} || {dest_row}")

    def removeItem(self, index: int):
        self.__items.pop(index)
        item = self.__listWidget.takeItem(index)
        del item
        self.loader.actions().pop(index)
        self.loader.save()

    def editItem(self, index: int):
        list_item = self.__items[index]
        self.__editor = PropertyGridDialog.Setup(self.__editor, self.__touchifyInstance.api_window, list_item.getTrigger())
        if self.__editor.exec_():
            editorResults: Trigger = self.__editor.editableConfig
            self.__items[index].setTrigger(editorResults)
            self.loader.actions()[index] = editorResults
            self.loader.save()

    def addItem(self, trigger_data: Trigger):
        list_entry = QuickActionsListItem(parent=self.__listWidget, trigger_data=trigger_data, action_manager=self.__touchifyInstance.managers.mgr_actions)
        self.__items.append(list_entry)
        self.loader.actions().append(trigger_data)
        self.loader.save()
    
    def refresh(self):
        self.__listWidget.clear()
        self.__items.clear()
        self.__items = []

        self.loader.load()

        for trigger_data in self.loader.actions():
            list_entry = QuickActionsListItem(parent=self.__listWidget, trigger_data=trigger_data, action_manager=self.__touchifyInstance.managers.mgr_actions)
            self.__items.append(list_entry)


    #endregion

    #region Misc

    def __createSpacer(self, widget: QWidget = None):
        spacer = QWidget()
        spacer.setLayout(QHBoxLayout())
        spacer.layout().setSpacing(0)
        spacer.layout().setContentsMargins(0,0,0,0)

        if widget: spacer.layout().addWidget(widget, 1)
        else: spacer.layout().addStretch()

        return spacer
        

    #endregion



