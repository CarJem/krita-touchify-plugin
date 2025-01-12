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
 
# Zoom percent constants
MAX_ZOOM = 800
MIN_ZOOM = 10
ZOOM_STEP = 10

useAngleSelector = True


from .sections.preview.PreviewSection import PreviewSection
from .sections.grid.GridSection import GridSection
from .sections.reference.ReferenceSection import ReferenceSection

from .sections.preview.PreviewMenu import PreviewMenu

from .DockerToolbar import DockerToolbar


PREVIEW_SECTION_ICON = Krita.instance().icon("folder-pictures")
GRID_SECTION_ICON = Krita.instance().icon("gridbrush")
REFERENCE_SECTION_ICON = Krita.instance().icon("zoom-fit")

if TYPE_CHECKING:
    from .DockerWidget import DockerWidget




class DockerPage(QWidget):
    def __init__(self, tab_widget: QTabWidget, view_widget: "DockerWidget"):
        super().__init__(tab_widget)

        self.tab_menus: list[QMenu] = []
        self.tab_widget = tab_widget
        self.view_widget = view_widget


        self.setContentsMargins(0,0,0,0)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.view = QStackedWidget(self)
        self.view.setContentsMargins(0,0,0,0)
        layout.addWidget(self.view)

        self.toolView = QStackedWidget(self)
        self.toolView.setContentsMargins(0,0,0,0)

        self.preview_section = PreviewSection(self)
        self.preview_menu = PreviewMenu(self.preview_section, self)
        self.view.addWidget(self.preview_section)
        self.toolView.addWidget(self.preview_section.tool_panel)

        self.grid_section = GridSection(self)
        self.view.addWidget(self.grid_section)
        self.toolView.addWidget(self.grid_section.tool_panel)

        self.reference_section = ReferenceSection(self)
        self.view.addWidget(self.reference_section)
        self.toolView.addWidget(self.reference_section.tool_panel)

        self.selection_box = QPushButton(self)
        self.selection_box.setIcon(PREVIEW_SECTION_ICON)
        self.selection_box_menu = QMenu(self.selection_box)
        self.selection_box.setMenu(self.selection_box_menu)
        self.selection_box.clicked.connect(self.selection_box.showMenu)

        self.toolLayout = DockerToolbar(self)
        self.toolLayout.setFixedHeight(25)
        self.toolLayout.widgetLayout.setSpacing(4)
        self.toolLayout.addWidget(self.selection_box)
        self.toolLayout.addWidget(self.toolView, stretch=1)
        layout.addWidget(self.toolLayout)
        
        previewAction = self.selection_box_menu.addAction(PREVIEW_SECTION_ICON, "Preview")
        previewAction.triggered.connect(lambda: self.changeSection("preview"))
        gridAction = self.selection_box_menu.addAction(GRID_SECTION_ICON, "Grid")
        gridAction.triggered.connect(lambda: self.changeSection("grid"))
        referenceAction = self.selection_box_menu.addAction(REFERENCE_SECTION_ICON, "Reference")
        referenceAction.triggered.connect(lambda: self.changeSection("reference"))

        self.changeSection("preview")

    def openPreview(self, imgPath: str):
        self.changeSection("preview")
        self.preview_section.openImage(imgPath)

    def openGrid(self, dirPath: str):
        self.changeSection("grid")
        self.grid_section.changePath(dirPath)

    def onTabActivated(self):
        self.view_widget.setTabSpecificMenus(self.tab_menus)

    def onTabDeactivated(self):
        self.view_widget.setTabSpecificMenus([])
        
    def changeSection(self, section: str):
        def switchTo(icon: QIcon, source: GridSection | PreviewSection, menu: QMenu | None = None):
            self.tab_menus = [ menu ] if menu else [ ]
            self.view_widget.setTabSpecificMenus(self.tab_menus)
            self.view.setCurrentWidget(source)
            self.toolView.setCurrentIndex(self.view.currentIndex())
            self.selection_box.setIcon(icon)

        match section:
            case "preview":
                switchTo(PREVIEW_SECTION_ICON, self.preview_section, self.preview_menu)
            case "grid":
                switchTo(GRID_SECTION_ICON, self.grid_section)
            case "reference":
                switchTo(REFERENCE_SECTION_ICON, self.reference_section)
                pass

        
        







