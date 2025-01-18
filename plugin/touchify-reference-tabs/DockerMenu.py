from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class DockerMenu(QMenu):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(title, parent)
        self.__menus: list[QMenu] = []

    def menus(self):
        return self.__menus
    
    def updateMenus(self):
        pass

    def mergeMenu(self, other_menu: "DockerMenu"):
        for menu in other_menu.menus():
            super().addMenu(menu)
            self.__menus.append(menu)

    def addMenu(self, title: str):
        result = super().addMenu(title)
        self.__menus.append(result)
        return result