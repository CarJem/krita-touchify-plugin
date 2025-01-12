# Photobash Images is a Krita plugin to get CC0 images based on a search,
# straight from the Krita Interface. Useful for textures and concept art!
# Copyright (C) 2020  Pedro Reis.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from typing import TYPE_CHECKING
from krita import *
from ...DockerToolbar import DockerToolbar
from .GridView import GridView
from .GridNativeActions import GridNativeActions
from ...classes.variables import *


if TYPE_CHECKING:
    from ...DockerPage import DockerPage

# Zoom percent constants
MAX_ZOOM = 800
MIN_ZOOM = 10
ZOOM_STEP = 10



class GridSection(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.section_parent: "DockerPage" = parent
        self.NativeFn: GridNativeActions = GridNativeActions(self)

        #region Interface
        
        self.central_layout = QtWidgets.QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 4)
        self.central_layout.setSpacing(0)
        self.central_layout.setObjectName("verticalLayout")



        self.grid_view = GridView(self)
        self.grid_view.pageChanged.connect(self.onPageChanged)
        self.grid_view.setContentsMargins(0,0,0,0)
        self.central_layout.addWidget(self.grid_view)

        self.filter_bar = QtWidgets.QLineEdit(self)
        self.filter_bar.setFixedHeight(25)
        self.filter_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.filter_bar.setContentsMargins(0,0,0,4)
        self.filter_bar.setObjectName("filterTextEdit")
        self.filter_bar.setPlaceholderText("Filter images by words...")
        self.filter_bar.textChanged.connect(self.onTextFilterChanged)
        self.central_layout.addWidget(self.filter_bar)

        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.setFixedHeight(25)
        self.central_layout.addWidget(self.tool_panel)

        self.zoom_scale = QSpinBox()
        self.zoom_scale.setRange(MIN_ZOOM, MAX_ZOOM)
        self.zoom_scale.setSingleStep(ZOOM_STEP)
        self.zoom_scale.setSuffix("%")
        self.zoom_scale.setValue(100)
        self.zoom_scale.setToolTip("Zoom")
        self.zoom_scale.valueChanged.connect(self.onZoomSizeChanged)
        self.tool_panel.addWidget(self.zoom_scale)

        self.paginationLabel = QtWidgets.QLabel(self.tool_panel)
        self.paginationLabel.setObjectName("paginationLabel")
        self.paginationLabel.setText("0/0")
        self.tool_panel.addWidget(self.paginationLabel)

        self.paginationSlider = QtWidgets.QSlider(self.tool_panel)
        self.paginationSlider.setOrientation(QtCore.Qt.Horizontal)
        self.paginationSlider.setObjectName("paginationSlider")
        self.paginationSlider.setMinimum(0)
        self.paginationSlider.valueChanged.connect(self.onSliderChanged)
        self.tool_panel.addWidget(self.paginationSlider)

        self.previousButton = QtWidgets.QToolButton(self.tool_panel)
        self.previousButton.setFixedSize(QtCore.QSize(25,25))
        self.previousButton.setArrowType(QtCore.Qt.LeftArrow)
        self.previousButton.setText("...")
        self.previousButton.clicked.connect(lambda: self.onSliderIncremented(-1))
        self.previousButton.setObjectName("previousButton")
        self.tool_panel.addWidget(self.previousButton)

        self.nextButton = QtWidgets.QToolButton(self.tool_panel)
        self.nextButton.setFixedSize(QtCore.QSize(25,25))
        self.nextButton.setArrowType(QtCore.Qt.RightArrow)
        self.nextButton.clicked.connect(lambda: self.onSliderIncremented(1))
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setText("...")
        self.tool_panel.addWidget(self.nextButton)        
        #endregion

        self.grid_view.initalize()



    #region Event Functions

    def resizeEvent(self, a0):
        return super().resizeEvent(a0)

    def leaveEvent(self, event):
        self.filter_bar.clearFocus()

    #endregion



    #region Signal Functions

    def onZoomSizeChanged(self):
        self.grid_view.setZoom(self.zoom_scale.value())

    def onTextFilterChanged(self):
        self.grid_view.setFilter(self.filter_bar.text())

    def onSliderIncremented(self, increment):
        self.grid_view.navigateFromIncrement(increment)

    def onSliderChanged(self, value):
        self.grid_view.navigateToIndex(value)

    def onPageChanged(self, maxNumPage: int, currPage: int):
        if maxNumPage == 0: self.paginationLabel.setText(f"Page: 0/0")
        else: self.paginationLabel.setText(f"Page: {str(currPage + 1)}/{str(maxNumPage)}")
        self.paginationSlider.setRange(0, maxNumPage - 1)
        self.paginationSlider.setSliderPosition(currPage)

    #endregion

    #region Action Functions

    def openPreview(self, path):
        self.section_parent.openPreview(path)

    def pinToFavourites(self, path):
        self.grid_view.Action_PinToFavourites(path)

    def unpinFromFavourites(self, path):
        self.grid_view.Action_UnpinFromFavourites(path)

    def changePath(self, folderPath: str):
        self.grid_view.setDirectoryPath(folderPath)

    
    #endregion