


from ....cfg.CfgToolshelf import CfgToolshelfAction
from ....variables import *
from ....cfg.CfgToolshelf import CfgToolshelfAction
from krita import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QMargins
from ....config import *
from .ToolshelfButtonBar import ToolshelfButtonBar
from .... import stylesheet

class ToolshelfQuickActions(QWidget):
    def __init__(self, cfg: List[CfgToolshelfAction], parent: QWidget=None,):
        super(ToolshelfQuickActions, self).__init__(parent)

        self.cfg = cfg

        self.ourLayout = QVBoxLayout()
        self.ourLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.ourLayout)

        self.bar = ToolshelfButtonBar(self)
        self.initQuickActions()
        self.ourLayout.addWidget(self.bar)

    def initQuickActions(self):
        actions = self.cfg
        for entry in actions:
            act: CfgToolshelfAction = entry
            action = Krita.instance().action(act.id)
            if action:
                self.bar.addCfgButton(
                    act,
                    action.trigger,
                    action.toolTip(),
                    False #action.isCheckable()
                    )

                if action.isCheckable():
                    btn = self.bar.button(act.id)
                    btn.setChecked(action.isChecked())