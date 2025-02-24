import uuid
from krita import *
from touchify.src.datatypes.metaclass.EnumStr import EnumStr

from touchify.src.components.trigger_buttons.TouchifyActionButton import *
from touchify.src.components.trigger_buttons.TouchifyActionToolbar import TouchifyActionToolbar

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from touchify.src.config.toolshelf.ToolshelfDataSection import ToolshelfDataSection
from touchify.src.config.triggers.Trigger import Trigger
from touchify.src.config.triggers.TriggerGroup import TriggerGroup
from touchify.__env__ import *
from touchify.src.managers.shared.settings import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...managers.normal.action_manager import ActionManager

class TouchifyActionPanel(QWidget):

    class DataLoader(QObject):

        dataRecieved = pyqtSignal(list)

        def __init__(self, actions: list[TriggerGroup]):
            super().__init__()
            self.seperate_thread = QThread()
            self.moveToThread(self.seperate_thread)
            self.seperate_thread.setTerminationEnabled(True)
            self.actions = actions

            # Thread
            self.seperate_thread.started.connect(self.LoadData_Async)

        def start(self, priority: QThread.Priority = QThread.Priority.NormalPriority):
            self.seperate_thread.start(priority)

        def LoadData_Async(self):
            row_index = 0
            results = []
            
            for row in self.actions:
                row: TriggerGroup
                for entry in row.actions:
                    act: Trigger = entry
                    results.append((row_index, act))
                row_index += 1
            self.dataRecieved.emit(results)
            self.seperate_thread.quit()

    class DisplayType(EnumStr):
        Toolbar = "toolbar"
        ToolbarFlat = "toolbar_flat"
        Popup = "popup"

    actionTriggered = pyqtSignal()
    dataLoaded = pyqtSignal()

    @staticmethod
    def Titlebar(cfg: List[TriggerGroup], parent: QWidget=None, actions_manager: "ActionManager" = None):
        data = ToolshelfDataSection()
        data.action_section_contents = cfg
        return TouchifyActionPanel(data, parent, actions_manager)
    
        #type: str = "default"

        #opacity: float = 1.0

    def __init__(self, cfg: ToolshelfDataSection, parent: QWidget=None, actions_manager: "ActionManager" = None):
        super(TouchifyActionPanel, self).__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.title = "Unknown"

        self.cfg = cfg
        self.actions_manager = actions_manager

        match cfg.action_section_display_mode:
            case ToolshelfDataSection.ActionSectionDisplayMode.Flat:
                self.display_type = TouchifyActionPanel.DisplayType.ToolbarFlat
            case ToolshelfDataSection.ActionSectionDisplayMode.Detailed:
                self.display_type = TouchifyActionPanel.DisplayType.Popup
            case _:
                self.display_type = TouchifyActionPanel.DisplayType.Toolbar

        if cfg.ignore_scaling: scale = 1
        else: scale = TouchifySettings.instance().preferences().Interface_ToolshelfActionSectionScale

        icon_size = int(cfg.action_section_icon_size * scale)

        self.icon_width: int = icon_size
        self.icon_height: int = icon_size
        
        self.item_width: int = int(cfg.action_section_btn_width * scale)
        self.item_height: int = int(cfg.action_section_btn_height * scale)
        
        self.opacity: float = 1.0

        self._rows: dict[int, any] = {}
        self._buttons: dict[any, TouchifyActionButton] = {}
        
        self.hinted_size: QSize | None = None

        self.ourLayout = QVBoxLayout(self)
        self.setLayout(self.ourLayout)
        
        if self.display_type == "toolbar_flat":
            self.layout().setSpacing(0)
            self.layout().setContentsMargins(0, 0, 0, 0)
        else:
            self.layout().setSpacing(0)
            self.layout().setContentsMargins(0, 0, 0, 0)
        
        self.data_loader = TouchifyActionPanel.DataLoader(self.cfg.action_section_contents)
        self.data_loader.dataRecieved.connect(self.OnEvent_DataLoaded)

    def Data_Load(self):
        self.data_loader.start()

    def OnEvent_DataLoaded(self, triggers: list[tuple[int, Trigger]]):
        for act in triggers:
            btn = self.actions_manager.Create_Button(self, act[1])
            if btn:
                btn.triggerActivated.connect(self.onButtonClicked)
                self.stylizeButton(btn)
                self.appendButton(act[1], btn, act[0])
        
        actionInfo = self.cfg
        if actionInfo.ignore_scaling: scale = 1
        else: scale = TouchifySettings.instance().preferences().Interface_ToolshelfActionSectionScale
    
        size_x = int(actionInfo.size_x * scale)
        size_y = int(actionInfo.size_y * scale)
        min_size_x = int(actionInfo.min_size_x * scale)
        min_size_y = int(actionInfo.min_size_y * scale)
        max_size_x = int(actionInfo.max_size_x * scale)
        max_size_y = int(actionInfo.max_size_y * scale)
    
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        if actionInfo.hasDisplayName(): self.setTitle(actionInfo.display_name)
        else: self.setTitle(actionInfo.action_section_id)

        if actionInfo.action_section_alignment_x != ToolshelfDataSection.SectionAlignmentX.Nothing or actionInfo.action_section_alignment_y != ToolshelfDataSection.SectionAlignmentY.Nothing:
            align_x = actionInfo.action_section_alignment_x
            align_y = actionInfo.action_section_alignment_y

            alignment_x = Qt.AlignmentFlag.AlignLeft
            alignment_y = Qt.AlignmentFlag.AlignTop

            expand_x = QSizePolicy.Policy.Preferred
            expand_y = QSizePolicy.Policy.Preferred

            if align_y == ToolshelfDataSection.SectionAlignmentY.Top: alignment_y = Qt.AlignmentFlag.AlignTop
            elif align_y == ToolshelfDataSection.SectionAlignmentY.Center: alignment_y = Qt.AlignmentFlag.AlignVCenter
            elif align_y == ToolshelfDataSection.SectionAlignmentY.Bottom: alignment_y = Qt.AlignmentFlag.AlignBottom
            elif align_y == ToolshelfDataSection.SectionAlignmentY.Expanding: expand_y = QSizePolicy.Policy.Expanding

            if align_x == ToolshelfDataSection.SectionAlignmentX.Left: alignment_x = Qt.AlignmentFlag.AlignLeft
            elif align_x == ToolshelfDataSection.SectionAlignmentX.Center: alignment_x = Qt.AlignmentFlag.AlignHCenter
            elif align_x == ToolshelfDataSection.SectionAlignmentX.Right: alignment_x = Qt.AlignmentFlag.AlignRight
            elif align_x == ToolshelfDataSection.SectionAlignmentX.Expanding: expand_x = QSizePolicy.Policy.Expanding

            self.layout().setAlignment(alignment_x | alignment_y)
            if expand_x: self.setSizePolicy(expand_x, expand_y)

        if size_x != 0 or size_y != 0:
            if size_x != 0: self.setFixedWidth(size_x)
            if size_y != 0: self.setFixedHeight(size_y)
        else:
            if min_size_x != 0: self.setMinimumWidth(min_size_x)
            if min_size_y != 0: self.setMinimumHeight(min_size_y)
            if max_size_x != 0: self.setMaximumWidth(max_size_x)
            if max_size_y != 0: self.setMaximumHeight(max_size_y)

        self.dataLoaded.emit()


    def setTitle(self, text: str):
        self.title = text

    def setSizeHint(self, hint: QSize):
        self.hinted_size = hint

    def sizeHint(self):
        if self.hinted_size:
            return self.hinted_size
        else:
            return super().sizeHint()
        
    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        return hint
    
    def close(self):
        super().close()
     
    def appendRow(self, row: int):
        if self.display_type == "toolbar_flat":
            rowWid = TouchifyActionToolbar(self)
            rowWid.setObjectName("touchify_actionpanel_toolbar")
            rowWid.layout().setSpacing(0)
            rowWid.layout().setContentsMargins(0,0,0,0)        
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            rowWid.setStyleSheet(f"""TouchifyActionToolbar {{ padding: 1; margin: 1; spacing: 1; }}""")
            if self.icon_width > 0 and self.icon_height > 0:
                rowWid.setIconSize(QSize(self.icon_width, self.icon_height))
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)
        else:
            rowWid = QWidget(self)
            rowLay = QHBoxLayout(rowWid)
            rowWid.setLayout(rowLay)
            rowWid.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            rowLay.setSpacing(0)
            rowLay.setContentsMargins(0, 0, 0, 0)
            self._rows[row] = rowWid
            self.layout().addWidget(rowWid)
     
    def addWidgetToRow(self, row: int, btn: TouchifyActionButton):
        if row not in self._rows:
            self.appendRow(row)
        
        rowItem = self._rows[row]
        if isinstance(rowItem, TouchifyActionToolbar):
            tlb: TouchifyActionToolbar = rowItem
            tlb.addWidget(btn)
            tlb.layout().setContentsMargins(0, 0, 0, 0)        
        elif isinstance(rowItem, QWidget):
            tlb: QWidget = rowItem
            tlb.layout().addWidget(btn)
  
    def appendButton(self, data: Trigger, btn: TouchifyActionButton, row: int):
        def action_id():
            result = None
            while result in self._buttons or result == None:
                result = str(uuid.uuid4())
            return result
        
        id = action_id()
        self._buttons[id] = btn
                    
        self.addWidgetToRow(row, btn)
        
    def stylizeButton(self, btn: TouchifyActionButton):
        if self.icon_width > 0 and self.icon_height > 0:
            btn.setIconSize(QSize(self.icon_width, self.icon_height))

        if self.item_width > 0:
            btn.setFixedWidth(self.item_width)
            
        if self.item_height > 0:
            btn.setFixedHeight(self.item_height)
            
        if self.display_type == "popup":
            stylesheet = f"""
                QToolButton, QPushButton {{
                    border-radius: 0px; 
                    background-color: palette(window);
                    padding: 5px 5px;
                    border: 0px solid transparent; 
                    font-size: 12px;
                }}
                
                QToolButton:hover, QPushButton:hover {{
                    background-color: palette(highlight);
                }}
                                
                QToolButton:pressed, QToolButton:pressed {{
                    background-color: palette(alternate-base);
                }}
            """
            btn.setStyleSheet(stylesheet)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setText(btn.meta_text)
        elif self.display_type == "toolbar":
            btn.setStyleSheet(f"""QPushButton::menu-indicator {{ image: none; }} QToolButton::menu-indicator {{ image: none; }}""")
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        elif self.display_type == "toolbar_flat":
            btn.setContentsMargins(0,0,0,0)
            btn.setStyleSheet(f"""QPushButton::menu-indicator {{ image: none; }} QToolButton::menu-indicator {{ image: none; }}""")

    def onButtonClicked(self):
        self.actionTriggered.emit()

