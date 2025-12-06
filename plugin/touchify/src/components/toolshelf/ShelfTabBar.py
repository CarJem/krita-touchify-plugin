from functools import partial
from PyQt5.QtWidgets import QPushButton, QSizePolicy
from krita import *
from PyQt5.QtWidgets import *


from touchify.src.config.toolshelf.ToolshelfState import ToolshelfState, ToolshelfSubState
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.src.components.trigger_buttons.TouchifyActionButton import TouchifyActionButton
import touchify.src.extensions.pyqt_extensions as PyQtExtensions
from touchify.src.config.toolshelf.ToolshelfDataOptions import ToolshelfDataOptions

from touchify.src.managers.shared.settings import TouchifySettings
from touchify.__env__ import *
from touchify.src.managers.shared.resources import ResourceManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ShelfWidget import ShelfWidget
    from .ShelfToolbar import ShelfToolbar


class ShelfTabBar(QWidget):

    class TabItem(QPushButton):
        def __init__(self, parent = None):
            super().__init__(parent)

            self.setFocusPolicy(Qt.NoFocus)
            self.highlightConnection = None
            self._resizing = False

        def setIcon(self, icon):
            if isinstance(icon, QIcon):
                super().setIcon(icon)
            elif isinstance(icon, QPixmap):
                super().setIcon(QIcon(icon))
            elif isinstance(icon, QImage):
                super().setIcon(QIcon(QPixmap.fromImage(icon)))
            else:
                raise TypeError(f"Unable to set icon of invalid type {type(icon)}")

        def setColor(self, color): # In case the Krita API opens up for a "color changed" signal, this could be useful...
            if isinstance(color, QColor):
                pxmap = QPixmap(self.iconSize())
                pxmap.fill(color)
                self.setIcon(pxmap)
            else:
                raise TypeError(f"Unable to set color of invalid type {type(color)}")

        def setCheckable(self, checkable):
            if checkable:
                self.highlightConnection = self.toggled.connect(self.highlight)
            else:
                if self.highlightConnection:
                    self.disconnect(self.highlightConnection)
                    self.highlightConnection = None
            return super().setCheckable(checkable)

        def highlight(self, toggle):
            p = self.window().palette()
            if toggle:
                p.setColor(QPalette.Button, p.color(QPalette.Highlight))
            self.setPalette(p)

    class LayoutHost(QWidget):
        def __init__(self, parent = None, orientation=Qt.Orientation.Horizontal):
            super().__init__(parent)
            self.setContentsMargins(0, 0, 0, 0)
            self.ourLayout = QHBoxLayout(self) if orientation == Qt.Orientation.Vertical else QVBoxLayout(self)
            self.ourLayout.setSpacing(1)
            self.ourLayout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.ourLayout)

        def dispose(self):
            PyQtExtensions.CommonHelpers.clearLayout(self.ourLayout)

    def __init__(self, parent_toolshelf: "ShelfWidget"):
        super(ShelfTabBar, self).__init__(parent_toolshelf)

        self.shelf: "ShelfWidget" = parent_toolshelf
        self.managers = self.shelf.managers

        self.orientation = Qt.Orientation.Horizontal
        self.tab_size = 32
        self.button_size = 32
        self.button_size_policy = QSizePolicy()
        self.stack_alignment = ToolshelfDataOptions.StackAlignment.Default
        self.stack_preview = ToolshelfDataOptions.StackPreview.Tabbed

        self.setLayout(QGridLayout(self))

        self.ourLayout = ShelfTabBar.LayoutHost(self, self.orientation)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.ourLayout)
        
        self._rows: dict[int, QWidget] = {}
        self._buttons: dict[str, ShelfTabBar.TabItem] = {}
        self._actions: list[TouchifyActionButton] = []
        self._homeButton: ShelfTabBar.TabItem | None = None


        qApp.paletteChanged.connect(self.updateStyleSheet)
        self.updateStyleSheet()

    def reload(self, state: ToolshelfState):



        self.button_size = int(state.options.button_size * TouchifySettings.instance().preferences().Interface_ToolshelfTabBarScale)
        self.tab_size = state.options.button_size
        self.stack_alignment = state.options.stack_alignment
        self.stack_preview = state.options.stack_preview
        match state.options.position:
            case "top":
                self.orientation = Qt.Orientation.Horizontal
            case "left":
                self.orientation = Qt.Orientation.Vertical
            case "right":
                self.orientation = Qt.Orientation.Vertical
            case _:
                self.orientation = Qt.Orientation.Horizontal

        self.ourLayout.dispose()
        self.ourLayout.close()
        self.ourLayout.deleteLater()

        self.ourLayout = ShelfTabBar.LayoutHost(self, self.orientation)
        self.layout().addWidget(self.ourLayout)

        self._rows: dict[int, QWidget] = {}
        self._buttons: dict[str, ShelfTabBar.TabItem] = {}
        self._actions: list[TouchifyActionButton] = []
        self._homeButton: ShelfTabBar.TabItem | None = None
        
        
        self.button_size_policy = QSizePolicy()
        not_default_alignment = self.stack_alignment != ToolshelfDataOptions.StackAlignment.Default
        if self.orientation == Qt.Orientation.Vertical:
            self.button_size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
            self.button_size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        else:
            self.button_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Minimum if not_default_alignment else QSizePolicy.Policy.MinimumExpanding)
            self.button_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)

        self._homeButton = self.createTab("material:home", "ROOT", 0, self.shelf.goToHomePage, "Home")

        for idx, properties in enumerate(state.pages):
            properties: ToolshelfSubState
            self.createTab("material:home", "Tab_" + str(idx), 0, partial(self.shelf.goToPage, idx),  properties.name)

        action_row = 0
        for action_list in state.options.stack_actions:
            action_list: TriggerGroup
            for action in action_list.actions:
                action: Trigger
                self.createAction(action, action_row)
            action_row += 1

        self.onPageChanged("ROOT")
        self.adjustSize()

    
    def addToRow(self, widget: QWidget, row: int):
        print("Adding item \"", str(widget), "\" to row: ", row)
        if row not in self._rows:
            print("Creating new row: ", row)
            isVertical = self.orientation == Qt.Orientation.Vertical
            rowWid = QWidget(self)
            rowWid.setObjectName("toolshelf-tablist-row")
            rowWid.setLayout(QVBoxLayout(rowWid) if isVertical else QHBoxLayout(rowWid))
            rowWid.layout().setSpacing(0)
            rowWid.layout().setContentsMargins(0, 0, 0, 0)
            rowWid.setSizePolicy(self.button_size_policy)

            match self.stack_alignment:
                case ToolshelfDataOptions.StackAlignment.Left:
                    if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
                    else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
                case ToolshelfDataOptions.StackAlignment.Center:
                    if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignVCenter)
                    else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)
                case ToolshelfDataOptions.StackAlignment.Right:
                    if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignBottom)
                    else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
            self._rows[row] = rowWid
            self.ourLayout.layout().addWidget(rowWid)
            rowWid.adjustSize()
            print("Created new row: ", row)
        self._rows[row].layout().addWidget(widget)
        print("Added item \"", str(widget), "\" to row: ", row)

    def createTab(self, icon: str, id: str, tabRow: int, onClick: any, toolTip: str):
        print("Creating tab:", id)
        btn = ShelfTabBar.TabItem(self)
        btn.setIcon(ResourceManager.iconLoader(icon))
        if onClick: 
            btn.clicked.connect(onClick)

        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(True)

        actual_id = id
        actual_id_num = 0
        while actual_id in self._buttons:
            actual_id = f"{id}{actual_id_num}"
            actual_id_num += 1

        self._buttons[actual_id] = btn

        self.addToRow(btn, tabRow)

        if self.orientation == Qt.Orientation.Vertical:
            btn.setMinimumHeight(self.tab_size)
            btn.setFixedWidth(self.tab_size)
        else:
            btn.setFixedHeight(self.tab_size)
            btn.setMinimumWidth(self.tab_size)

        btn.setSizePolicy(self.button_size_policy)  
        
        print("Created tab:", id)
        return btn
    
    def createAction(self, properties: Trigger, action_row: int):
        btn = self.managers.mgr_actions.Create_Button(self, properties)
        if btn:
            btn.setContentsMargins(0,0,0,0)
            self._actions.append(btn)

            self.addToRow(btn, action_row)

            if self.orientation == Qt.Orientation.Vertical:
                btn.setMinimumHeight(self.tab_size)
                btn.setFixedWidth(self.tab_size)
            else:
                btn.setFixedHeight(self.tab_size)
                btn.setMinimumWidth(self.tab_size)

            btn.setSizePolicy(self.button_size_policy)  
    
    def applyButtonRules(self, btn: "ShelfTabBar.TabItem", btn_id: str, page_id: str):
        preview_type = self.stack_preview
        should_hide = False
        should_check = False


        match preview_type:
            case ToolshelfDataOptions.StackPreview.Default:
                if btn_id == "ROOT": should_hide = True
                else:
                    if page_id == "ROOT": should_hide = False
                    else: should_hide = True
            case ToolshelfDataOptions.StackPreview.Tabbed:
                if page_id == btn_id: should_check = True
                else: should_check = False
            case ToolshelfDataOptions.StackPreview.TabbedExclusive:
                if page_id == btn_id: should_hide = True
                else: should_hide = False

        if should_hide: btn.hide()
        else: btn.show()

        if should_check:
            btn.setChecked(True)
        else:
            btn.setChecked(False)
            
    def updateStyleSheet(self):
        stylesheet = f"""
            QWidget#toolshelf-header {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QWidget#toolshelf-tablist-row {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton, QToolButton {{
                background-color: palette(alternate-base);
                border: none;
            }}

            QPushButton:hover, QToolButton:hover {{
                background-color: palette(highlight);
            }}

            QPushButton:checked, QToolButton:checked {{
                background-color: palette(highlight);
            }}
            
            QPushButton:pressed, QToolButton:pressed {{
                background-color: palette(alternate-base);
            }}

            QPushButton#back-widget {{
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border: none;
            }}

            QPushButton#pin-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QPushButton::menu-indicator, QToolButton::menu-indicator {{ 
                image: none; 
            }}

            QPushButton#menu-widget {{
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                border: none;
            }}

            QWidget#filler-widget {{
                background-color: palette(alternate-base);
                border: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
        """
        self.setStyleSheet(stylesheet)  

    def applyActionRules(self, btn: TouchifyActionButton, page_id: str):
        preview_type = self.stack_preview
        should_hide = False

        match preview_type:
            case ToolshelfDataOptions.StackPreview.Default:
                if page_id == "ROOT": should_hide = False
                else: should_hide = True
            case ToolshelfDataOptions.StackPreview.Tabbed:
                pass
            case ToolshelfDataOptions.StackPreview.TabbedExclusive:
                pass

        if should_hide: btn.hide()
        else: btn.show()
            
    def onPageChanged(self, page_id: str):
        for btn_id in self._buttons:
            btn = self._buttons[btn_id]
            self.applyButtonRules(btn, btn_id, page_id)

        if self._homeButton:
            self.applyButtonRules(self._homeButton, "ROOT", page_id)

        for act in self._actions:
            self.applyActionRules(act, page_id)


