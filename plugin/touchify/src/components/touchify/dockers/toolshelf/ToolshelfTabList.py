
from PyQt5.QtGui import QColor, QIcon, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import QSizePolicy, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize, Qt

from functools import partial
from krita import *

from .....resources import ResourceManager
from .....settings.TouchifyConfig import *
from .....cfg.toolshelf.CfgToolshelfPanel import CfgToolshelfPanel
from .....cfg.action.CfgTouchifyAction import CfgTouchifyAction
from .....cfg.action.CfgTouchifyActionCollection import CfgTouchifyActionCollection
from .....cfg.toolshelf.CfgToolshelf import CfgToolshelf
from .....cfg.toolshelf.CfgToolshelfHeaderOptions import CfgToolshelfHeaderOptions
from .ToolshelfTabItem import ToolshelfTabItem
from ...actions.TouchifyActionButton import TouchifyActionButton

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ToolshelfHeader import ToolshelfHeader

class ToolshelfTabList(QWidget):
    def __init__(self, parent: "ToolshelfHeader", orientation: Qt.Orientation):
        super(ToolshelfTabList, self).__init__(parent)

        self.parent_header: ToolshelfHeader = parent
        self.cfg = self.parent_header.cfg
        self.header_options = self.cfg.header_options
        self.actions_manager = self.parent_header.parent_toolshelf.parent_docker.actions_manager
        
        self.orientation = orientation
        self.tab_size = self.header_options.button_size
        
        self.ourLayout = QHBoxLayout(self) if self.orientation == Qt.Orientation.Vertical else QVBoxLayout(self)
        self.ourLayout.setSpacing(1)
        self.ourLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ourLayout)

        self._rows: dict[int, QWidget] = {}
        self._buttons: dict[any, ToolshelfTabItem] = {}
        self._actions: dict[any, TouchifyActionButton] = {}

        self.button_size_policy = QSizePolicy()
        if self.orientation == Qt.Orientation.Vertical:
            self.button_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
            if self.header_options.stack_alignment != CfgToolshelfHeaderOptions.StackAlignment.Default:
                self.button_size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
            else:
                self.button_size_policy.setVerticalPolicy(QSizePolicy.Policy.MinimumExpanding)
        else:
            if self.header_options.stack_alignment != CfgToolshelfHeaderOptions.StackAlignment.Default:
                self.button_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Minimum)
            else:
                self.button_size_policy.setHorizontalPolicy(QSizePolicy.Policy.MinimumExpanding)
            self.button_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)


        homeProps = CfgToolshelfPanel()
        homeProps.row = 0
        homeProps.id = "ROOT"
        homeProps.icon = "material:home"
        self.homeButton = self.createTab(homeProps, self.parent_header.openRootPage, "Home")

        panels = self.cfg.panels
        for properties in panels:
            properties: CfgToolshelfPanel
            self.createTab(properties, partial(self.parent_header.openPage, properties.id), properties.id)

        action_row = 0
        for action_list in self.header_options.stack_actions:
            action_list: CfgTouchifyActionCollection
            for action in action_list.actions:
                action: CfgTouchifyAction
                self.createAction(action, action_row)
            action_row += 1

        self.onPageChanged("ROOT")


    def createRow(self, row: int):
        isVertical = self.orientation == Qt.Orientation.Vertical

        rowWid = QWidget(self)
        rowWid.setObjectName("toolshelf-tablist-row")
        rowWid.setLayout(QVBoxLayout(self) if isVertical else QHBoxLayout(self))
        rowWid.layout().setSpacing(0)
        rowWid.layout().setContentsMargins(0, 0, 0, 0)
        rowWid.setSizePolicy(self.button_size_policy)



        match self.header_options.stack_alignment:
            case CfgToolshelfHeaderOptions.StackAlignment.Left:
                if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
                else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
            case CfgToolshelfHeaderOptions.StackAlignment.Center:
                if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignVCenter)
                else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignHCenter)
            case CfgToolshelfHeaderOptions.StackAlignment.Right:
                if isVertical: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignBottom)
                else: rowWid.layout().setAlignment(Qt.AlignmentFlag.AlignRight)

        self._rows[row] = rowWid
        self.ourLayout.addWidget(rowWid)
    
    def createTab(self, properties: CfgToolshelfPanel, onClick: any, toolTip: str):
        btn = ToolshelfTabItem()
        btn.setIcon(ResourceManager.iconLoader(properties.icon))
        if onClick: 
            btn.clicked.connect(onClick)

        btn.setToolTip(toolTip)
        btn.setContentsMargins(0,0,0,0)
        btn.setCheckable(True)
        self._buttons[properties.id] = btn

        if properties.row not in self._rows:
            self.createRow(properties.row)

        self._rows[properties.row].layout().addWidget(btn)

        if self.orientation == Qt.Orientation.Vertical:
            btn.setMinimumHeight(self.tab_size)
            btn.setFixedWidth(self.tab_size)
        else:
            btn.setFixedHeight(self.tab_size)
            btn.setMinimumWidth(self.tab_size)

        btn.setSizePolicy(self.button_size_policy)  
            
        return btn
    
    def createAction(self, properties: CfgTouchifyAction, action_row: int):
        btn = self.actions_manager.createButton(self, properties)
        btn.setContentsMargins(0,0,0,0)
        self._actions[properties.id] = btn

        if action_row not in self._rows:
            self.createRow(action_row)

        self._rows[action_row].layout().addWidget(btn)

        if self.orientation == Qt.Orientation.Vertical:
            btn.setMinimumHeight(self.tab_size)
            btn.setFixedWidth(self.tab_size)
        else:
            btn.setFixedHeight(self.tab_size)
            btn.setMinimumWidth(self.tab_size)

        btn.setSizePolicy(self.button_size_policy)  
    

    def applyButtonRules(self, btn: ToolshelfTabItem, btn_id: str, page_id: str):
        preview_type = self.header_options.stack_preview
        should_hide = False
        should_check = False


        match preview_type:
            case CfgToolshelfHeaderOptions.StackPreview.Default:
                if btn_id == "ROOT": should_hide = True
                else:
                    if page_id == "ROOT": should_hide = False
                    else: should_hide = True
            case CfgToolshelfHeaderOptions.StackPreview.Tabbed:
                if page_id == btn_id: should_check = True
                else: should_check = False
            case CfgToolshelfHeaderOptions.StackPreview.TabbedExclusive:
                if page_id == btn_id: should_hide = True
                else: should_hide = False

        if should_hide: btn.hide()
        else: btn.show()

        if should_check:
            btn.setChecked(True)
        else:
            btn.setChecked(False)
        

    def applyActionRules(self, btn: TouchifyActionButton, act_id: str, page_id: str):
        preview_type = self.header_options.stack_preview
        should_hide = False

        match preview_type:
            case CfgToolshelfHeaderOptions.StackPreview.Default:
                if page_id == "ROOT": should_hide = False
                else: should_hide = True
            case CfgToolshelfHeaderOptions.StackPreview.Tabbed:
                pass
            case CfgToolshelfHeaderOptions.StackPreview.TabbedExclusive:
                pass

        if should_hide: btn.hide()
        else: btn.show()
            
    def onPageChanged(self, page_id: str):


        for btn_id in self._buttons:
            btn = self._buttons[btn_id]
            self.applyButtonRules(btn, btn_id, page_id)

        self.applyButtonRules(self.homeButton, "ROOT", page_id)

        for act_id in self._actions:
            act = self._actions[act_id]
            self.applyActionRules(act, act_id, page_id)

            


        
        
            
            
            