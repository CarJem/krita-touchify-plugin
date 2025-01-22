import copy
import re
from typing import TYPE_CHECKING
from krita import *
from ...DockerToolbar import DockerToolbar
from .GridView import GridView
from ...extensions.variables import *
from ...extensions.native_actions import NativeActions
from ...dataclasses.images import InsertablePin
from ...extensions.filetypes import REFERENCE_FILETYPE_DATA
from ...extensions.commons import Commons
from ...dataclasses.session import SessionGrid


if TYPE_CHECKING:
    from ...DockerPage import DockerPage

# Zoom percent constants
MAX_ZOOM = 800
MIN_ZOOM = 80
ZOOM_STEP = 10



class GridSection(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.DockerPage: "DockerPage" = parent

        self.Variables()
        self.Components()
        self.Connections()
        
    def Canvas(self):
        return self.DockerPage.ParentWidget.docker.canvas()

    def Variables(self):
        self.folder_path = ""
        self.file_paths = []
        self.list_mode = "Folder"
        self.krita_sort = "Name"
        self.folder_sort = QDir.SortFlag.LocaleAware
        self.preview_index = 0
        self.max_items = 0
        self.update_slider = True
    
    def Components(self):
        self.central_layout = QtWidgets.QVBoxLayout(self)
        self.central_layout.setContentsMargins(0, 0, 0, 4)
        self.central_layout.setSpacing(0)
        self.central_layout.setObjectName("verticalLayout")

        self.grid_container = QWidget( self )
        self.grid_container.installEventFilter(self)
        self.grid_container.setContentsMargins(0,0,0,4)
        self.central_layout.addWidget(self.grid_container)

        self.grid_view = GridView(self.grid_container)
        self.grid_view.setContentsMargins(0,0,0,0)
        self.grid_view.Set_FileSearch(REFERENCE_FILETYPE_DATA["file_search"])

        self.filter_bar = QtWidgets.QLineEdit(self)
        self.filter_bar.setFixedHeight(25)
        self.filter_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.filter_bar.setContentsMargins(0,0,0,4)
        self.filter_bar.setObjectName("filterTextEdit")
        self.filter_bar.setPlaceholderText("Filter...")
        self.central_layout.addWidget(self.filter_bar)

        self.tool_panel = DockerToolbar(self, Qt.Orientation.Horizontal)
        self.tool_panel.setFixedHeight(25)
        self.central_layout.addWidget(self.tool_panel)

        self.zoom_scale = QSpinBox()
        self.zoom_scale.setRange(MIN_ZOOM, MAX_ZOOM)
        self.zoom_scale.setSingleStep(ZOOM_STEP)
        self.zoom_scale.setSuffix("px")
        self.zoom_scale.setValue(200)
        self.zoom_scale.setToolTip("Zoom")
        self.tool_panel.addWidget(self.zoom_scale)

        self.paginationLabel = QtWidgets.QLabel(self.tool_panel)
        self.paginationLabel.setObjectName("paginationLabel")
        self.paginationLabel.setText("0/0")
        self.tool_panel.addWidget(self.paginationLabel)

        self.paginationSlider = QtWidgets.QSlider(self.tool_panel)
        self.paginationSlider.setOrientation(QtCore.Qt.Horizontal)
        self.paginationSlider.setObjectName("paginationSlider")
        self.paginationSlider.setMinimum(0)
        self.tool_panel.addWidget(self.paginationSlider)

        self.previousButton = QtWidgets.QToolButton(self.tool_panel)
        self.previousButton.setFixedSize(QtCore.QSize(25,25))
        self.previousButton.setArrowType(QtCore.Qt.LeftArrow)
        self.previousButton.setText("...")

        self.previousButton.setObjectName("previousButton")
        self.tool_panel.addWidget(self.previousButton)

        self.nextButton = QtWidgets.QToolButton(self.tool_panel)
        self.nextButton.setFixedSize(QtCore.QSize(25,25))
        self.nextButton.setArrowType(QtCore.Qt.RightArrow)
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setText("...")
        self.tool_panel.addWidget(self.nextButton)        

    def Connections(self):
        qApp.paletteChanged.connect(self.OnEvent_ThemeChanged)
        self.OnEvent_ThemeChanged()
    
        self.nextButton.clicked.connect(lambda: self.OnEvent_SliderIncremented(1))
        self.previousButton.clicked.connect(lambda: self.OnEvent_SliderIncremented(-1))
        self.zoom_scale.valueChanged.connect(self.OnEvent_SizeChanged)
        self.filter_bar.textChanged.connect(self.OnEvent_FilterChanged)

        self.paginationSlider.valueChanged.connect(self.OnEvent_SliderValueChanged)
        self.paginationSlider.sliderReleased.connect(self.OnEvent_SliderReleased)
        self.paginationSlider.sliderPressed.connect(self.OnEvent_SliderPressed)

        self.grid_view.SIGNAL_INDEX.connect(self.OnEvent_IndexChanged)
        self.grid_view.SIGNAL_PREVIEW_REQUESTED.connect(self.OnEvent_PreviewRequested)
        self.grid_view.SIGNAL_PIN_IMAGE.connect(self.OnEvent_PinImage)

    def Session_Load(self, session: SessionGrid):
        match session.path_type:
            case "path":
                self.changePath(session.path)
        
        self.filter_bar.setText(session.filter)
                

    def Session_Save(self):
        return SessionGrid(
            filter=self.filter_bar.text(),
            path=self.folder_path,
            path_type="path"
        )

    #region Event Functions

    def eventFilter(self, a0: QObject, a1: QEvent):
        if a0 == self.grid_container and a1.type() == QEvent.Type.Resize:
            self.grid_view.Set_Size(self.grid_container.width(), self.grid_container.height() - 4)    
        return super().eventFilter(a0, a1)

    def leaveEvent(self, event):
        self.filter_bar.clearFocus()

    #endregion

    def OnEvent_PreviewRequested(self, path: str):
        self.DockerPage.OpenPreview(path)

    def OnEvent_SizeChanged(self):
        self.grid_view.Grid_Size(self.zoom_scale.value())
        self.updatePageLabel()

    def OnEvent_FilterChanged(self):
        self.reload()
        self.updatePageLabel()

    def OnEvent_SliderIncremented(self, increment):
        self.grid_view.Grid_Increment(increment)

    def OnEvent_SliderValueChanged(self, value: int):
        increment = value - self.grid_view.line_index
        self.grid_view.Grid_Increment(increment)

    def OnEvent_SliderPressed(self):
        self.update_slider = False

    def OnEvent_SliderReleased(self):
        self.update_slider = True
        self.updatePageSlider()


    def OnEvent_FileLocationRequested( self, image_path: str ):
        NativeActions.File_Location(image_path)

    def OnEvent_PinImage( self, pin: InsertablePin ):
        self.DockerPage.PinImage(pin)

    def OnEvent_ThemeChanged( self ):
        # Krita Theme
        theme_value = QApplication.palette().color( QPalette.Window ).value()
        if theme_value > 128:
            self.color_1 = QColor( "#191919" )
            self.color_2 = QColor( "#e5e5e5" )
        else:
            self.color_1 = QColor( "#e5e5e5" )
            self.color_2 = QColor( "#191919" )
        # Update
        self.grid_view.Set_Theme( self.color_1, self.color_2 )

    def OnEvent_IndexChanged(self, current_index: int):
        self.updatePageLabel(current_index)
        if self.update_slider: self.updatePageSlider(current_index)


    #endregion

    #region Action Functions

    def reload( self ):
        search = self.filter_bar.text().lower()

        try:
            # Time Watcher
            start = QtCore.QDateTime.currentDateTimeUtc()

            # Lists
            active_list = self.list_mode.upper()
            if self.list_mode == "Folder":
                active_location = os.path.basename( self.folder_path )
                qdir = QDir(self.folder_path)
                qdir.setSorting( self.folder_sort )
                qdir.setFilter( QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot )
                qdir.setNameFilters( REFERENCE_FILETYPE_DATA["file_normal"] )
                files = qdir.entryInfoList()
                count = len( files )
            else:
                active_list = None
                active_location = None
                files = []
                count = 0

            # Progress Bar
            #self.Progress_Value( 0 )
            #self.Progress_Max( count )

            # Keywords
            keywords = []
            remove = []
            elements = r'[0-9A-Za-z\\/|!"#$%&()=?@£§{[\]\}\'«»,;.:-_çºª¨´~^*-+]+'
            words = re.findall( elements, search )
            try:
                n = words.index( "not" )
                keywords = words[:n]
                remove = words[n+1:]
            except:
                keywords = words
            len_key = len( keywords )
            len_rem = len( remove )

            # Search Cycle
            path_new = []
            for i in range( 0, count ):
                # Progress Bar
                #self.Progress_Value( i + 1 )

                # Variables
                item = files[i]
                if self.list_mode in ( "Krita", "Reference" ):
                    fn = os.path.basename( item ).lower()
                    fp = os.path.abspath( item )
                else:
                    fn = item.fileName().lower()
                    fp = os.path.abspath( item.filePath() )
                # Logic
                if ( len_key == 0 and len_rem == 0 ):
                    path_new.append( fp )
                else:
                    # Variables
                    check_add = False
                    check_rem = False
                    # Add
                    for key in keywords:
                        if key in fn:
                            check_add = True
                            break
                    # Remove
                    for rem in remove:
                        if rem in fn:
                            check_rem = True
                            break
                    # Operation
                    if ( check_add == True and check_rem == False ):
                        path_new.append( fp )

            # Variables
            self.file_paths.clear()
            self.file_paths = copy.deepcopy( path_new )
            if len( path_new ) > 0:
                self.file_found = True
                self.max_items = len( path_new ) - 1
                self.paginationSlider.setMinimum(1)
                self.paginationSlider.setMaximum(self.max_items)
            else:
                self.file_found = False
                self.max_items = 0
                self.paginationSlider.setMinimum(0)
                self.paginationSlider.setMaximum(0)

            # Update List and Display
            self.grid_view.Display_Path(self.file_paths, self.paginationSlider.value())
            self.updatePageLabel()

            # Progress Bar
            #self.Progress_Value( 0 )
            #self.Progress_Max( 1 )

            # Time Watcher
            end = QtCore.QDateTime.currentDateTimeUtc()
            delta = start.msecsTo( end )
            time = QTime( 0,0 ).addMSecs( delta )
            Commons.Message_Log( "FILTER", f"{ time.toString( 'hh:mm:ss.zzz' ) } | { active_list } { active_location } | SEARCH { search }" )
        except Exception as e:
            print(e)
            self.max_items = 0
            self.paginationSlider.setMinimum(0)
            self.paginationSlider.setMaximum(0)

    def updatePageSlider(self, current_index: int = None):
        if current_index == None:
            current_index = self.grid_view.line_index
    
        self.paginationSlider.blockSignals(True)
        self.paginationSlider.valueChanged.disconnect(self.OnEvent_SliderValueChanged)
        self.paginationSlider.setSliderPosition(current_index)
        self.paginationSlider.valueChanged.connect(self.OnEvent_SliderValueChanged)
        self.paginationSlider.blockSignals(False)

    def updatePageLabel(self, current_index: int = None):
        if current_index == None:
            current_index = self.grid_view.line_index

        ipp = self.grid_view.gmx * self.grid_view.gmy

        actual_page = int(current_index / ipp)
        max_pages = int(self.max_items / ipp)

        if self.max_items == 0: 
            self.paginationLabel.setText(f"Page: 0/0")
        else: 
            self.paginationLabel.setText(f"Page: {str(actual_page+1)}/{max_pages+1}")

    def changePath(self, folderPath: str):
        self.folder_path = folderPath
        self.reload()

    
    #endregion