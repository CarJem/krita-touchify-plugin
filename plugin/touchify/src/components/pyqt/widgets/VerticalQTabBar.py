from PyQt5.QtWidgets import QApplication, QTabBar, QStylePainter, QStyleOptionTab, QStyle
from PyQt5 import QtCore

class VerticalQTabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        super(VerticalQTabBar, self).__init__(*args, **kwargs)
        self.setElideMode(QtCore.Qt.TextElideMode.ElideNone)

    def tabSizeHint(self, index):
        size_hint = super(VerticalQTabBar, self).tabSizeHint(index)
        size_hint.transpose()
        return size_hint

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            if QApplication.style().objectName() == "macos":
                option.shape = QTabBar.Shape.RoundedNorth
                option.position = QStyleOptionTab.TabPosition.Beginning
            else:
                option.shape = QTabBar.Shape.RoundedWest
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabShape, option)
            option.shape = QTabBar.Shape.RoundedNorth
            painter.drawControl(QStyle.ControlElement.CE_TabBarTabLabel, option)
            
                        
# inspired by https://github.com/mauriliogenovese/PySide6_VerticalQTabWidget
# from https://github.com/yjg30737/pyqt-vertical-tab-widget/issues/1#issuecomment-1826354818                         
# big thanks to @yjg30737 and @mauriliogenovese 