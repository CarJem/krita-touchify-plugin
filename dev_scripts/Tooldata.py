from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


from krita import *

def find_tool_options(tool_names: list[str]):
    qdock = next((w for w in Krita.instance().dockers() if w.objectName() == 'sharedtooldocker'), None)
    for option in tool_names:
        result = qdock.findChild(QWidget, option)
        if result: return result

    return None

def get_info(tool_names: list[str], widgets: list[list[any]], properties: list[str]):
    tool_options = find_tool_options(tool_names)
    if not tool_options: return {}

    results = {}
    tool_widgets = tool_options.findChildren(QWidget)

    __current_search = 0
    for item in tool_widgets:
        if len(widgets) - 1 < __current_search: continue

        meta_class = None
        meta_class_allowed = True
        
        if len(widgets[__current_search]) >= 2:
            meta_class = widgets[__current_search][1]
            if not meta_class.startswith("###"):
                meta_class_allowed = item.metaObject().className() == meta_class

        if isinstance(item, widgets[__current_search][0]) and meta_class_allowed:
            if isinstance(item, QComboBox) and meta_class == None:
                x: QComboBox = item
                results[properties[__current_search]] = x.currentIndex() 

            elif isinstance(item, QComboBox) and meta_class == "KisCompositeOpComboBox":
                xa: QComboBox = item
                results[properties[__current_search]] = xa.currentText() 

            elif isinstance(item, QSpinBox) and meta_class == "KisSliderSpinBox":
                yb: QSpinBox = item
                results[properties[__current_search]] = yb.value()

            elif isinstance(item, QDoubleSpinBox)  and meta_class == None:
                y: QDoubleSpinBox = item
                results[properties[__current_search]] = y.value() 

            elif isinstance(item, QDoubleSpinBox) and meta_class == "KisAngleSelectorSpinBox":
                ya: QDoubleSpinBox = item
                results[properties[__current_search]] = ya.value() 

            elif isinstance(item, QPushButton) and meta_class == "KisColorButton":
                ds: QPushButton = item
                results[properties[__current_search]] = "(unsupported)"

            elif isinstance(item, QCheckBox) and meta_class == None:
                z: QCheckBox = item
                results[properties[__current_search]] = z.isChecked() 
                
            elif isinstance(item, QToolButton) and meta_class == "KoGroupButton":
                a: QToolButton = item
                results[properties[__current_search]] = a.isChecked()

            elif isinstance(item, QToolButton) and meta_class == "###CheckState###":
                azz: QToolButton = item
                results[properties[__current_search]] = azz.isChecked()
            
            elif isinstance(item, QWidget) and meta_class == "KisColorLabelSelectorWidget":
                aa: QWidget = item
                aa_range = {}
                for idx, color_button in enumerate(aa.findChildren(QAbstractButton)):
                    aa_range[idx] = color_button.isChecked()
                results[properties[__current_search]] = aa_range

            __current_search += 1

    [print(f"{x}: {y}") for x, y in results.items()]

    return results

print("Selection Options:")
get_info(
    tool_names=[
        'KisToolSelectRectangularoption widget',
        'KisToolSelectOutlineoption widget',
        'KisToolSelectEllipticaloption widget',
        'KisToolSelectPolygonaloption widget',
        'KisToolSelectMagneticoption widget',
        'KisToolSelectPathoption widget',
    ],
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
    ],
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
)

print("Selection Options:")
get_info(
    tool_names=[
        'KisToolSelectRectangularoption widget',
        'KisToolSelectOutlineoption widget',
        'KisToolSelectEllipticaloption widget',
        'KisToolSelectPolygonaloption widget',
        'KisToolSelectMagneticoption widget',
        'KisToolSelectPathoption widget',
    ],
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
    ],
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
)

print("Brush Options:")
get_info(
    tool_names=[
        'KritaShape/KisToolBrushoption widget', 
        'KritaShape/KisToolMultiBrushoption widget'
    ],
    widgets=[
        [QComboBox],
        [QDoubleSpinBox],
        [QCheckBox],
        [QCheckBox],
        [QDoubleSpinBox],
        [QCheckBox],
        [QDoubleSpinBox],
        [QCheckBox],
        [QCheckBox],
    ],
    properties=[
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
)

print("Fill Options:")
get_info(
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
)