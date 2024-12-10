from touchify.src.cfg.toolbox.CfgToolboxItem import *
from touchify.src.cfg.toolbox.CfgToolboxCategory import *
from touchify.src.ext.FileExtensions import FileExtensions
from touchify.src.ext.types.TypedList import TypedList
from touchify.src.ext.JsonExtensions import JsonExtensions as Extensions
from touchify.src.cfg.CfgBackwardsCompat import CfgBackwardsCompat


   
class CfgToolbox:
    preset_name: str = "New Toolbox Preset"

    column_count: int = 2
    icon_size: int = 16

    submenu_delay: int = 200
    background_opacity: int = 255
    button_opacity: int = 255

    categories: TypedList[CfgToolboxCategory] = [] 


    json_version: int = 1





    def __init__(self, **args) -> None:
        args = CfgBackwardsCompat.CfgToolbox(args)
        Extensions.dictToObject(self, args)
        self.categories = Extensions.init_list(args, "categories", CfgToolboxCategory)

    def __str__(self):
        return self.preset_name.replace("\n", "\\n")

    def getFileName(self):
        return FileExtensions.fileStringify(self.preset_name)
    
    def forceLoad(self):
        self.categories = TypedList(self.categories, CfgToolboxCategory)

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
        labels["background_opacity"] = "Background Opacity"
        labels["button_opacity"] = "Button Opacity"
        return labels

    def propertygrid_restrictions(self):
        restrictions = {}
        restrictions["column_count"] = {"type": "range", "min": 1}
        restrictions["background_opacity"] = {"type": "range", "min": 0, "max": 255}
        restrictions["button_opacity"] = {"type": "range", "min": 0, "max": 255}
        return restrictions
    
    def loadDefaults(self):
        result = TypedList([], CfgToolboxCategory)

        vectorSection = CfgToolboxCategory()
        vectorSection.id = "Vector"

        vectorSection.addAction("InteractionTool")
        vectorSection.addAction("SvgTextTool")
        vectorSection.addAction("PathTool")
        vectorSection.addAction("KarbonCalligraphyTool")

        paintSection = CfgToolboxCategory()
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

        transformSection = CfgToolboxCategory()
        transformSection.id = "Transform"

        transformSection.addAction("KisToolTransform")
        transformSection.addAction("KritaTransform/KisToolMove")
        transformSection.addAction("KisToolCrop")


        colorSection = CfgToolboxCategory()
        colorSection.id = "Color"

        colorSection.addAction("KritaFill/KisToolGradient")
        colorSection.addAction("KritaSelected/KisToolColorSampler")
        colorSection.addAction("KritaShape/KisToolLazyBrush")
        colorSection.addAction("KritaShape/KisToolSmartPatch")
        colorSection.addAction("KritaFill/KisToolFill")
        colorSection.addAction("KisToolEncloseAndFill")

        measureSection = CfgToolboxCategory()
        measureSection.id = "Measure"

        measureSection.addAction("KisAssistantTool")
        measureSection.addAction("KritaShape/KisToolMeasure")
        measureSection.addAction("ToolReferenceImages")

        selectSection = CfgToolboxCategory()
        selectSection.id = "Select"

        selectSection.addAction("KisToolSelectRectangular")
        selectSection.addAction("KisToolSelectElliptical")
        selectSection.addAction("KisToolSelectPolygonal")
        selectSection.addAction("KisToolSelectOutline") 
        selectSection.addAction("KisToolSelectContiguous")
        selectSection.addAction("KisToolSelectSimilar")
        selectSection.addAction("KisToolSelectPath")   
        selectSection.addAction("KisToolSelectMagnetic")

        navigationSection = CfgToolboxCategory()
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


