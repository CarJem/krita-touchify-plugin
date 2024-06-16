from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from krita import *


TITLEBAR_SIZE = 20

class PopupDialog_ToolboxTitlebar(QWidget):

    def __init__(self, parent: QDialog):
        super(PopupDialog_ToolboxTitlebar, self).__init__()
        self.parent: QDialog = parent
        print(self.parent.width())
        self.layout: QHBoxLayout = QHBoxLayout()
        self.layout.addStretch()
        self.layout.setContentsMargins(0,0,0,0)

        self.isCollapsed: bool = False
        self.lastSize: QSize = QSize()

        self.btn_collapse = QPushButton()
        self.btn_collapse.setIcon(Krita.instance().icon("groupOpened"))
        self.btn_collapse.clicked.connect(self.btn_toggle_clicked)
        self.btn_collapse.setFixedHeight(TITLEBAR_SIZE)
        self.btn_collapse.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.btn_collapse, 1)
        self.setLayout(self.layout)


    def btn_toggle_clicked(self):
        if not self.isCollapsed:
            self.btn_collapse.setIcon(Krita.instance().icon("groupClosed"))
            self.lastSize = self.parent.size()
            self.parent.collapse()
            self.parent.resize(self.lastSize.width(),0)
            self.isCollapsed = True
        else:
            self.parent.resize(self.parent.size().width(), self.lastSize.height())
            self.btn_collapse.setIcon(Krita.instance().icon("groupOpened"))
            self.parent.expand()
            self.lastSize = QSize()
            self.isCollapsed = False
