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




from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenuBar, QTabWidget, \
                            QAction, QMenu, QActionGroup
from krita import DockWidget
from .extensions.variables import *


from .DockerPage import DockerPage
from .DockerMenu import DockerMenu


# The main widget, containing the menu bar and tab bar.
class DockerWidget(QWidget):

    currentFolderChanged = pyqtSignal('QString')


    def __init__(self, parent: DockWidget):
        super().__init__(parent)
        self.docker: DockWidget = parent
        
        self.tab_menubar: DockerMenu | None = None
        self.tab_menu_items: list[tuple[QMenuBar | QMenu, list[QAction]]] = []
        self.last_tab: DockerPage | None = None

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.menubar = QMenuBar()
        

        # - File menu   
        fileMenu = self.menubar.addMenu("File")
        fileMenu.aboutToShow.connect(self.updateTabMenus)
        fileMenu.addAction("New Tab", self.addTab)

        fileMenu.addSeparator()

        closeMenu = fileMenu.addMenu("Close Tabs...")
        closeMenu.addAction("Close Current Tab", self.closeTab)
        closeMenu.addAction("Close All Tabs", self.closeAllTabs)
        closeMenu.addAction("Close Tabs to the Left", self.closeTabsLeft)
        closeMenu.addAction("Close Tabs to the Right", self.closeTabsRight)

        editMenu = self.menubar.addMenu("Edit")
        editMenu.aboutToShow.connect(self.updateTabMenus)

        renameTabAction = editMenu.addAction("Rename tab...")

        # - View menu
        viewMenu = self.menubar.addMenu("View")
        viewMenu.aboutToShow.connect(self.updateTabMenus)

        self.showTabBarAction = viewMenu.addAction("Show Tabs", self.toggleTabs)
        self.showTabBarAction.setCheckable(True)
        self.showTabBarAction.setChecked(True)

        self.showToolbarAction = viewMenu.addAction("Show Toolbar", self.toggleToolbar)
        self.showToolbarAction.setCheckable(True)
        self.showToolbarAction.setChecked(True)

        # - Mode menu
        modeMenu = self.menubar.addMenu("Mode")
        modeMenu.aboutToShow.connect(self.updateTabMenus)

        self.displayModeActionGroup = QActionGroup(self)

        previewAction = QAction("Preview", self.displayModeActionGroup)
        previewAction.setCheckable(True)
        previewAction.setChecked(True)
        previewAction.setEnabled(False)
        previewAction.setData("preview")

        gridAction = QAction("Grid", self.displayModeActionGroup)
        gridAction.setCheckable(True)
        gridAction.setEnabled(False)
        gridAction.setData("grid")

        referenceAction = QAction("Reference", self.displayModeActionGroup)
        referenceAction.setCheckable(True)
        referenceAction.setEnabled(False)
        referenceAction.setData("reference")

        self.displayModeActionGroup.triggered.connect(self.changeViewMode)
        modeMenu.addActions(self.displayModeActionGroup.actions())

        layout.setMenuBar(self.menubar)
        # Don't overwrite Krita's application menubar on macOS.
        self.menubar.setNativeMenuBar(False)

        # Tab bar
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setContentsMargins(0,0,0,0)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.onCloseRequestedTab)
        self.tabWidget.setMovable(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.currentChanged.connect(self.onTabChanged)
        layout.addWidget(self.tabWidget)

        self.tabWidget.setStyleSheet(f"""
            QTabBar::tab {{
                height: 25px;
            }}
        """)



    #region Widget Functions

    def currentTab(self) -> (DockerPage | None):
        return self.tabWidget.currentWidget()
    
    def tab(self, index: int) -> (DockerPage | None):
        return self.tabWidget.widget(index)

    # endregion

    #region Signal Functions

    def onTabChanged(self):
        if self.last_tab: self.last_tab.onTabDeactivated()
        self.last_tab = self.currentTab()
        if self.last_tab: self.last_tab.onTabActivated()
        self.updateMenuActions()

    def onCloseRequestedTab(self, idx):
        tab = self.tab(idx)
        if tab:
            self.tabWidget.removeTab(idx)
            tab.close()

    #endregion

    #region Menu Updates
    
    def updateTabMenus(self):
        if self.tab_menubar: self.tab_menubar.updateMenus()

    def updateMenuActions(self):
        def updateViewModeMenuActions():
            tab = self.currentTab()

            for action in self.displayModeActionGroup.actions():
                action.setEnabled(tab != None)

            if not tab: return
            current = tab.section()
            
            self.displayModeActionGroup.blockSignals(True)
            for action in self.displayModeActionGroup.actions():
                if action.data() == current: action.setChecked(True)
            self.displayModeActionGroup.blockSignals(False)

        updateViewModeMenuActions()

    def updateSectionMenus(self, tab_menubar: DockerMenu):

        def findMenuBarSection(title: str) -> QMenu | None:
            for menubar_action in self.menubar.actions():
                if menubar_action.menu() != None and menubar_action.text() == title:
                    return menubar_action.menu()
            return None

        for menu_item in self.tab_menu_items:
            source = menu_item[0]
            actions = menu_item[1]

            for action in actions:
                source.removeAction(action)

        self.tab_menubar = tab_menubar
        self.tab_menu_items = []

        if self.tab_menubar == None: return

        for menu_item in self.tab_menubar.menus():
            parent_menu = findMenuBarSection(menu_item.title())

            if parent_menu != None:
                result: tuple[QMenu, list[QAction]] = (parent_menu, [])
                for action in menu_item.actions():
                    result[0].addAction(action)
                    result[1].append(action)
                self.tab_menu_items.append(result)
            else:
                result: tuple[QMenuBar, list[QAction]] = (self.menubar, [])
                action = result[0].addMenu(menu_item)
                result[1].append(action)
                self.tab_menu_items.append(result)

        self.tab_menubar.updateMenus()           
                



    #endregion 

    #region Menu Functions

    def changeViewMode(self, action: QAction):
        data = str(action.data())
        tab = self.currentTab()
        current = tab.section()
        if not tab: return
        if current != data: tab.changeSection(data)

    def toggleToolbar(self):
        full_screen_state = self.showToolbarAction.isChecked()
        for i in range(0, self.tabWidget.count()):
            tab = self.tab(i)
            tab.setToolbarVisibile(full_screen_state)

    def toggleTabs(self):
        self.tabWidget.setTabBarAutoHide(not self.showTabBarAction.isChecked())

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


