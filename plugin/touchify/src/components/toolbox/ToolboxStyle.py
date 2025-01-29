from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from krita import *

class ToolboxStyle(QProxyStyle):


    def __init__(self, key: str, delay: int):
        super().__init__(key)
        self.menuDelay = delay

    def styleHint(self, element, option,
                  widget, returnData):

        if element == QStyle.SH_ToolButton_PopupDelay:
            return self.menuDelay

        return super().styleHint(element, option, widget, returnData);

