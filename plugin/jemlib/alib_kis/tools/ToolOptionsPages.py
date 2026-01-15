from collections.abc import Callable
from typing import Generic, TypeVar
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


from jemlib.api_krita.wrappers.window import WindowAPI
from krita import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

T = TypeVar("T")
V = TypeVar("V")

class ToolOptionPage(QObject):

    optionsChanged = pyqtSignal()

    class Field(Generic[T, V]):

        valueChanged: pyqtBoundSignal

        def __init__(self, name: str, widget: V, setFn: Callable[[T], None], getFn: Callable[[], T]):
            self.__name = name
            self.__widget: QWidget = widget
            self.__getFn = getFn
            self.__setFn = setFn

        def widget(self) -> V:
            return self.__widget

        def isAlive(self) -> bool:
            try:
                self.__widget.objectName()
                return True
            except RuntimeError:
                return False

        def get(self) -> T:
            return self.__getFn()

        def set(self, val: T): 
            self.__setFn(val)

    def __init__(self, parent: QObject | None, tool_names: list[str], widgets: list[list[any]], properties: list[str], api: WindowAPI):
        super().__init__(parent)
        self.tool_names: list[str] = tool_names
        self.widgets: list[list[any]] = widgets
        self.properties: list[str] = properties
        self.window_api: WindowAPI = api
        self.__lastViewModel: dict[str, ToolOptionPage.Field] = None
    
    def close(self):
        pass

    def on_options_changed(self):
        self.optionsChanged.emit()

    def find_tool_options(self):
        if not self.window_api: return None

        qdock = next((w for w in self.window_api.dockers if w.objectName() == 'sharedtooldocker'), None)
        if not qdock: return None

        for option in self.tool_names:
            result = qdock.findChild(QWidget, option)
            if result: return result

        qdock = self.window_api.qwindow.findChild(QWidget, 'sharedtooldocker_touchify_borrowed')
        if not qdock: return None

        for option in self.tool_names:
            result = qdock.findChild(QWidget, option)
            if result: return result

        return None

    def get_view_model(self) -> dict[str, Field]:
        if not self.window_api: return None

        if self.__lastViewModel != None:
            for x in self.__lastViewModel.values():
                if not x.isAlive():
                    self.__lastViewModel = None
                    break
            if self.__lastViewModel != None:
                return self.__lastViewModel

        tool_options = self.find_tool_options()
        if not tool_options: return None

        results: dict[str, ToolOptionPage.Field] = {}
        tool_widgets = tool_options.findChildren(QWidget)

        __current_search = 0
        for w in tool_widgets:
            if len(self.widgets) - 1 < __current_search: continue

            meta_class = None
            meta_class_allowed = True


            current_property_name = self.properties[__current_search]
            
            if len(self.widgets[__current_search]) >= 2:
                meta_class = current_property_name[1]
                if not meta_class.startswith("###"):
                    meta_class_allowed = w.metaObject().className() == meta_class

            if isinstance(w, self.widgets[__current_search][0]) and meta_class_allowed:
                if isinstance(w, QComboBox) and meta_class == None:
                    combo_box: QComboBox = w
                    result = (ToolOptionPage.Field[int, QComboBox](current_property_name, combo_box, combo_box.setCurrentIndex, combo_box.currentIndex))
                    result.widget().currentIndexChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QComboBox) and meta_class == "KisCompositeOpComboBox":
                    combo_box: QComboBox = w
                    result = (ToolOptionPage.Field[str, QComboBox](current_property_name, combo_box, combo_box.setCurrentText, combo_box.currentText))
                    result.widget().currentTextChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QSpinBox) and meta_class == "KisSliderSpinBox":
                    spin_box: QSpinBox = w
                    result = (ToolOptionPage.Field[int, QSpinBox](current_property_name, spin_box, spin_box.setValue, spin_box.value))
                    result.widget().valueChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QDoubleSpinBox)  and meta_class == None:
                    double_spin_box: QDoubleSpinBox = w
                    result = (ToolOptionPage.Field[float, QDoubleSpinBox](current_property_name, double_spin_box, double_spin_box.setValue, double_spin_box.value))
                    result.widget().valueChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QDoubleSpinBox) and meta_class == "KisAngleSelectorSpinBox":
                    double_spin_box: QDoubleSpinBox = w
                    result = (ToolOptionPage.Field[float, QDoubleSpinBox](current_property_name, double_spin_box, double_spin_box.setValue, double_spin_box.value))
                    result.widget().valueChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QCheckBox) and meta_class == None:
                    check_box: QCheckBox = w
                    result = (ToolOptionPage.Field[bool, QCheckBox](current_property_name, check_box, check_box.setChecked, check_box.isChecked))
                    result.widget().stateChanged.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QToolButton) and meta_class == "KoGroupButton":
                    tool_button: QToolButton = w
                    result = (ToolOptionPage.Field[bool, QToolButton](current_property_name, tool_button, tool_button.setChecked, tool_button.isChecked))
                    result.widget().toggled.connect(self.on_options_changed)
                    results[current_property_name] = result
                elif isinstance(w, QToolButton) and meta_class == "###CheckState###":
                    tool_button: QToolButton = w
                    result = (ToolOptionPage.Field[bool, QToolButton](current_property_name, tool_button, tool_button.setChecked, tool_button.isChecked))
                    result.widget().toggled.connect(self.on_options_changed)
                    results[current_property_name] = result
                #elif isinstance(w, QPushButton) and meta_class == "KisColorButton":
                    #pass #unsupported: cpython limitation
                #elif isinstance(w, QWidget) and meta_class == "KisColorLabelSelectorWidget":
                    #aa: QWidget = w
                    #aa_range = {}
                    #for idx, color_button in enumerate(aa.findChildren(QAbstractButton)):
                    #    aa_range[idx] = color_button.isChecked()
                    #results[current_property_name] = aa_range

                __current_search += 1

        self.__lastViewModel = results
        return self.__lastViewModel

    def get_settings(self):
        if not self.window_api: return None
        view_model = self.get_view_model()
        if not view_model: return None
        
        return { k: v.get() for k, v in view_model.items() }

    def set_settings(self, properties: dict[str, any]):
        if not self.window_api: return 
        view_model = self.get_view_model()
        if not view_model: return

        self.blockSignals(True)
        for k, v in properties.items():
            if k in view_model: view_model[k].set(v)
        self.blockSignals(False)


