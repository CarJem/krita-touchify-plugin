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




import os
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenuBar, QTabWidget, \
                            QAction, QActionGroup, QFileDialog, QMenu
from krita import DockWidget
from .classes.variables import *
from .classes.settings import Settings
from .classes.common import generateFiletypeFilter

from .DockerPage import DockerPage


# The main widget, containing the menu bar and tab bar.
class DockerWidget(QWidget):

    currentFolderChanged = pyqtSignal('QString')


    def __init__(self, parent: DockWidget):
        super().__init__(parent)
        self.docker: DockWidget = parent
        
        self.tab_menu_items: list[QAction] = []
        self.last_tab: DockerPage | None = None

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.menubar = QMenuBar()

        # - File menu
        fileMenu = self.menubar.addMenu("File")
        fileMenu.addAction("New Tab", self.addTab)


        self.tabActionsGroup = QActionGroup(self)

        self.openImageAction = QAction("Open Image...", self.tabActionsGroup)
        self.openImageAction.triggered.connect(self.openImage)
        self.openImageAction.setEnabled(False)

        self.openFolderAction = QAction("Open Folder...", self.tabActionsGroup)
        self.openFolderAction.triggered.connect(self.openFolder)
        self.openFolderAction.setEnabled(False)

        fileMenu.addActions(self.tabActionsGroup.actions())
        fileMenu.addSeparator()

        closeMenu = fileMenu.addMenu("Close Tabs...")
        closeMenu.addAction("Close Current Tab", self.closeTab)
        closeMenu.addAction("Close All Tabs", self.closeAllTabs)
        closeMenu.addAction("Close Tabs to the Left", self.closeTabsLeft)
        closeMenu.addAction("Close Tabs to the Right", self.closeTabsRight)

        layout.setMenuBar(self.menubar)
        # Don't overwrite Krita's application menubar on macOS.
        self.menubar.setNativeMenuBar(False)

        # Tab bar
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.onCloseRequestedTab)
        self.tabWidget.setMovable(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.currentChanged.connect(self.onTabChanged)
        layout.addWidget(self.tabWidget)

        self.filter = generateFiletypeFilter()



    #region Widget Functions

    def currentTab(self) -> (DockerPage | None):
        return self.tabWidget.currentWidget()
    
    def tab(self, index: int) -> (DockerPage | None):
        return self.tabWidget.widget(index)

    def setTabSpecificMenus(self, menu_items: list[QMenu]):
        for menu_item in self.tab_menu_items:
            self.menubar.removeAction(menu_item)

        self.tab_menu_items = []

        for menu_item in menu_items:
            action = self.menubar.addMenu(menu_item)
            self.tab_menu_items.append(action)

    # endregion

    #region Signal Functions

    def onTabChanged(self):
        if self.last_tab: self.last_tab.onTabDeactivated()

        if self.currentTab() != None: [i.setEnabled(True) for i in self.tabActionsGroup.actions()]
        else: [i.setEnabled(False) for i in self.tabActionsGroup.actions()]
        self.last_tab = self.currentTab()

        if self.last_tab: self.last_tab.onTabActivated()

    def onCloseRequestedTab(self, idx):
        tab = self.tab(idx)
        if tab:
            self.tabWidget.removeTab(idx)
            tab.close()

    #endregion

    #region Event Functions

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        filePaths = event.mimeData().urls()
        # for now, always open in new tab
        for path in filePaths:
            # toLocalFile removes "file:///" on Windows
            # and "file://" on other OSes
            self.openImage(path.toLocalFile())

    #endregion

    #region Menu Functions

    def openImage(self, filePath=False):
        if not filePath:
            filePath, _filter = QFileDialog.getOpenFileName(self, "Open an image", filter=self.filter, directory=Settings.getFileDialogState())
            if not filePath: return
            Settings.setFileDialogState(os.path.dirname(filePath))

        tabIdx = self.tabWidget.currentIndex()
        tab = self.tab(tabIdx)
        tab.openPreview(filePath)
    
    def openFolder(self, folderPath=False):
        if not folderPath:
            folderPath = QFileDialog.getExistingDirectory(self, "Open a folder", Settings.getFileDialogState(), QFileDialog.Option.ShowDirsOnly)
            if not folderPath: return
            Settings.setFileDialogState(os.path.dirname(folderPath))
        
        tabIdx = self.tabWidget.currentIndex()
        tab = self.tab(tabIdx)
        tab.openGrid(folderPath)

    def addTab(self):
        tab = DockerPage(self.tabWidget, self)
        index = self.tabWidget.addTab(tab, "")
        self.tabWidget.setTabText(index, f"#{index}")
        self.tabWidget.setCurrentIndex(index)

    def closeTab(self):
        idx = self.tabWidget.currentIndex()
        self.onCloseRequestedTab(idx)

    def closeAllTabs(self):
       while True:
            idx = self.tabWidget.currentIndex()
            if idx == -1:
                return
            self.onCloseRequestedTab(idx)

    def closeTabsLeft(self):
       while True:
            idxLeft = self.tabWidget.currentIndex() - 1
            if not self.tab(idxLeft):
                return
            self.onCloseRequestedTab(idxLeft)

    def closeTabsRight(self):
       while True:
            idxRight = self.tabWidget.currentIndex() + 1
            if not self.tab(idxRight):
                return
            self.onCloseRequestedTab(idxRight)
    
    #endregion


