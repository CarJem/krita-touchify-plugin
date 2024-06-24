


from .ToolshelfPageHost import ToolshelfPageHost
from ...cfg.CfgToolshelf import CfgToolboxAction
from ...variables import *
from ...cfg.CfgToolshelf import CfgToolboxAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ...config import *
from .ToolshelfButtonBar import ToolshelfButtonBar
from .ToolshelfDockerHost import ToolshelfDockerHost
from ... import stylesheet

class ToolshelfQuickActions(QWidget):
    _lastSharedToolOptionsState = False

    def __init__(self, cfg: List[CfgToolboxAction], actionHeight: int, parent: QStackedWidget=None,):
        super(ToolshelfQuickActions, self).__init__(parent)

        self.cfg = cfg

        self.ourLayout = QVBoxLayout()
        self.ourLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ourLayout)

        self.quickActions = ToolshelfButtonBar(actionHeight, self)
        self.initQuickActions()
        self.ourLayout.addWidget(self.quickActions)

    def updateStyleSheet(self):
        self.quickActions.setStyleSheet(stylesheet.nu_tool_options_style)

    def initQuickActions(self):
        actions = self.cfg
        for entry in actions:
            act: CfgToolboxAction = entry
            if act.isEnabled:
                action = Krita.instance().action(act.id)
                if action:
                    self.quickActions.addButton(
                        act,
                        action.trigger,
                        action.toolTip(),
                        action.isCheckable()
                        )

                    if action.isCheckable():
                        btn = self.quickActions.button(act.id)
                        btn.setChecked(action.isChecked())