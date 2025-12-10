from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from touchify.__env__ import TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT, TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT
from touchify.src.components.toolshelf.ShelfDockWidget import ShelfDockWidget
from touchify.src.components.toolshelf.ShelfFloatingDockWidget import ShelfFloatingDockWidget



class ShelfDockWidget1(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #1")
        self.PanelIndex = 1

class ShelfDockWidget2(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #2")
        self.PanelIndex = 2

class ShelfDockWidget3(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #3")
        self.PanelIndex = 3

class ShelfDockWidget4(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #4")
        self.PanelIndex = 4

class ShelfDockWidget5(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #5")
        self.PanelIndex = 5

class ShelfDockWidget6(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #6")
        self.PanelIndex = 6

class ShelfDockWidget7(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #7")
        self.PanelIndex = 7

class ShelfDockWidget8(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #8")
        self.PanelIndex = 8

class ShelfDockWidget9(ShelfDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.DOCKER_TITLE + " #9")
        self.PanelIndex = 9


ShelfDockWidgetsExt = [
    ShelfDockWidget1,
    ShelfDockWidget2,
    ShelfDockWidget3,
    ShelfDockWidget4,
    ShelfDockWidget5,
    ShelfDockWidget6,
    ShelfDockWidget7,
    ShelfDockWidget8,
    ShelfDockWidget9
]

class ShelfDockWidgetFlt1(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #1")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 1
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.TopLeft)

class ShelfDockWidgetFlt2(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #2")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 2
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.TopCenter)

class ShelfDockWidgetFlt3(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #3")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 3
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.TopRight)

class ShelfDockWidgetFlt4(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #4")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 4
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.MidLeft)

class ShelfDockWidgetFlt5(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #5")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 5
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.MidRight)

class ShelfDockWidgetFlt6(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #6")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 6
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.BottomLeft)

class ShelfDockWidgetFlt7(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #7")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 7
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.BottomCenter)

class ShelfDockWidgetFlt8(ShelfFloatingDockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ShelfDockWidgets.FLT_DOCKER_TITLE + " #8")
        self.PanelIndex = len(ShelfDockWidgetsExt) + 8
        self.setAlignment(ShelfFloatingDockWidget.WidgetAlignment.BottomRight)

ShelfFloatingDockWidgets = [
    ShelfDockWidgetFlt1,
    ShelfDockWidgetFlt2,
    ShelfDockWidgetFlt3,
    ShelfDockWidgetFlt4,
    ShelfDockWidgetFlt5,
    ShelfDockWidgetFlt6,
    ShelfDockWidgetFlt7,
    ShelfDockWidgetFlt8
]


class ShelfDockWidgets:

    DOCKER_TITLE="Touchify Core: Extra Toolshelf"
    FLT_DOCKER_TITLE="Touchify Core: Floating Toolshelf"

    @staticmethod
    def isExt(docker_id: str):
        for idx in range(0, len(ShelfDockWidgetsExt)):
            if docker_id.startswith(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT) and docker_id.endswith("_" + str(idx + 1)):
                return True
    
        for idx in range(0, len(ShelfFloatingDockWidgets)):
            if docker_id.startswith(TOUCHIFY_DOCKERID_TOOLSHELFDOCKER_EXT_FLT) and docker_id.endswith("_" + str(idx + 1)):
                return True
        return False