class ToolOptionPages:
    class FreehandBrush(ToolOptionPage):
        def __init__(self, api: WindowAPI):
            tool_names = [ 'KritaShape/KisToolBrushoption widget' ]
            widgets = [
                [QComboBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QCheckBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QCheckBox],
            ]
            properties = [
                "LineSmoothingType",
                "LineSmoothingDistance",
                "LineSmoothingFinishStabilizedCurve",
                "LineSmoothingUseDelayDistance",
                "LineSmoothingDelayDistance",
                "LineSmoothingStabilizeSensors",
                "LineSmoothingTailAggressiveness",
                "LineSmoothingSmoothPressure",
                "LineSmoothingScalableDistance"
            ]
            super().__init__(api.qwindow, tool_names, widgets, properties, api)
    
    class MultiBrush(ToolOptionPage):
        def __init__(self, api: WindowAPI):
            tool_names = [ 'KritaShape/KisToolMultiBrushoption widget' ]
            widgets = [
                [QComboBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QCheckBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QDoubleSpinBox],
                [QCheckBox],
                [QCheckBox],
            ]
            properties = [
                "LineSmoothingType",
                "LineSmoothingDistance",
                "LineSmoothingFinishStabilizedCurve",
                "LineSmoothingUseDelayDistance",
                "LineSmoothingDelayDistance",
                "LineSmoothingStabilizeSensors",
                "LineSmoothingTailAggressiveness",
                "LineSmoothingSmoothPressure",
                "LineSmoothingScalableDistance"
            ]
            super().__init__(api.qwindow, tool_names, widgets, properties, api)

    class Selection(ToolOptionPage):
        def __init__(self, api: WindowAPI):
            tool_names=[
                'KisToolSelectRectangularoption widget',
                'KisToolSelectOutlineoption widget',
                'KisToolSelectEllipticaloption widget',
                'KisToolSelectPolygonaloption widget',
                'KisToolSelectMagneticoption widget',
                'KisToolSelectPathoption widget',
            ]
            widgets=[
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],

                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],

                [QCheckBox],
                [QSpinBox, "KisSliderSpinBox"],
                [QSpinBox, "KisSliderSpinBox"],
            ]
            properties=[
                "RectangleSelectionPixelMode",
                "RectangleSelectionVectorMode",

                "RectangleSelectionActionReplace",
                "RectangleSelectionActionIntersect",
                "RectangleSelectionActionAdd",
                "RectangleSelectionActionSubtract",
                "RectangleSelectionActionSymetricDiffrence",

                "RectangleSelectionAdjustmentsAntiAliasing",
                "RectangleSelectionAdjustmentsGrowSize",
                "RectangleSelectionAdjustmentsFeatherSize",
            ]
            super().__init__(api.qwindow, tool_names, widgets, properties, api)

    class Fill(ToolOptionPage):
        def __init__(self, api: WindowAPI):
            tool_names=[
                'KritaFill/KisToolFill'
            ],
            widgets=[
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QDoubleSpinBox],
                [QDoubleSpinBox, "KisAngleSelectorSpinBox"],
                [QCheckBox],
                [QSpinBox, "KisSliderSpinBox"],
                [QComboBox, 'KisCompositeOpComboBox'],
                [QWidget, 'KisColorLabelSelectorWidget'],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QPushButton, "KisColorButton"],
                [QSpinBox, "KisSliderSpinBox"],
                [QSpinBox, "KisSliderSpinBox"],
                [QCheckBox],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"],
                [QCheckBox],
                [QSpinBox, "KisSliderSpinBox"],
                [QToolButton, "###CheckState###"],
                [QSpinBox, "KisSliderSpinBox"],
                [QToolButton, "KoGroupButton"],
                [QToolButton, "KoGroupButton"]
            ],
            properties=[
                "FillActiveSelection",
                "FillContagiusRegions",
                "FillSimilarRegions",
                "FillSourcePatternScale",
                "FillSourcePatternRotation",
                "FillCustomBlendingEnabled",
                "FillCustomBlendingOpacity",
                "FillCustomBlendingMode",
                "FillReferenceLayerTags",
                "FillRefrenceActiveLayer",
                "FillRefrenceMergedLayer",
                "FillRefrenceTaggedLayers",
                "FillExtentColor",
                "FillExtentThreshold",
                "FillExtentSpread",
                "FillExtentSelectionAsBoundary",
                "FillExtentBySimilarColor",
                "FillExtentBySpecificColor",
                "FillAdjustmentsAntiAliasing",
                "FillAdjustmentsGrowSize",
                "FillAdjustmentsGrowStopAtEdge",
                "FillAdjustmentsFeatherSize",
                "FillDragModeAnyColor",
                "FillDragModeSimilarColors",
            ]
            super().__init__(api.qwindow, tool_names, widgets, properties, api)