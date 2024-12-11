from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget

from touchify.src.resources import ResourceManager

class PropertyLabel(QWidget):



    def __init__(self, parent: QWidget, variable_name: str, label_text: str, hint_text: str, is_nested: bool = False) -> None:
        super().__init__(parent)

        self.variable_name = variable_name
        self.label_text = label_text
        self.hint_text = hint_text

        self.setup(is_nested)
        
    def setup(self, is_nested: bool):  
        titleSection = QHBoxLayout(self)
        titleSection.setSpacing(0)
        titleSection.setContentsMargins(0,0,0,0)

        self.varLabel = QLabel(self)
        self.varLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.varLabel.setMargin(0)
        self.varLabel.setWordWrap(True)
        self.varLabel.setContentsMargins(0,0,0,0)
        self.varLabel.setText(self.label_text)

        if self.hint_text != "":
            self.hintLabel = QPushButton(self)
            self.hintLabel.setContentsMargins(0,0,0,0)
            self.hintLabel.setFlat(True)
            self.hintLabel.clicked.connect(self.showHint)
            self.hintLabel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.hintLabel.setIcon(ResourceManager.iconLoader("material:information-variant"))
            self.hintLabel.setToolTip(self.hint_text)
        else:
            self.hintLabel = None

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setContentsMargins(0,0,0,0)

        titleSection.addWidget(self.varLabel)
        titleSection.addWidget(self.hintLabel, 1, Qt.AlignmentFlag.AlignRight)


    def showHint(self):
        QToolTip.showText(self.hintLabel.mapToGlobal(QPoint(0,0)), self.hint_text)


