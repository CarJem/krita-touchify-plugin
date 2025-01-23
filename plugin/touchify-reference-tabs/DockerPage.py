# Reference Tabs
# Copyright (C) 2022 Freya Lupen <penguinflyer2222@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import TYPE_CHECKING
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from krita import *
from .dataclasses.images import InsertablePin


from .sections.preview.PreviewSection import PreviewSection
from .sections.grid.GridSection import GridSection
from .sections.reference.ReferenceSection import ReferenceSection

from .sections.preview.PreviewMenu import PreviewMenu
from .sections.grid.GridMenu import GridMenu
from .sections.reference.ReferenceMenu import ReferenceMenu

from .dataclasses.session import SessionTab

from .DockerToolbar import DockerToolbar
from .DockerMenu import DockerMenu


PREVIEW_SECTION_ICON = Krita.instance().icon("folder-pictures")
GRID_SECTION_ICON = Krita.instance().icon("gridbrush")
REFERENCE_SECTION_ICON = Krita.instance().icon("zoom-fit")

if TYPE_CHECKING:
    from .DockerWidget import DockerWidget




class DockerPage(QWidget):
    def __init__(self, tab_widget: QTabWidget, view_widget: "DockerWidget"):
        super().__init__(tab_widget)
        self.setContentsMargins(0,0,0,0)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.TabMenus: DockerMenu = None
        self.TabWidget = tab_widget
        self.ParentWidget = view_widget

        self.__current_section = "preview"
        self.__previous_section = "preview"

        self.__Layout = QVBoxLayout(self)
        self.__Layout.setSpacing(0)
        self.setLayout(self.__Layout)

        self.ViewSet = QStackedWidget(self)
        self.ViewSet.setContentsMargins(0,0,0,0)
        self.__Layout.addWidget(self.ViewSet)

        self.ToolPanel = QStackedWidget(self)
        self.ToolPanel.setContentsMargins(0,0,0,0)

        self.PreviewSection = PreviewSection(self)
        self.PreviewMenu = PreviewMenu(self.PreviewSection, self)
        self.ViewSet.addWidget(self.PreviewSection)
        self.ToolPanel.addWidget(self.PreviewSection.tool_panel)

        self.GridSection = GridSection(self)
        self.GridMenu = GridMenu(self.GridSection, self)
        self.ViewSet.addWidget(self.GridSection)
        self.ToolPanel.addWidget(self.GridSection.tool_panel)

        self.ReferenceSection = ReferenceSection(self)
        self.ReferenceMenu = ReferenceMenu(self.ReferenceSection, self)
        self.ViewSet.addWidget(self.ReferenceSection)
        self.ToolPanel.addWidget(self.ReferenceSection.tool_panel)

        self.ViewSetButton = QPushButton(self)
        self.ViewSetButton.setIcon(PREVIEW_SECTION_ICON)
        self.ViewSetButton.clicked.connect(self.ViewSetButton.showMenu)
        self.ViewSetButtonMenu = QMenu(self.ViewSetButton)
        self.ViewSetButton.setMenu(self.ViewSetButtonMenu)

        self.ToolLayout = DockerToolbar(self)
        self.ToolLayout.setFixedHeight(25)
        self.ToolLayout.widgetLayout.setSpacing(4)
        self.ToolLayout.addWidget(self.ViewSetButton)
        self.ToolLayout.addWidget(self.ToolPanel, stretch=1)
        self.__Layout.addWidget(self.ToolLayout)
        
        __PreviewAction = self.ViewSetButtonMenu.addAction(PREVIEW_SECTION_ICON, "Preview")
        __PreviewAction.setIconVisibleInMenu(True)
        __PreviewAction.triggered.connect(lambda: self.changeSection("preview"))

        __GridAction = self.ViewSetButtonMenu.addAction(GRID_SECTION_ICON, "Grid")
        __GridAction.setIconVisibleInMenu(True)
        __GridAction.triggered.connect(lambda: self.changeSection("grid"))
        
        __ReferenceAction = self.ViewSetButtonMenu.addAction(REFERENCE_SECTION_ICON, "Reference")
        __ReferenceAction.setIconVisibleInMenu(True)
        __ReferenceAction.triggered.connect(lambda: self.changeSection("reference"))

        self.changeSection("preview")

    def Get_TabTitle(self):
        index = self.TabWidget.indexOf(self)
        if index != -1: return self.TabWidget.tabText(index)
        else: return ""

    def Set_TabTitle(self, title: str):
        index = self.TabWidget.indexOf(self)
        if index == -1: return

        self.TabWidget.setTabText(index, title)

    def Session_Load(self, session: SessionTab):
        self.Set_TabTitle(session.name)
        self.PreviewSection.Session_Load(session.preview)
        self.GridSection.Session_Load(session.grid)
        self.ReferenceSection.Session_Load(session.ref)

        if session.active_mode: self.changeSection(session.active_mode)

    def Session_Save(self):
        active_mode = self.__current_section
        preview = self.PreviewSection.Session_Save()
        grid = self.GridSection.Session_Save()
        ref = self.ReferenceSection.Session_Save()
        tab_name = self.Get_TabTitle()

        return SessionTab(
            name=tab_name,
            preview=preview,
            grid=grid,
            ref=ref,
            active_mode=active_mode
        )



    def section(self):
        return self.__current_section

    def setToolbarVisibile(self, boolean: bool):
        if boolean:
            self.ReferenceSection.setToolbarVisibile(True)
            self.ToolLayout.setVisible(True)
        else:
            self.ReferenceSection.setToolbarVisibile(False)
            self.ToolLayout.setVisible(False)


    def OpenPreviousPage(self):
        self.changeSection(self.__previous_section)

    def OpenReference(self):
        self.changeSection("reference")

    def OpenGrid(self, dirPath: str):
        self.changeSection("grid")
        self.GridSection.changePath(dirPath)

    def OpenPreview(self, imgPath: str=None, pixmap: QPixmap = None):
        if imgPath != None:
            self.changeSection("preview")
            self.PreviewSection.Action_OpenImage(imgPath)
        elif pixmap != None:
            self.changeSection("preview")
            self.PreviewSection.Action_OpenQPixmap(pixmap)

    def PinImage(self, pin: InsertablePin):
        self.ReferenceSection.OnEvent_PinImage(pin)

    def onTabActivated(self):
        self.ParentWidget.updateSectionMenus(self.TabMenus)

    def onTabDeactivated(self):
        self.ParentWidget.updateSectionMenus(None)

    def updateTabMenus(self):
        if self.TabMenus: self.TabMenus.updateMenus()
        
    def changeSection(self, section: str):
        def switchTo(icon: QIcon, source: GridSection | PreviewSection, menu: DockerMenu | None = None):
            self.__previous_section = self.__current_section
            self.__current_section = section
            self.TabMenus = menu
            self.ParentWidget.updateSectionMenus(self.TabMenus)
            self.ViewSet.setCurrentWidget(source)
            self.ToolPanel.setCurrentIndex(self.ViewSet.currentIndex())
            self.ViewSetButton.setIcon(icon)
            self.ParentWidget.updateMenuActions()

        match section:
            case "preview":
                switchTo(PREVIEW_SECTION_ICON, self.PreviewSection, self.PreviewMenu)
            case "grid":
                switchTo(GRID_SECTION_ICON, self.GridSection, self.GridMenu)
            case "reference":
                switchTo(REFERENCE_SECTION_ICON, self.ReferenceSection, self.ReferenceMenu)
                pass

        
        







