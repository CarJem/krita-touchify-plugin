from touchify.src.config.toolbox.ToolboxDataItem import *
from touchify.src.config.toolbox.ToolboxDataCategory import *
from jemlib.alib_datatypes.EnumStr import EnumStr
from jemlib.alib_vaporjem.extensions.file_extensions import FileExtensions
from jemlib.alib_datatypes.TypedList import TypedList
from jemlib.alib_vaporjem.extensions.json_extensions import JsonExtensions
from touchify.src.config.BackwardsCompatibility import BackwardsCompatibility
from jemlib.alib_propertygrid.data.DataConstraints import DataConstraints


   
class ToolboxData:

    class OrientationMode(EnumStr):
        Dynamic = "dynamic"
        Horizontal = "horizontal"
        Vertical = "vertical"

    class ThemeStyle(EnumStr):
        Default = "default"
        Touchify = "touchify"
        Krita = "krita"

    def __defaults__(self):
        self.preset_name: str = "New Toolbox Preset"

        self.column_count: int = 2
        self.icon_size: int = 16

        self.submenu_delay: int = 200
        self.background_opacity: int = 255
        self.button_opacity: int = 255

        self.theme: str = "default"

        self.orientation_mode: str = "dynamic"

        self.categories: TypedList[ToolboxDataCategory] = [] 

        self.json_version: int = 1





    def __init__(self, **args) -> None:
        self.__defaults__()
        args = BackwardsCompatibility.ToolboxData(args)
        JsonExtensions.dictToObject(self, args)
        self.categories = JsonExtensions.init_list(args, "categories", ToolboxDataCategory)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)
    
    def propertygrid_listload(self):
        self.categories = TypedList(self.categories, ToolboxDataCategory)

    def propertygrid_sorted(self):
        return [
            "preset_name",
            # Layout
            "column_count",
            "icon_size",
            # Others
            "submenu_delay",
            "background_opacity",
            "button_opacity",
            "orientation_mode",
            "theme"
            # Items
            "categories"
        ]

    def propertygrid_labels(self):
        labels = {}
        labels["preset_name"] = "Preset Name"
        labels["categories"] = "Categories"
        labels["submenu_delay"] = "Menu Delay"
        labels["column_count"] = "Column Count"
        labels["icon_size"] = "Icon Size"
        labels["theme"] = "Theme"
        labels["background_opacity"] = "Background Opacity"
        labels["orientation_mode"] = "Orientation Mode"
        labels["button_opacity"] = "Button Opacity"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["column_count"] = DataConstraints.range(min=1)
        restrictions["background_opacity"] = DataConstraints.range(min=0, max=255)
        restrictions["button_opacity"] = DataConstraints.range(min=0, max=255)
        restrictions["orientation_mode"] = DataConstraints.strEnumValues(self.OrientationMode)
        restrictions["theme"] = DataConstraints.strEnumValues(self.ThemeStyle)
        return restrictions
    
    def update(self, item: "ToolboxData"):
        self.background_opacity = item.background_opacity
        self.button_opacity = item.button_opacity
        self.categories = item.categories
        self.column_count = item.column_count
        self.icon_size = item.icon_size
        self.orientation_mode = item.orientation_mode
        self.preset_name = item.preset_name
        self.submenu_delay = item.submenu_delay
        self.theme = item.theme
    
    def loadDefaults(self):
        result = TypedList([], ToolboxDataCategory)

        vectorSection = ToolboxDataCategory()
        vectorSection.id = "Vector"

        vectorSection.addAction("InteractionTool")
        vectorSection.addAction("SvgTextTool")
        vectorSection.addAction("PathTool")
        vectorSection.addAction("KarbonCalligraphyTool")

        paintSection = ToolboxDataCategory()
        paintSection.id = "Paint"

        paintSection.addAction("KisToolPencil")
        paintSection.addAction("KritaShape/KisToolLine")
        paintSection.addAction("KritaShape/KisToolRectangle")
        paintSection.addAction("KritaShape/KisToolEllipse")
        paintSection.addAction("KisToolPolygon")
        paintSection.addAction("KisToolPolyline")
        paintSection.addAction("KisToolPath")
        paintSection.addAction("KritaShape/KisToolBrush")
        paintSection.addAction("KritaShape/KisToolDyna")
        paintSection.addAction("KritaShape/KisToolMultiBrush")

        transformSection = ToolboxDataCategory()
        transformSection.id = "Transform"

        transformSection.addAction("KisToolTransform")
        transformSection.addAction("KritaTransform/KisToolMove")
        transformSection.addAction("KisToolCrop")


        colorSection = ToolboxDataCategory()
        colorSection.id = "Color"

        colorSection.addAction("KritaFill/KisToolGradient")
        colorSection.addAction("KritaSelected/KisToolColorSampler")
        colorSection.addAction("KritaShape/KisToolLazyBrush")
        colorSection.addAction("KritaShape/KisToolSmartPatch")
        colorSection.addAction("KritaFill/KisToolFill")
        colorSection.addAction("KisToolEncloseAndFill")

        measureSection = ToolboxDataCategory()
        measureSection.id = "Measure"

        measureSection.addAction("KisAssistantTool")
        measureSection.addAction("KritaShape/KisToolMeasure")
        measureSection.addAction("ToolReferenceImages")

        selectSection = ToolboxDataCategory()
        selectSection.id = "Select"

        selectSection.addAction("KisToolSelectRectangular")
        selectSection.addAction("KisToolSelectElliptical")
        selectSection.addAction("KisToolSelectPolygonal")
        selectSection.addAction("KisToolSelectOutline") 
        selectSection.addAction("KisToolSelectContiguous")
        selectSection.addAction("KisToolSelectSimilar")
        selectSection.addAction("KisToolSelectPath")   
        selectSection.addAction("KisToolSelectMagnetic")

        navigationSection = ToolboxDataCategory()
        navigationSection.id = "Navigation"

        navigationSection.addAction("PanTool")
        navigationSection.addAction("ZoomTool")

        result.append(vectorSection)
        result.append(transformSection)
        result.append(paintSection)
        result.append(colorSection)
        result.append(measureSection)
        result.append(selectSection)
        result.append(navigationSection)

        return result


